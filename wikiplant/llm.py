"""Model adapters: any `Model` is a callable str -> str.

gemini_model talks to the Gemini REST API with the standard library only. It
paces calls to stay under a free-tier per-minute limit, waits out 429s using the
server's retry delay, retries transient 5xx errors, and stops with QuotaExhausted
when a per-day quota is spent, so a run can resume the next day. Every call is
counted in USAGE for the run report.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
USAGE = defaultdict(lambda: {"calls": 0, "tokens": 0, "retries": 0})


class QuotaExhausted(RuntimeError):
    pass


def _retry_delay(body):
    """Seconds the server asks us to wait, from RetryInfo or the message text."""
    m = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', body) or re.search(r"retry in (\d+(?:\.\d+)?)s", body, re.I)
    return float(m.group(1)) if m else None


def gemini_model(model, min_interval_s=4.0, temperature=None, max_retries=8, max_output_tokens=8192, key=None,
                 opener=urllib.request.urlopen, sleep=time.sleep, clock=time.monotonic):
    key = key or os.environ["GEMINI_API_KEY"]
    state = {"last": -1e9}

    def call(prompt):
        cfg = {"maxOutputTokens": max_output_tokens}
        if temperature is not None:
            cfg["temperature"] = temperature
        body = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": cfg}).encode()
        for attempt in range(max_retries + 1):
            wait = state["last"] + min_interval_s - clock()
            if wait > 0:
                sleep(wait)
            state["last"] = clock()
            req = urllib.request.Request(GEMINI_URL.format(model), data=body,
                                         headers={"x-goog-api-key": key, "Content-Type": "application/json"})
            try:
                data = json.loads(opener(req, timeout=300).read())
            except urllib.error.HTTPError as e:
                text = e.read().decode(errors="replace")
                if e.code == 429:
                    if re.search(r"PerDay|per day|daily", text, re.I) and not re.search(r"PerMinute", text):
                        raise QuotaExhausted(f"{model}: daily quota spent") from None
                    USAGE[model]["retries"] += 1
                    sleep(_retry_delay(text) or min(60, 5 * 2 ** attempt))
                    continue
                if e.code in (500, 502, 503, 504) and attempt < max_retries:
                    USAGE[model]["retries"] += 1
                    sleep(min(60, 3 * 2 ** attempt))
                    continue
                raise RuntimeError(f"{model}: HTTP {e.code}: {text[:300]}") from None
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < max_retries:
                    USAGE[model]["retries"] += 1
                    sleep(min(60, 3 * 2 ** attempt))
                    continue
                raise RuntimeError(f"{model}: {e}") from None
            USAGE[model]["calls"] += 1
            USAGE[model]["tokens"] += data.get("usageMetadata", {}).get("totalTokenCount", 0)
            cands = data.get("candidates") or []
            parts = (cands[0].get("content") or {}).get("parts", []) if cands else []
            return "".join(p.get("text", "") for p in parts if not p.get("thought"))
        raise RuntimeError(f"{model}: gave up after {max_retries} retries")
    call.name = model
    return call
