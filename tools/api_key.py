"""Resolve the Anthropic API key, accepting an alternate variable name.

Some hosted environments reserve ANTHROPIC_API_KEY for their own use and will
not pass it through to the project. HANDOFF_ANTHROPIC_API_KEY is accepted in
its place and copied into ANTHROPIC_API_KEY, so the anthropic SDK (the frozen
consumer) and litellm (mini-swe-agent) both find it with no further plumbing.
"""

import os

ALT_NAME = "HANDOFF_ANTHROPIC_API_KEY"

MISSING = (
    f"Neither ANTHROPIC_API_KEY nor {ALT_NAME} is set.\n"
    "Set one in this project's environment config (not in a shell here, and\n"
    "never in a chat transcript); it is injected at container start, so a\n"
    f"new session will have it. Use {ALT_NAME} if the environment refuses\n"
    "ANTHROPIC_API_KEY."
)


def resolve_api_key():
    """Return True if a key is available, promoting ALT_NAME if it is the only one."""
    if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get(ALT_NAME):
        os.environ["ANTHROPIC_API_KEY"] = os.environ[ALT_NAME]
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
