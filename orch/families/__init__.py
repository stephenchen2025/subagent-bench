"""Task families of the orchestrator track (ORCHESTRATOR.md 3)."""

from orch.families import chain, coupled, probe, wide

FAMILIES = {"W": wide, "P": probe, "C": coupled, "L": chain}
