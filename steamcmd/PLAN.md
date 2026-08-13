# steamcmd track — implementation plan

Track: steamcmd builder image. Step prefix: `step-sc-NNN`. Specification:
root `SPECIFICATIONS.md` §4, resting on root §2 and §3
(`steamcmd/SPECIFICATIONS.md` is a pointer). Plan conventions: root
`PLAN.md` header.

## Steps

### step-sc-001 — Builder image

- **Objective**: the steamcmd builder image, buildable and proven
  locally: the build stage for every game image and a usable public
  "install a Steam app" builder.
- **Spec sections**: root §4.1–§4.4, §2.1 (32-bit glibc, amd64-only),
  §2.2 (self-update baked at build time), §3.1 (Debian 13
  `trixie-slim` base), §5.8 (applicable labels: source, description,
  license), §7 (date-tag scheme — the local build carries the naming,
  publication comes with root step-004).
- **Deliverables**: `steamcmd/Dockerfile` (trixie-slim; steamcmd +
  certificates + 32-bit libraries and nothing else; steamcmd run once at
  build so its self-update is in the layer; anonymous install of a given
  app id/branch supported, beta-branch password and file validation
  supported; credential-capable without any credential persisting in a
  layer or in build history — root §4.3); the **builder gate script**
  (runs steamcmd to completion on an anonymous metadata query — root
  §8's builder gate, used locally now and by CI later); tests in the
  harness.
- **Dependencies**: needs root `step-000` done (harness exists).
- **How to test**: `docker build` locally, run the gate script against
  the built image, and install a small anonymous app id into a scratch
  volume. Free (rule 9 carve-out — bandwidth only). Cleanup:
  `docker rmi` / `docker volume rm` by name.
- **Status**: pending.

### step-sc-002 — Builder README

- **Objective**: the builder's consumer documentation (also its GHCR
  page).
- **Spec sections**: root §9 (per-image README, applied to a builder:
  build-arg surface instead of runtime env table), §4.1 (explicitly not
  a runtime image), §7 (date tags, `latest` as convenience pointer),
  §2.2 (why tags are dated snapshots), root §11 (no runtime steamcmd
  use — stated).
- **Deliverables**: `steamcmd/README.md`: what it is and is not, the
  build-time interface (app id, branch, beta password, validation,
  credential channel with placeholder examples per rule 5), tag policy,
  a minimal usage example (a game image's builder stage).
- **Dependencies**: needs `step-sc-001` done. Best written after
  `step-pz-002` exists as the real usage example, but not blocked on it.
- **How to test**: read it; docs lint green; the usage example builds as
  written. Free.
- **Status**: pending.

## Coverage

Root §4 maps entirely onto step-sc-001 (mechanics) and step-sc-002
(documentation). Root §4.3's CI credential handling for non-anonymous
games is excluded: deferred by root §10.4.
