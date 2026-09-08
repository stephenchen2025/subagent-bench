"""Turning a HANDOFF task spec into something Harbor can run.

Harbor supplies the runner and mini-swe-agent supplies the agent (DESIGN.md 8.1).
This package is the seam: it emits Harbor task directories, wraps the agent so
it produces the artifact triple, and plays F10's scripted handback inside a
single trial.
"""
