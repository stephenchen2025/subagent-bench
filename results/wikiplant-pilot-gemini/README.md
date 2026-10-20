# wikiplant pilot on Gemini's free tier

The first live run of the planted-fact pipeline (2026-10-18). It is a plumbing test and
not a dataset: two puzzles, free-tier models, no human review.

- Corpus: Wikimedia's Structured Wikipedia on Hugging Face (English, 2024-09-16), all 86
  shards streamed and filtered to British industry, transport and the towns around them:
  47,778 pages, 490,647 paragraphs, 7,984 host-eligible pages. Wikipedia and its dumps
  are blocked by this environment's network policy; Hugging Face is not.
- Models: Gemini 3 Flash Preview and 3.7 Flash for design, the oracle and the consistency
  judge; 3.5 and 3.1 Flash-Lite as writers, the search agent and the style judge.
- Clusters: Sutton Veny (Wiltshire villages, 40 pages), Shalden (Alton and the Watercress
  Line, 67 pages), Haywards Heath (57 pages). The third puzzle's design failed: the reply
  was cut off mid-JSON.

`report.md` is the run's own report. The other files are its outputs.

## What the gates found

| gate | p01 (easy) | p02 (medium) | finding |
|---|---|---|---|
| closed-book, base corpus, both oracles | pass | pass | Unanswerable from memory or from real Wikipedia; answerable and unique given the planted text. |
| lexical shortcut | rank 24 | rank 262,135 | Questions describe bridge entities instead of naming them, so BM25 cannot find the final hop. The tier bands need calibrating against how the designer actually writes. |
| consistency | fail | fail | Real contradictions in decoys: a wharf leased from the LNER in 1895 (it was formed in 1923), a survey of a 2020 derailment dated 1879, a stationmaster appointed after the station opened, and an invented firm named after a real Cornish hamlet. The judge also flagged invented firms just for being absent from real text. |
| style (pick-the-planted) | 0.80 | 1.00 | Chance is 0.25. The Flash-Lite writers produce text that is easy to spot ("Historical records indicate..."), and gold paragraphs are sometimes one bare sentence. |

## Fixed since this run

- Decoy years come from the span of years the host page itself mentions.
- Invented names use coined place stems instead of real places.
- A near-miss for a person is a person, not a firm.
- The consistency judge is told that invented entities are absent from real text by design.
- Real paragraphs keep their snapshot ids after planting, which fixed a gate 5 crash.
- JSON prompts use Gemini's JSON mode, and the output cap is 32k tokens.
- A free-tier daily quota (20 requests per model per day for the Flash models) moves a
  role to the next model in its chain instead of stalling the run.

## Still open

- Style is the main problem, as the design doc predicted. It needs stronger writers than
  Flash-Lite, prompt work, and the copy and blocklist checks tuned on rejected units.
- The lexical-shortcut bands need calibrating.
- Model usage was 105 successful calls over the run. The free tier allows about 20 per Flash
  model per day, so a larger batch needs a paid key or several days.

## Second run (2026-10-19), after the fixes

Same snapshot, same three clusters, current code. Outputs are in `run2/`.

- **Plumbing:** It ran end to end on the free tier (28.5 minutes, 56 calls). One crash on
  the way, a year sent as the string "1857", is now fixed: years are normalized and a bad
  one goes back to the model. An unexpected error in one puzzle no longer ends the batch.
- **Design:** 1 of 3 puzzles passed. p02 cited an infobox as a paragraph and planted on a
  page outside the host list. p03 left three real facts without a paragraph id. The
  designer prompt now spells both rules out. Design is the weakest step at medium difficulty.
- **p01 (easy):** Q: "Which merchant owned a cloth mill in 1824 in the parish that includes
  the now uninhabited village of Imber?" A: Jedidiah Thwaite. It passed name collision,
  closed-book, both oracles and the base corpus.
  - Lexical shortcut: rank 11 against the easy band of 2-10. That is close, which points
    at band calibration rather than a bad puzzle.
  - Consistency: 2 findings, and neither is one of the pilot's bugs (decoy years now fall
    inside their host page's years). The gold finding is a judge false positive: it
    compared a claim about Heytesbury with a paragraph about a different village that BM25
    retrieved. The decoy finding is real: an invented coal company "bought coal from" a
    Danish country house. The domain filter let that page in, and decoy relations still
    ignore what the host page is about.
  - Style: 1.00 against a chance of 0.25. It is still the main open problem.

Next fixes in order: style (stronger writers, prompt work), decoy relations that fit the
host, consistency-judge context limited to the host page and the pages the claim links to,
and the lexical bands.
