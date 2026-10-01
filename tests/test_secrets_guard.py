"""The agent's shell must not see API keys, and saved episodes must not hold them.

A Gemma pilot episode ran `env` and wrote the host's API keys into its
trajectory; GitHub push protection caught it. These tests pin both layers of
the fix in tools/secrets_guard.py.
"""

import json

import pytest

from tools.secrets_guard import REDACTED, redact, shell_env_overrides

FAKE_ENV = {
    "ANTHROPIC_API_KEY": "sk-ant-api03-" + "x" * 40,
    "GEMINI_API_KEY": "AIza" + "y" * 35,
    "HANDOFF_ANTHROPIC_API_KEY": "handoff-secret-value",
    "GITHUB_TOKEN": "ghs_" + "z" * 36,
    "PATH": "/usr/bin:/bin",
    "HOME": "/root",
    "DEBUG_SESSION": "1",  # sensitive name, value too short to scrub
}


def test_overrides_blank_every_secret_looking_variable():
    overrides = shell_env_overrides(FAKE_ENV)
    assert set(overrides) == {"ANTHROPIC_API_KEY", "GEMINI_API_KEY", "HANDOFF_ANTHROPIC_API_KEY",
                              "GITHUB_TOKEN", "DEBUG_SESSION"}
    assert all(v == "" for v in overrides.values())


def test_agent_shell_sees_no_key(monkeypatch, tmp_path):
    local = pytest.importorskip("minisweagent.environments.local")
    for k, v in FAKE_ENV.items():
        monkeypatch.setenv(k, v)
    env = local.LocalEnvironment(cwd=str(tmp_path), env=shell_env_overrides())
    out = env.execute({"command": "env"})["output"]
    assert "PATH=" in out  # the shell still works
    for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "HANDOFF_ANTHROPIC_API_KEY", "GITHUB_TOKEN"):
        assert FAKE_ENV[k] not in out


def test_redact_scrubs_env_values_everywhere():
    record = {
        "report": f"key is {FAKE_ENV['HANDOFF_ANTHROPIC_API_KEY']}",
        "trajectory": [{"command": "env",
                        "output": "\n".join(f"{k}={v}" for k, v in FAKE_ENV.items())}],
        "tokens": 1200,
    }
    clean = redact(record, environ=FAKE_ENV)
    text = json.dumps(clean)
    for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "HANDOFF_ANTHROPIC_API_KEY", "GITHUB_TOKEN"):
        assert FAKE_ENV[k] not in text
    assert REDACTED in clean["report"]
    assert "PATH=/usr/bin:/bin" in text and "DEBUG_SESSION=1" in text  # harmless values kept
    assert clean["tokens"] == 1200
    assert record["report"].endswith("handoff-secret-value")  # input not mutated


def test_redact_catches_credential_shapes_not_in_env():
    leaked = "found sk-ant-api03-" + "q" * 30 + " and AIza" + "r" * 35 + " in a log"
    assert redact(leaked, environ={}) == f"found {REDACTED} and {REDACTED} in a log"


def test_redact_leaves_ordinary_text_alone():
    text = "retry_policy lives in settings/upload.yml:14; sk-learn is a library"
    assert redact(text, environ={}) == text

