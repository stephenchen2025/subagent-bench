import io
import json
import urllib.error

import pytest

from wikiplant.llm import USAGE, QuotaExhausted, gemini_model


def fake(responses):
    calls = []

    def opener(req, timeout):
        calls.append(json.loads(req.data))
        r = responses.pop(0)
        if isinstance(r, tuple):
            code, body = r
            raise urllib.error.HTTPError(req.full_url, code, "err", {}, io.BytesIO(body.encode()))
        return io.BytesIO(json.dumps(r).encode())
    opener.calls = calls
    return opener


OK = {"candidates": [{"content": {"parts": [{"text": "thinking", "thought": True}, {"text": "hello"}]}}],
      "usageMetadata": {"totalTokenCount": 7}}


def test_returns_text_and_counts_usage():
    m = gemini_model("t-ok", key="k", opener=fake([OK]), sleep=lambda s: None)
    assert m("hi") == "hello" and USAGE["t-ok"]["calls"] == 1 and USAGE["t-ok"]["tokens"] == 7


def test_waits_out_per_minute_limits_and_5xx():
    slept = []
    body = '{"error": {"details": [{"retryDelay": "17s"}], "message": "PerMinute quota"}}'
    m = gemini_model("t-retry", key="k", opener=fake([(429, body), (503, "busy"), OK]), sleep=slept.append)
    assert m("hi") == "hello"
    assert 17.0 in slept and USAGE["t-retry"]["retries"] == 2


def test_daily_quota_stops_the_run():
    m = gemini_model("t-day", key="k", opener=fake([(429, '{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"}')]),
                     sleep=lambda s: None)
    with pytest.raises(QuotaExhausted):
        m("hi")


def test_paces_calls():
    now = [0.0]
    slept = []

    def sleep(s):
        slept.append(s)
        now[0] += s
    m = gemini_model("t-pace", key="k", min_interval_s=4, opener=fake([OK, OK]), sleep=sleep, clock=lambda: now[0])
    m("a")
    m("b")
    assert slept == [4.0]
