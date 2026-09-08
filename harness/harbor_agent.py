"""Harbor adapter for the HANDOFF subagent.

Verified against harbor 0.22.0. Two things about Harbor's real contract shape
this file, and neither is visible from its docs:

1. `BaseEnvironment.exec` is **async**, while mini-swe-agent's `env.execute` is
   **synchronous**. mini's loop cannot be driven from inside a coroutine, so the
   agent runs on a worker thread and the bridge hands each command back to the
   event loop with `run_coroutine_threadsafe`.
2. Harbor has a first-class `resume()` hook and a `resume` capability. Our F10
   handback does not need it -- the pushback is scripted, so it fits inside one
   `run()` -- but implementing `resume()` too costs almost nothing and lets a
   trial drive the second turn natively if it wants to.

Harbor is imported lazily: it needs Python >= 3.12, and the rest of this repo
does not need it at all.
"""

import asyncio
import json
from pathlib import Path

from harness.agent import AGENT_NAME, AGENT_VERSION, build_mini_agent
from harness.budget import EstimatingCounter
from harness.episode_runner import run_episode

DEFAULT_CWD = "/workspace"
DEFAULT_TIMEOUT_SEC = 120


class HarborEnvBridge:
    """Synchronous facade over Harbor's async `environment.exec`.

    mini executes one command per step and blocks on the result. Harbor's
    environment is async. Rather than nest event loops, the mini loop runs on a
    worker thread and each command is scheduled back onto the running loop.
    """

    def __init__(self, environment, loop, cwd=DEFAULT_CWD,
                 timeout_sec=DEFAULT_TIMEOUT_SEC):
        self._environment = environment
        self._loop = loop
        self._cwd = cwd
        self._timeout_sec = timeout_sec
        self.commands = []

    def execute(self, action, **kwargs):
        self.commands.append(action)
        future = asyncio.run_coroutine_threadsafe(
            self._environment.exec(
                action, cwd=self._cwd, timeout_sec=self._timeout_sec
            ),
            self._loop,
        )
        result = future.result(timeout=self._timeout_sec + 30)
        stdout = getattr(result, "stdout", None) or ""
        stderr = getattr(result, "stderr", None) or ""
        return {
            "output": (stdout + stderr).strip(),
            "returncode": getattr(result, "return_code", 0),
        }

    def get_template_vars(self):
        return {"cwd": self._cwd}

    def serialize(self):
        return {"type": "harbor-bridge", "cwd": self._cwd}


def load_spec(spec_path):
    """Task spec, when one was supplied. Absent means a task with no handback."""
    if not spec_path:
        return None
    path = Path(spec_path)
    return json.loads(path.read_text()) if path.exists() else None


def populate_context(context, episode):
    """Report usage back to Harbor in the fields it defines."""
    context.n_input_tokens = episode.usage.input_tokens or None
    context.n_output_tokens = episode.usage.output_tokens or None
    context.metadata = {
        "handoff_task_id": episode.task_id,
        "handoff_family": episode.family,
        "handoff_report_present": bool(episode.report.strip()),
        "handoff_tool_calls": episode.usage.tool_calls,
        "handoff_tokens_exact": getattr(episode, "tokens_exact", True),
    }
    return context


def build_agent_class():
    """Define the Harbor agent class. Lazy: importing harbor needs Python 3.12+."""
    from typing import Annotated

    from harbor.agents.base import BaseAgent
    from harbor.agents.capabilities import AgentCapabilities
    from harbor.agents.options import AgentOptions, Env

    class HandoffOptions(AgentOptions):
        spec_path: Annotated[str | None, Env("HANDOFF_SPEC_PATH")] = None

    class HandoffMiniAgent(BaseAgent):
        """mini-swe-agent under Harbor, emitting the HANDOFF artifact triple."""

        capabilities = AgentCapabilities(resume=True)
        options_model = HandoffOptions

        def __init__(self, logs_dir, model_name=None, **kwargs):
            self._model_factory = kwargs.pop("model_factory", None)
            self._counter = kwargs.pop("token_counter", None) or EstimatingCounter()
            super().__init__(logs_dir, model_name=model_name, **kwargs)
            self._mini = None
            self._bridge = None

        @staticmethod
        def name():
            return AGENT_NAME

        def version(self):
            return AGENT_VERSION

        def _spec(self):
            path = getattr(self.options, "spec_path", None) if self.options else None
            return load_spec(path) or {
                "id": "unknown",
                "family": "unknown",
                "budget": {"max_tokens": 100_000},
            }

        def _make_model(self):
            if self._model_factory is not None:
                return self._model_factory()
            from minisweagent.models import get_model

            return get_model(self.model_name)

        async def setup(self, environment):
            self._bridge = HarborEnvBridge(
                environment, asyncio.get_running_loop()
            )
            self._mini = build_mini_agent(self._make_model(), self._bridge)

        async def _drive(self, instruction, environment, context, resuming):
            if self._mini is None:
                await self.setup(environment)
            spec = self._spec()
            budget = spec["budget"]["max_tokens"]
            mini = self._mini

            def start():
                return mini.run(task=instruction, budget_tokens=budget)

            # mini's loop is synchronous and blocking; the bridge schedules each
            # command back onto this loop, so it must keep running.
            episode, _ = await asyncio.to_thread(
                run_episode,
                mini,
                spec,
                self._counter,
                self.logs_dir,
                200,
                None if resuming else start,
            )
            populate_context(context, episode)

        async def run(self, instruction, environment, context):
            await self._drive(instruction, environment, context, resuming=False)

        async def resume(self, instruction, environment, context):
            await self._drive(instruction, environment, context, resuming=True)

    return HandoffMiniAgent
