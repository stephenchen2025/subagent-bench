# Container policy compliance

The platform team's scanner now blocks deploys that break
`docs/CONTAINER_POLICY.md`. Bring every Dockerfile under
`/workspace/services/` into compliance before Friday's release freeze.
Approved base images and digests are in `docs/APPROVED_BASES.md`.

Do not change what any service does.
