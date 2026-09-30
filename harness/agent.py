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


NO_ACTION_NUDGE = (
    "Your reply had no tool call and no report. Use the bash tool to run a "
    "command, or, if you are done, reply without a tool call and end with your "
    "report between {open} and {close}."
)


def _response_text(format_error):
    """The assistant text mini parsed and threw away when it raised FormatError.

    mini's tool-calling model persists the raw response on the error message's
    `extra` -- either a model_dump dict or, if dumping failed, a repr string.
    """
    if not format_error.messages:
        return ""
    response = (format_error.messages[0].get("extra") or {}).get("response")
    if not isinstance(response, dict):
        return ""
    try:
        return response["choices"][0]["message"].get("content") or ""
    except (KeyError, IndexError, TypeError, AttributeError):
        return ""


_AGENT_CLASS = None


def _handoff_agent_class():
    """DefaultAgent, with a final report accepted as the way to finish.

    mini 2.4.6's default (tool-calling) model treats any reply without a tool
    call as a FormatError: the text is discarded and the model is told "Every
    response MUST include at least one tool call". The HANDOFF contract is the
    opposite -- the deliverable IS a text reply -- so a reply carrying a
    delimited report is recorded as an assistant turn and ends the episode with
    Submitted. A reply with neither a tool call nor a report still counts as a
    format error, with a nudge that names both ways forward.
    """
    global _AGENT_CLASS
    if _AGENT_CLASS is not None:
        return _AGENT_CLASS

    from minisweagent.agents.default import DefaultAgent
    from minisweagent.exceptions import FormatError, Submitted

    from harness.templates import REPORT_CLOSE, REPORT_OPEN, extract_report

    class HandoffDefaultAgent(DefaultAgent):
        def query(self):
            try:
                return super().query()
            except FormatError as exc:
                text = _response_text(exc)
                report = extract_report(text)
                if not report:
                    if exc.messages and "No tool calls found" in str(exc.messages[0].get("content", "")):
                        exc.messages[0]["content"] = NO_ACTION_NUDGE.format(
                            open=REPORT_OPEN, close=REPORT_CLOSE
                        )
                    raise
                # run() only charges a FormatError's cost; this is no longer one.
                self.cost += exc.messages[0].get("extra", {}).get("cost", 0.0)
                self.add_messages({"role": "assistant", "content": text})
                raise Submitted(
                    {"role": "exit", "content": report,
                     "extra": {"exit_status": "Submitted", "submission": report}}
                ) from None

    _AGENT_CLASS = HandoffDefaultAgent
    return _AGENT_CLASS


def build_mini_agent(model, environment, step_limit=0):
    """Construct mini-swe-agent configured with the HANDOFF report contract.

    Verified against mini-swe-agent 2.4.6: DefaultAgent takes AgentConfig fields
    as keyword arguments, not a config object. `cost_limit=0.0` disables mini's
    dollar cap (its guard is `0 < cost_limit <= cost`), which is what we want --
    budgets here are token-denominated, and a dollar cap would buy a cheap model
    more work than an expensive one at nominally equal budget.
    """
    from harness.templates import INSTANCE_TEMPLATE, SYSTEM_TEMPLATE

    return _handoff_agent_class()(
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
