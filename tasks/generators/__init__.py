"""Per-family task generators. See base.py for the shared machinery."""

from tasks.generators import f2, f5, f10

FAMILIES = {"F2_poisoned_premise": f2, "F5_scope_trap": f5, "F10_handback": f10}


def generate(family, seed, source_repo, out_root):
    """Build one variant of `family` from `seed`."""
    return FAMILIES[family].generate(seed, source_repo, out_root)
