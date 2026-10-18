import io
import json
import urllib.error

import pytest

from wikiplant.llm import USAGE, QuotaExhausted, fallback, gemini_model


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


DAY = (429, '{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"}')


def test_one_per_day_429_is_waited_out():
    m = gemini_model("t-day1", key="k", opener=fake([DAY, OK]), sleep=lambda s: None)
    assert m("hi") == "hello"


def test_repeated_per_day_429s_stop_the_run():
    m = gemini_model("t-day", key="k", opener=fake([DAY, DAY, DAY]), sleep=lambda s: None)
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


def test_long_retry_delay_means_daily_quota():
    body = '{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier", "retryDelay": "26882s"}'
    slept = []
    m = gemini_model("t-long", key="k", opener=fake([(429, body)]), sleep=slept.append)
    with pytest.raises(QuotaExhausted):
        m("hi")
    assert slept == []          # never sleeps for hours


def test_fallback_moves_down_the_chain():
    def spent(p):
        raise QuotaExhausted("x")
    spent.name = "a"
    ok = lambda p: "from b"
    ok.name = "b"
    chain = fallback([spent, ok])
    assert chain("q") == "from b" and chain("q") == "from b" and chain.spent == {"a"}
    dead = fallback([spent])
    with pytest.raises(QuotaExhausted):
        dead("q")


def test_json_prompts_ask_for_json_mode():
    op = fake([OK, OK])
    m = gemini_model("t-json", key="k", opener=op, sleep=lambda s: None)
    m("Return only JSON: {}")
    m("Reply with only the short answer.")
    assert op.calls[0]["generationConfig"]["responseMimeType"] == "application/json"
    assert "responseMimeType" not in op.calls[1]["generationConfig"]
