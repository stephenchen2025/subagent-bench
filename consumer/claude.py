"""Model-backed frozen consumer (Claude).

Import is lazy: the whole scoring pipeline runs offline without the SDK
installed, and only this module needs it.
"""

import json

from consumer.probe import SYSTEM_PROMPT, ProbeAnswer, Verdict, build_prompt

# Pinned. Changing any of these changes what a HANDOFF score means, so they are
# part of consumer_id and a change is a benchmark major-version bump.
MODEL = "claude-opus-5"
PROMPT_VERSION = "v1"
MAX_TOKENS = 16000
EFFORT = "high"


def _schema(probes):
    """One enum-constrained answer per probe, in order."""
    return {
        "type": "object",
        "properties": {
            "answers": {
                "type": "array",
                "minItems": len(probes),
                "maxItems": len(probes),
                "items": {
                    "type": "object",
                    "properties": {
                        "question_number": {"type": "integer"},
                        "choice": {"type": "string"},
                        "confidence": {"type": "number"},
                    },
                    "required": ["question_number", "choice", "confidence"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["answers"],
        "additionalProperties": False,
    }


class ClaudeConsumer:
    """The frozen consumer as specified in DESIGN.md 4.

    Note on determinism: current Claude models reject `temperature` and `top_p`,
    so this consumer is *pinned*, not deterministic. Repeat runs can differ.
    That is exactly why `consumer.base.noise_floor` is mandatory before
    comparing two systems -- a gap below the floor is a tie, not a result.
    """

    def __init__(self, client=None, model=MODEL, effort=EFFORT):
        if client is None:
            try:
                import anthropic
            except ImportError as exc:  # pragma: no cover - env dependent
                raise ImportError(
                    "pip install anthropic, or pass an explicit client. "
                    "The offline scorers and ReplayConsumer need neither."
                ) from exc
            client = anthropic.Anthropic()
        self._client = client
        self._model = model
        self._effort = effort

    @property
    def consumer_id(self):
        return f"{self._model}/{PROMPT_VERSION}/effort={self._effort}"

    def judge(self, report, probes):
        response = self._client.messages.create(
            model=self._model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(report, probes)}],
            output_config={
                "effort": self._effort,
                "format": {"type": "json_schema", "schema": _schema(probes)},
            },
        )
        if getattr(response, "stop_reason", None) == "refusal":
            raise RuntimeError(
                f"consumer refused to judge: {getattr(response, 'stop_details', None)}"
            )
        text = next(b.text for b in response.content if b.type == "text")
        return self._parse(json.loads(text), probes)

    @staticmethod
    def _parse(payload, probes):
        raw = sorted(payload["answers"], key=lambda a: a["question_number"])
        answers = []
        for item, probe in zip(raw, probes):
            choice = item["choice"]
            if choice not in probe.options:
                # An off-menu answer is not a licence to guess: it carries no
                # information about the report, so it is scored as a miss with
                # the confidence the consumer actually stated.
                choice = f"<invalid: {choice}>"
            answers.append(
                ProbeAnswer(choice, max(0.0, min(1.0, float(item["confidence"]))))
            )
        return Verdict(answers=answers, consumer_id=f"{MODEL}/{PROMPT_VERSION}")

    def count_prompt_tokens(self, report, probes):
        """Token accounting for the cost axis -- never estimate, never tiktoken."""
        return self._client.messages.count_tokens(
            model=self._model,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(report, probes)}],
        ).input_tokens
