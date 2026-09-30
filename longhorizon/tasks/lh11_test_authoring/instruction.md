# Write the missing tests

Nothing under `/workspace/lib/` has tests. For every module `lib/<name>.py`,
write `tests/test_<name>.py` (pytest) for its public function. Each public
function's docstring is its specification.

Your tests should pass against the code as it is and fail if the behaviour
the docstring specifies ever changes. Test behaviour through the function
itself; do not read or fingerprint the source.

Run them with `cd /workspace && python -m pytest`. Do not modify `lib/`.
