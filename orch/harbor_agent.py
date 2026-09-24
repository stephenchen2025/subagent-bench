"""Harbor agent for the orchestrator track's reference harness.

    harbor run -p datasets/orch-v0.2 \\
        -a orch.harbor_agent:OrchMiniAgent \\
        -m anthropic/claude-haiku-4-5-20251001 --ak mode=delegate

`mode` is one of solo, solo-xl, delegate, oracle-split (ORCHESTRATOR.md 4). The
per-agent limits default to the values every task records in its task.toml
metadata and can be overridden with --ak.

The lead and its workers all drive the same container through one synchronous
bridge over Harbor's async `exec` (harness/harbor_agent.py explains why the
bridge is needed). Workers run on their own threads; each command is scheduled
back onto Harbor's event loop, which is safe to do from several threads.

telemetry.json and trajectories.json are written to the trial's agent logs dir,
where `tools/orch_collect.py` finds them next to the verifier's reward.json.
"""

import asyncio
import functools
import hashlib
import json
import os
import tomllib
from pathlib import Path

from harness.harbor_agent import HarborEnvBridge
from orch.harness import MODES, Limits, run_orchestrated

AGENT_NAME = "subagent-bench-orch"
AGENT_VERSION = "0.1.0"


@functools.cache
def build_agent_class():
    """Harbor needs Python >= 3.12; import it only when the class is wanted."""
    from harbor.agents.base import BaseAgent
    from harbor.agents.options import AgentOptions
    from pydantic import Field

    defaults = Limits()

    class OrchOptions(AgentOptions):
        mode: str = Field(default="delegate", description=f"one of {', '.join(MODES)}")
        worker_model: str | None = Field(default=None, description="defaults to the lead's model")
        context_tokens: int = defaults.context_tokens
        step_limit: int = defaults.step_limit
        observation_chars: int = defaults.observation_chars
        max_concurrent_subagents: int = defaults.max_concurrent_subagents
        max_total_subagents: int = defaults.max_total_subagents
        command_timeout_sec: int = 120

    class OrchMiniAgent(BaseAgent):
        """mini-swe-agent lead with an intercepted `subagent` command."""

        options_model = OrchOptions

        def __init__(self, logs_dir, model_name=None, **kwargs):
            self._model_factory = kwargs.pop("model_factory", None)
            super().__init__(logs_dir, model_name=model_name, **kwargs)

        @staticmethod
        def name():
            return AGENT_NAME

        def version(self):
            return AGENT_VERSION

        async def setup(self, environment):
            return None

        def _new_model(self, name):
            if self._model_factory is not None:
                return self._model_factory()
            from minisweagent.models import get_model

            return get_model(name)

        async def run(self, instruction, environment, context):
            options = self.options
            if options.mode not in MODES:
                raise ValueError(f"mode must be one of {MODES}, got {options.mode!r}")
            limits = Limits(
                context_tokens=int(options.context_tokens),
                step_limit=int(options.step_limit),
                observation_chars=int(options.observation_chars),
                max_concurrent_subagents=int(options.max_concurrent_subagents),
                max_total_subagents=int(options.max_total_subagents),
            )
            bridge = HarborEnvBridge(
                environment, asyncio.get_running_loop(),
                timeout_sec=int(options.command_timeout_sec),
            )
            worker_name = options.worker_model or self.model_name
            result = await asyncio.to_thread(
                run_orchestrated,
                instruction,
                bridge,
                self._new_model(self.model_name),
                lambda: self._new_model(worker_name),
                options.mode,
                limits,
                self.logs_dir,
            )
            tel = result.telemetry
            agents = [tel["lead"], *tel["workers"]]
            context.n_input_tokens = sum(a["input_tokens"] for a in agents) or None
            context.n_output_tokens = sum(a["output_tokens"] for a in agents) or None
            context.cost_usd = sum(a["cost_usd"] for a in agents) or None
            context.metadata = {
                "orch_mode": options.mode,
                "orch_lead_exit": tel["lead"]["exit_status"],
                "orch_subagents": len(tel["workers"]),
                "orch_tokens_exact": tel["tokens_exact"],
            }

    return OrchMiniAgent


@functools.cache
def build_rehearsal_class():
    """The reference harness driven by scripted policies instead of a model.

    For checking the harness inside real Harbor and Docker with no API key. The
    policies are perfect readers and need the ground truth, which is never in
    the image, so this agent (which runs on the host) regenerates the task:
    it finds the emitted task whose instruction.md matches, under
    ORCH_REHEARSAL_TASKS, and rebuilds it from its (family, size, seed).
    """
    from pydantic import Field

    from orch import policies
    from orch.families import FAMILIES

    base = build_agent_class()

    class RehearsalOptions(base.options_model):
        system: str = Field(default="judicious", description=f"one of {sorted(policies.LEADS)}")

    class OrchRehearsalAgent(base):
        options_model = RehearsalOptions

        @staticmethod
        def name():
            return AGENT_NAME + "-rehearsal"

        async def run(self, instruction, environment, context):
            task = await _find_task(instruction, environment)
            mode, lead, worker_factory = policies.build(self.options.system, task)
            self.options.mode = mode
            self._lead = lead
            self._model_factory = worker_factory
            await super().run(instruction, environment, context)

        def _new_model(self, name):
            lead, self._lead = getattr(self, "_lead", None), None
            return lead if lead is not None else self._model_factory()

    async def _find_task(instruction, environment):
        """The task this trial is running, identified from what the agent can see.

        Instructions alone are not unique: every W task of one size has the
        same instruction whatever its seed. When several tasks match, the
        workspace's file listing and contents settle it.
        """
        root = Path(os.environ["ORCH_REHEARSAL_TASKS"])
        candidates = []
        for toml_path in sorted(root.glob("*/task.toml")):
            if (toml_path.parent / "instruction.md").read_text() == instruction:
                meta = tomllib.loads(toml_path.read_text())["metadata"]
                candidates.append(FAMILIES[meta["family"]].generate(meta["size"], meta["seed"]))
        if len(candidates) > 1:
            listing = await environment.exec(
                "find . -type f ! -name answer.json | sed 's#^./##' | sort | xargs -r md5sum",
                cwd="/workspace",
            )
            seen = set((getattr(listing, "stdout", "") or "").split())
            candidates = [t for t in candidates if all(
                hashlib.md5(text.encode()).hexdigest() in seen for text in t.files.values())]
        # Seeds that happen to produce the same task are interchangeable.
        distinct = {json.dumps([t.files, t.truth], sort_keys=True): t for t in candidates}
        candidates = list(distinct.values())
        if len(candidates) != 1:
            raise LookupError(f"{len(candidates)} emitted tasks match this trial")
        return candidates[0]

    return OrchRehearsalAgent


def __getattr__(name):
    # `harbor run -a orch.harbor_agent:OrchMiniAgent` resolves lazily.
    if name == "OrchMiniAgent":
        return build_agent_class()
    if name == "OrchRehearsalAgent":
        return build_rehearsal_class()
    raise AttributeError(name)
