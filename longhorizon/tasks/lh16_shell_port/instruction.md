# Retire the shell toolbox

Port every pipeline in `/workspace/scripts/` to Python: `py/<name>.py`, taking
the same file arguments and printing exactly the same bytes to stdout. Example
inputs are in `samples/<name>/` (in argument order), and you can run the
original scripts to compare.

The ports will replace the scripts everywhere they run, on inputs you have not
seen, where the shell tools are not installed: pure Python, standard library
only, and a port may not run other programs.
