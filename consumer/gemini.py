"""Model-backed frozen consumer on Gemini, for the free-tier pilot.

Same system prompt, same probe prompt, same forced-choice contract as
ClaudeConsumer -- only the model behind it differs. That still makes it a
different consumer: consumer_id changes, and a score judged by it is not
comparable with one judged by the Claude consumer (DESIGN.md 4). Use it to
pilot the pipeline for free, not to publish.

Goes through litellm (already a mini-swe-agent dependency), so it adds no
package. Import is lazy, like the Claude consumer's.
"""

import json
import re
import time

from consumer.probe import SYSTEM_PROMPT, build_prompt

MODEL = "gemini/gemini-3.5-flash-lite"
PROMPT_VERSION = "v1"
MAX_TOKENS = 8000

_JSON_FORMAT = (
    "\n\nRespond with JSON only, no prose and no code fence, in exactly this shape:\n"
    '{"answers": [{"question_number": 1, "choice": "<one option, verbatim>", '
    '"confidence": 0.0}, ...]}\n'
    "One entry per question, in order. `choice` must be copied verbatim from that "
    "question's options."
)


def _loads(text):
    """Parse the JSON body, tolerating a code fence the model added anyway."""
    text = (text or "").strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return json.loads(fenced.group(1) if fenced else text)


class GeminiConsumer:
    """The frozen consumer's contract, answered by a Gemini model.

    Unlike current Claude models, Gemini accepts temperature, so it is pinned
    to 0. That narrows the noise floor but does not remove it -- the floor is
    still measured, never assumed (DESIGN.md 7.1).

    `min_interval_s` spaces calls out to stay under a free-tier per-minute
    limit instead of leaning on 429 retries.
    """

    def __init__(self, model=MODEL, completion=None, min_interval_s=0.0):
        if completion is None:
            import litellm

            completion = litellm.completion
        self._completion = completion
        self._model = model
        self._min_interval_s = min_interval_s
        self._last_call = 0.0

    @property
    def consumer_id(self):
        return f"{self._model}/{PROMPT_VERSION}/temperature=0"

    def _pace(self):
        wait = self._last_call + self._min_interval_s - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def judge(self, report, probes):
        from consumer.claude import ClaudeConsumer

        self._pace()
        response = self._completion(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(report, probes) + _JSON_FORMAT},
            ],
            temperature=0,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"},
        )
        text = response.choices[0].message.content
        # Parsing is shared with the Claude consumer on purpose: an off-menu
        # choice must be scored the same way whichever model produced it.
        verdict = ClaudeConsumer._parse(_loads(text), probes)
        verdict.consumer_id = self.consumer_id
        return verdict
