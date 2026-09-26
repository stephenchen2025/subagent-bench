# Port every plugin to API v2

API v1 is removed in the next release. Port every plugin under
`/workspace/plugins/` to the v2 API in `pluginapi/base.py`. `docs/PORTING.md`
says what changes and what else each port must update.

`tests/` defines done: `cd /workspace && python -m pytest`. Do not edit the
tests.
