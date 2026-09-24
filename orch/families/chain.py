"""L -- ledger chain. Long, and nothing to split.

Follow a chain of H ledger pages. Each page lists a handful of accounts, each
pointing at another page, and a rule saying which entry to follow ("the largest
credit", "the account that comes first alphabetically among debits", ...). You
cannot know page k+1 without reading page k, so the work is strictly sequential:
H hops is H dependent steps, 60 to 140 of them.

This is the negative control. It is as long as any delegation-favourable task,
and it "breaks down" only into consecutive segments, each of which needs the
previous one's result. Parallel workers have nothing to do; a relay of workers
does the same reads plus briefs and cold starts. Pages are short on purpose, so
the whole chain fits one 32k window: a solo agent is not walled, and the
scaling-agent-systems finding (multi-agent variants degraded sequential tasks by
39-70%) predicts delegation can only cost here.

Decoy pages outnumber the chain, and they are real pages with real rules, so a
wrong turn leads somewhere plausible rather than to an error. The listing of
ledger/ says nothing about order.
"""

import json

from orch.task import SOLO, OrchTask, rng_for, task_id

FAMILY = "L"
SIZES = (60, 100, 140)

ACCOUNTS = [
    "Abbott", "Baker", "Castillo", "Dunn", "Eriksen", "Fofana", "Grant", "Hughes",
    "Ibarra", "Jensen", "Kowalski", "Lambert", "Moreau", "Nakamura", "Osei", "Park",
    "Quinn", "Rahman", "Silva", "Tanaka", "Umar", "Vance", "Weber", "Xu", "Young", "Zhou",
]

# (rule text, chooser over [(account, amount), ...] -> index)
RULES = [
    ("Follow the entry with the largest credit.",
     lambda e: max(range(len(e)), key=lambda i: e[i][1])),
    ("Follow the entry with the largest debit (the most negative amount).",
     lambda e: min(range(len(e)), key=lambda i: e[i][1])),
    ("Follow the entry whose amount is closest to zero.",
     lambda e: min(range(len(e)), key=lambda i: abs(e[i][1]))),
    ("Follow the credit belonging to the account that comes first alphabetically.",
     lambda e: min((i for i in range(len(e)) if e[i][1] > 0), key=lambda i: e[i][0])),
    ("Follow the debit belonging to the account that comes last alphabetically.",
     lambda e: max((i for i in range(len(e)) if e[i][1] < 0), key=lambda i: e[i][0])),
    ("Follow the entry with the second-largest amount.",
     lambda e: sorted(range(len(e)), key=lambda i: e[i][1])[-2]),
]

INSTRUCTION = """\
The directory `ledger/` holds ledger pages. Starting at `ledger/{start}.txt`, follow
the chain: each page lists entries, each pointing at another page, and states a rule
for which entry to follow. Keep going until you reach the closing page.

Write the result to `answer.json` in the working directory:

```json
{{"path": ["{start}", "P-....", "..."], "closing_code": "...."}}
```

`path` is every page you visited in order, starting with `{start}` and ending with
the closing page. The score is the length of the correct prefix of your path over
the length of the chain, so write down how far you got even if you don't finish.
"""

SEGMENT_BRIEF = """\
Follow the ledger chain starting at `ledger/{start}.txt` for {hops} hops (or until the
closing page, if sooner). Each page states a rule for which entry to follow. Report
every page you visited in order, one page code per line, starting with {start}, and
the closing code if you reached the closing page.
"""


def _entries(rng, n):
    """n entries with distinct accounts and distinct, nonzero amounts; mixed signs."""
    accounts = rng.sample(ACCOUNTS, n)
    amounts = rng.sample([a for a in range(-900, 901) if a != 0], n)
    if all(a > 0 for a in amounts):
        amounts[0] = -amounts[0]
    if all(a < 0 for a in amounts):
        amounts[0] = -amounts[0]
    return list(zip(accounts, amounts))


def _page(code, rule_text, entries, targets):
    lines = [f"Ledger page {code}", "", "account      amount   see page"]
    for (account, amount), target in zip(entries, targets):
        lines.append(f"{account:<12} {amount:+6d}   {target}")
    lines += ["", rule_text, ""]
    return "\n".join(lines)


def generate(size, seed):
    rng = rng_for(FAMILY, size, seed)
    codes = [f"P-{n}" for n in rng.sample(range(1000, 9999), size * 3)]
    chain, decoys = codes[:size], codes[size:]
    closing_code = f"{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}"
    files = {}
    for i, code in enumerate(chain):
        if i == len(chain) - 1:
            files[f"ledger/{code}.txt"] = (
                f"Ledger page {code}\n\nThis is the closing page. Closing code: {closing_code}\n")
            break
        rule_text, choose = rng.choice(RULES)
        entries = _entries(rng, rng.randint(5, 7))
        pick = choose(entries)
        targets = [rng.choice(decoys) for _ in entries]
        targets[pick] = chain[i + 1]
        files[f"ledger/{code}.txt"] = _page(code, rule_text, entries, targets)
    for code in decoys:
        rule_text, _ = rng.choice(RULES)
        entries = _entries(rng, rng.randint(5, 7))
        targets = [rng.choice(decoys + chain[1:]) for _ in entries]
        files[f"ledger/{code}.txt"] = _page(code, rule_text, entries, targets)
    answer = json.dumps({"path": chain, "closing_code": closing_code})
    return OrchTask(
        id=task_id(FAMILY, size, seed),
        family=FAMILY,
        size=size,
        seed=seed,
        label=SOLO,
        instruction=INSTRUCTION.format(start=chain[0]),
        files=files,
        truth={"path": chain, "closing_code": closing_code},
        solution=f"cat > answer.json <<'EOF'\n{answer}\nEOF\n",
        work_items=[],  # nothing independent to hand out
    )
