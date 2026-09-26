# Backport PATHGUARD-2026-004

`fix/PATHGUARD-2026-004.patch` fixes a path traversal in `pathguard` on main.
Backport it to every supported release line under `/workspace/releases/`.
`SUPPORT.md` says which lines are supported. End-of-life lines are frozen.

The code has moved around between releases, so the patch will not apply as-is.
Put the equivalent fix wherever each line joins paths. A line that does not
have the vulnerable code needs no change. Each line's own tests
(`releases/<line>/tests/`) must keep passing; do not edit them.

When you are done, write `/workspace/BACKPORT_REPORT.md` with one line per
release line: patched, not affected (and why), or end of life.
