"""Harbor agent shim.

Harbor's BaseAgent is `async` and returns None -- an agent communicates by what
it leaves in /logs, which is exactly the artifact contract HANDOFF wants.

The Harbor and mini-swe-agent imports are deliberately lazy: the rest of this
package, and every test in the repo, runs without either installed.
"""

from harness.episode_runner import run_episode

AGENT_NAME = "handoff-mini"
AGENT_VERSION = "0.1.0"
LOGS = "/logs"


def build_mini_agent(model, environment, step_limit=0):
    """Construct mini-swe-agent configured with the HANDOFF report contract.

    Verified against mini-swe-agent 2.4.6: DefaultAgent takes AgentConfig fields
    as keyword arguments, not a config object. `cost_limit=0.0` disables mini's
    dollar cap (its guard is `0 < cost_limit <= cost`), which is what we want --
    budgets here are token-denominated, and a dollar cap would buy a cheap model
    more work than an expensive one at nominally equal budget.
    """
    from minisweagent.agents.default import DefaultAgent

    from harness.templates import INSTANCE_TEMPLATE, SYSTEM_TEMPLATE

    return DefaultAgent(
        model,
        environment,
        system_template=SYSTEM_TEMPLATE,
        instance_template=INSTANCE_TEMPLATE,
        step_limit=step_limit,
        cost_limit=0.0,
    )


class HandoffMiniAgent:  # pragma: no cover - needs a live Harbor install
    """Adapter matching Harbor's BaseAgent surface.

    Unverified against a running Harbor: this environment has no install, and
    harborframework.com is blocked by the egress proxy. The signatures follow
    Harbor's documented BaseAgent (`name`, `version`, async `setup`, async
    `run`); treat the wiring as the part to check first on a real run.
    """

    def __init__(self, model, spec, counter):
        self._model = model
        self._spec = spec
        self._counter = counter
        self._agent = None

    @staticmethod
    def name():
        return AGENT_NAME

    def version(self):
        return AGENT_VERSION

    async def setup(self, environment):
        self._agent = build_mini_agent(self._model, environment)

    async def run(self, instruction, environment, context):
        if self._agent is None:
            await self.setup(environment)
        # mini's run() initialises the history from the templates and loops to
        # exit; `task` and the extra kwargs become Jinja vars for
        # instance_template. Never append the instruction by hand -- run() would
        # reset messages and discard it.
        budget = self._spec["budget"]["max_tokens"]
        run_episode(
            self._agent,
            self._spec,
            self._counter,
            logs_dir=LOGS,
            start=lambda: self._agent.run(task=instruction, budget_tokens=budget),
        )
