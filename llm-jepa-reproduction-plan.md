# Reproducing LLM-JEPA: Plan

Paper: *LLM-JEPA: Large Language Models Meet Joint Embedding Predictive Architectures* (Huang, LeCun, Balestriero), arXiv 2509.14252.
Authors' code: `rbalestr-lab/llm-jepa`.

> Caveat: this plan is based on the paper's main text only (read via the Hugging Face mirror). I have not read the appendix or the authors' repo, and the compute estimates below are my own guesses, not from the paper.

## 1. What is being reproduced

Fine-tune a pretrained LLM on paired data (Text, Code) with two losses:

```
L = L_LLM + λ · d(Pred(Enc(Text)), Enc(Code))
```

- `L_LLM`: normal next-token cross-entropy.
- `Enc(x)`: last-layer hidden state of the last token of `x`.
- `Pred`: append `k` `[PRED]` tokens to Text and take the last one's hidden state (`k=0` means identity).
- `d`: cosine distance.
- `λ`: weight of the JEPA term.
- Text and Code are packed into one sequence with a block-causal attention mask so they cannot see each other (2 forward passes instead of 3).

## 2. Difficulty overview

| Piece | Difficulty | Notes |
|---|---|---|
| Loss, mask, `[PRED]` tokens | Easy | A few dozen lines on Hugging Face Transformers; the paper prints the mask snippet |
| Models and datasets | Easy | All public (Llama and Gemma need license acceptance) |
| Matching the paper's numbers | Moderate | 5 seeds per setting, large run-to-run spread, prompt/eval details matter |
| Full hyperparameter grids | Costly | 4 learning rates plus a 20-point `(k, λ)` grid per (model, dataset) pair |
| 7B/8B models, Spider execution eval, dropout sweeps | Harder | More memory (use LoRA) and more runs |
| Pretraining at scale | Research problem | The paper does not solve how to get views for arbitrary text |

## 3. Step-by-step plan

### Step 0: Setup
- Get a GPU machine (a single modern GPU is enough for 1B models).
- Accept the licenses for Llama-3.2 and Gemma-2 on Hugging Face.
- Clone `rbalestr-lab/llm-jepa` and read its README and training script.
- Pin library versions (torch, transformers) and record them.

### Step 1: Smallest end-to-end test (the main target)
- Model: `Llama-3.2-1B-Instruct`.
- Data: NL-RX-SYNTH (description to regex).
- Run two arms:
  - Baseline: next-token loss only.
  - LLM-JEPA: use a config from the paper, e.g. `lr=2e-5`, `λ` in 1-2, `k` in 1-3.
- Metric: exact match of the generated regex.
- Seeds: `82, 23, 37, 84, 4`.
- Reference numbers (paper): about 52% (baseline) vs about 71% (LLM-JEPA) in Fig. 3; 57.3 ± 5.3 vs 71.5 ± 1.3 in the Table 3 ablation (lr=2e-5, λ=1, k=1).
- Success criterion: LLM-JEPA beats baseline by a clear margin across all 5 seeds. Report mean ± std and a paired one-tailed t-test.

### Step 2: Sanity checks on your implementation
- Confirm that without the JEPA gradient, the JEPA distance does not shrink (the paper's Fig. 3 finding).
- Confirm that the next-token loss looks the same with and without the JEPA term.
- Check the attention mask by verifying the Text embedding does not change when Code tokens are altered.

### Step 3: Ablations (cheap, on NL-RX-SYNTH)
Reproduce Table 3 (lr=2e-5, λ=1, k=1):
- cosine vs L2 vs MSE
- append vs prepend `[PRED]`
- Text-to-Code vs Code-to-Text
- InfoNCE (temperature 0.07)

### Step 4: Expand datasets and models
- Datasets: NL-RX-TURK, GSM8K, Spider (needs a SQL execution harness).
- Models: Gemma-2-2B-it, OpenELM-1.1B-Instruct, OLMo-2-0425-1B-Instruct.
- Protocol per (model, dataset):
  1. Sweep baseline `lr` in {1e-5, 2e-5, 4e-5, 8e-5}; pick best after 4 epochs.
  2. Keep that `lr` and sweep `(k, λ)` in {0..4} x {0.5, 1, 2, 4}.
  3. Run 5 seeds at the best config for each arm.

### Step 5: Extensions (optional)
- Overfitting check: train 6+ epochs and plot accuracy over epochs for both arms.
- LoRA at several ranks (use LoRA for 7B/8B models).
- Loss dropout: skip the JEPA term on a fraction of batches (e.g. 0.5, 0.75); compare accuracy at equal PFLOPs; keep `λ * (1 - dropout)` roughly constant.
- Non-code data: NQ-Open (Text = question, Code = answer) and HellaSwag (Text = context, Code = correct continuation).
- Reasoning models: Qwen3-1.7B and DeepSeek-R1-Distill-Qwen-1.5B on GSM8K.
- Pretraining from scratch: NL-RX-SYNTH (prefix-match evaluation) and the paraphrase dataset (`cestwc/paraphrase`), then fine-tune on Rotten Tomatoes/Yelp without the JEPA loss.

### Step 6: Representation analysis (optional)
- t-SNE of Text and Code embeddings for base, fine-tuned, and LLM-JEPA models.
- SVD of `Enc(Text) - Enc(Code)`; expect much smaller singular values with LLM-JEPA.
- Least-squares fit of a linear map from Text to Code embeddings.

## 4. Risks and things to watch

- Large run-to-run variance: always use 5 seeds and report spread.
- Evaluation details (prompt templates, exact-match rules, answer parsing) can shift numbers by several points.
- Batch size, epochs, and other training details may not be fully specified in the main text; check the appendix and the repo.
- Tuning asymmetry: the baseline only tunes `lr`, while LLM-JEPA also tunes `k` and `λ`. Consider giving the baseline extra tuning budget to test how much of the gain survives.
- Cost: LLM-JEPA training is about 2x a baseline run, and the full grid is large. Start with Step 1 and expand only if it reproduces.

## 5. Suggested order of work

1. Steps 0-1 (reproduce the headline result).
2. Step 2 (sanity checks).
3. Step 3 (ablations).
4. Steps 4-6 as time and compute allow.
