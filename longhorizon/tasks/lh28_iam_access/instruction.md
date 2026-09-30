# Access review

The auditors sent access questions for every principal: see
`/workspace/questions/`. Answer each one from the IAM documents in `iam/`,
evaluated exactly as `docs/EVALUATION.md` describes.

Write `/workspace/answer/access.json`, one list of five answers per principal,
in question order:

```json
{"<principal>": ["allow", "deny", "deny", "allow", "deny"]}
```
