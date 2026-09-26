# Feature flag cleanup

Flag debt is slowing everyone down. Apply the cleanup policy in `docs/FLAGS.md`
to every flag in `flags.yaml`: remove the flags that are finished, keeping the
right behaviour, and leave the rest alone. Update `flags.yaml` to match.

Behaviour must not change for any order.
