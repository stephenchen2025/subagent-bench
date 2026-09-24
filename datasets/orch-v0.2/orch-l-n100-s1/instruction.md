The directory `ledger/` holds ledger pages. Starting at `ledger/P-8333.txt`, follow
the chain: each page lists entries, each pointing at another page, and states a rule
for which entry to follow. Keep going until you reach the closing page.

Write the result to `answer.json` in the working directory:

```json
{"path": ["P-8333", "P-....", "..."], "closing_code": "...."}
```

`path` is every page you visited in order, starting with `P-8333` and ending with
the closing page. The score is the length of the correct prefix of your path over
the length of the chain, so write down how far you got even if you don't finish.
