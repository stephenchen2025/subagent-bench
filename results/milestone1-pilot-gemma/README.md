# Milestone 1 -- free-tier Gemma pilot (in progress)

**A pilot, not a Milestone 1 result.** The frozen consumer here is
`gemini/gemini-3.1-flash-lite`, not the Claude consumer, and a different
consumer is a different benchmark (DESIGN.md 4). This run checks that the
whole pipeline (episodes, consumer, noise floor, comparison) works on real
models while the Anthropic account is out of credit.

- Subagents: `gemini/gemma-4-31b-it`, `gemini/gemma-4-26b-a4b-it`
- Consumer: `gemini/gemini-3.1-flash-lite`
- Why Gemma: Gemini 3.5 Flash's free tier allows 20 requests/day per model,
  which is less than one episode needs; Gemma's free tier is metered per minute.

Episodes are snapshotted here as the run progresses. To resume:

    mkdir -p build/milestone1-pilot-gemini_gemini-3.1-flash-lite
    cp -r results/milestone1-pilot-gemma/episodes build/milestone1-pilot-gemini_gemini-3.1-flash-lite/
    make pilot-gemini GEMINI_MODELS=gemini/gemma-4-31b-it,gemini/gemma-4-26b-a4b-it \
                      GEMINI_CONSUMER=gemini/gemini-3.1-flash-lite
