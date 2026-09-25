"""The Gemini consumer, against a stubbed completion call -- no key, no network."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer.gemini import GeminiConsumer  # noqa: E402
from consumer.probe import INSUFFICIENT, Probe, SYSTEM_PROMPT  # noqa: E402

PROBES = [
    Probe("Where is the retry policy?", ["client.py", "app.yaml", INSUFFICIENT], "client.py"),
    Probe("Does app.yaml exist?", ["yes", "no", INSUFFICIENT], "no"),
]


def _reply(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def _consumer(text, seen=None):
    def completion(**kwargs):
        if seen is not None:
            seen.update(kwargs)
        return _reply(text)
    return GeminiConsumer(model="gemini/test", completion=completion)


ANSWERS = {"answers": [
    {"question_number": 1, "choice": "client.py", "confidence": 0.9},
    {"question_number": 2, "choice": "no", "confidence": 0.8},
]}


def test_judges_with_the_shared_prompt_pinned_to_temperature_zero():
    seen = {}
    verdict = _consumer(json.dumps(ANSWERS), seen).judge("report text", PROBES)
    assert [a.chosen for a in verdict.answers] == ["client.py", "no"]
    assert seen["temperature"] == 0
    assert seen["messages"][0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert "report text" in seen["messages"][1]["content"]


def test_consumer_id_names_the_model_and_is_on_the_verdict():
    consumer = _consumer(json.dumps(ANSWERS))
    verdict = consumer.judge("r", PROBES)
    assert verdict.consumer_id == consumer.consumer_id
    assert consumer.consumer_id.startswith("gemini/test/")


def test_a_code_fenced_reply_still_parses():
    verdict = _consumer("```json\n" + json.dumps(ANSWERS) + "\n```").judge("r", PROBES)
    assert [a.chosen for a in verdict.answers] == ["client.py", "no"]


def test_an_off_menu_choice_is_scored_as_a_miss_not_coerced():
    bad = {"answers": [
        {"question_number": 1, "choice": "somewhere", "confidence": 0.9},
        {"question_number": 2, "choice": "no", "confidence": 1.4},
    ]}
    verdict = _consumer(json.dumps(bad)).judge("r", PROBES)
    assert verdict.answers[0].chosen.startswith("<invalid")
    assert verdict.answers[1].confidence == 1.0
