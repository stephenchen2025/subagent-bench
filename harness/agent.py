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


def build_mini_agent(model, environment, budget_tokens):  # pragma: no cover
    """Construct mini-swe-agent configured with the HANDOFF report contract."""
    from minisweagent.agents.default import AgentConfig, DefaultAgent

    from harness.templates import INSTANCE_TEMPLATE, SYSTEM_TEMPLATE

    config = AgentConfig(
        system_template=SYSTEM_TEMPLATE,
        instance_template=INSTANCE_TEMPLATE,
        step_limit=0,
        cost_limit=0,  # budgets are token-denominated here, never dollars
    )
    return DefaultAgent(model, environment, config=config)


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
        self._agent = build_mini_agent(
            self._model, environment, self._spec["budget"]["max_tokens"]
        )

    async def run(self, instruction, environment, context):
        if self._agent is None:
            await self.setup(environment)
        self._agent.messages.append({"role": "user", "content": instruction})
        run_episode(self._agent, self._spec, self._counter, logs_dir=LOGS)
