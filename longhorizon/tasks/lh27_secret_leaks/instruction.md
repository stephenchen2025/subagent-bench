# Credential leak review

The secret scanner lit up across `/workspace/repos/`. Security needs the real
leaks only, as defined in `docs/LEAK_POLICY.md`, so it can rotate them today.

Write `/workspace/answer/leaks.json`, with every repository listed:

```json
{"<repo>": ["path/in/repo:LINE", ...]}
```

Use an empty list for a repository with no leaks.
