# Partner identifier validation

The partner onboarding form must reject malformed identifiers before they
reach the partner systems. For every format specified in `/workspace/specs/`,
write `validators/<format>.py` exposing `is_valid(text: str) -> bool`, exactly
as the specification defines it. Standard library only.

Each spec gives a few valid examples. Your validators will be tested on
identifiers you have not seen, valid and invalid.
