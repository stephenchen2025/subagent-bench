# Localisation QA before the release

The translation vendors delivered every catalogue in `/workspace/locales/`.
Before we ship, check each one against the English source (`locales/en.json`)
by the rules in `docs/L10N_RULES.md`.

Write `/workspace/answer/l10n_errors.json`, one entry per catalogue:

```json
{"<locale>": ["<key>:<code>", ...]}
```

Use an empty list for a catalogue with no errors.
