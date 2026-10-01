"""Keep credentials out of the agent's shell and out of saved episodes.

The Milestone 1 runner drives mini-swe-agent's LocalEnvironment, which runs the
agent's commands on the host with the host's environment. An agent that runs
`env` then writes every API key into its trajectory -- this happened in the
Gemma pilot, and GitHub's push protection caught the key before it left.

Two layers:

- `shell_env_overrides()` blanks every secret-looking variable for the agent's
  shell. The agent process itself keeps its key (it calls the model API); the
  commands it runs never need one.
- `redact()` scrubs a record before it is written: the value of every
  secret-looking variable in this process's environment, and anything shaped
  like a known credential, becomes "[REDACTED]".
"""

import os
import re

SENSITIVE_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSW|CREDENTIAL|AUTH|COOKIE|SESSION", re.I)
CREDENTIAL_SHAPES = re.compile(
    r"sk-ant-[A-Za-z0-9_-]{16,}"           # Anthropic
    r"|AIza[0-9A-Za-z_-]{30,}"             # Google / Gemini
    r"|sk-[A-Za-z0-9]{32,}"                # OpenAI-style
    r"|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"
    r"|xox[abprs]-[A-Za-z0-9-]{10,}"       # Slack
    r"|AKIA[0-9A-Z]{16}"                   # AWS access key id
)
REDACTED = "[REDACTED]"
MIN_SECRET_LEN = 8  # shorter values ("1", "true") are not worth scrubbing and would mangle text


def _sensitive(environ):
    return {k: v for k, v in environ.items() if SENSITIVE_NAME.search(k)}


def shell_env_overrides(environ=None):
    """Env overrides that blank every secret-looking variable for the agent's shell."""
    return {k: "" for k in _sensitive(os.environ if environ is None else environ)}


def redact(obj, environ=None):
    """A copy of `obj` (dicts, lists, strings) with credentials replaced."""
    values = sorted((v for v in _sensitive(os.environ if environ is None else environ).values()
                     if len(v) >= MIN_SECRET_LEN), key=len, reverse=True)

    def scrub(s):
        for v in values:
            s = s.replace(v, REDACTED)
        return CREDENTIAL_SHAPES.sub(REDACTED, s)

    def walk(x):
        if isinstance(x, str):
            return scrub(x)
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x

    return walk(obj)
