"""Task families of the orchestrator track (ORCHESTRATOR.md 3)."""

from orch.families import coupled, probe, small, wide

FAMILIES = {"W": wide, "P": probe, "C": coupled, "S": small}
