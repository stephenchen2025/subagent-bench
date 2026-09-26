# Hit the performance budget

Every function in `/workspace/perf/` is correct and far too slow for
production traffic. `docs/BUDGET.md` gives the input size each must handle in
under a second.

Make each one fast enough. Every function must keep returning exactly what it
returns today, for every input: same values, same order, same winner on ties.
Keep module and function names and signatures unchanged.
