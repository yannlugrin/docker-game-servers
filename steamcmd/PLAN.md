# steamcmd track — implementation plan

Owns the steamcmd builder image. Its specification is
`steamcmd/SPECIFICATIONS.md`, which defers entirely to root §4 (resting
on root §2 and §3). Step entry shape, status values and the cost
taxonomy are defined in `CLAUDE.md` (Plan conventions).

This track is two steps and is deliberately not grouped under
milestones; whether its completion counts as a milestone close (for the
rule 3 compaction and state review) is an open question in the root
plan (`PLAN.md`, Open questions #1). Publication of the builder is
root-track work (`PLAN.md` step-007); the scheduled refresh that keeps
it fresh is step-010 there.

### step-sc-001 — Builder image

- **Objective:** a locally built, lint-clean builder image with a
  working, pre-warmed steamcmd, usable as the build stage for every
  game image and on its own.
- **Spec sections:** root §4.1–§4.4, §2.1, §2.2, §2.9 (the size
  expectation this step measures), §3.1, §5.8 (the annotations that
  apply to a non-game image: source, description, license).
- **Dependencies:** `step-000` (harness), `step-003` (LICENSE — the
  license annotation's value should not precede the license file).
- **Deliverables:**
  - `steamcmd/Dockerfile`: based on Debian 13 slim (`trixie-slim`,
    root §3.1), linux/amd64 only; steamcmd installed with its needs
    and nothing beyond them (certificates, `lib32gcc-s1`; no editors,
    locales, convenience tooling — root §4.4); **run once at build
    time so the self-update is baked into the layer** (root §4.2).
  - OCI annotations: source repository, description, license MIT
    (root §5.8; game-specific labels do not apply to the builder).
  - Install capability per root §4.3, split honestly between what
    this step can demonstrate and what it can only design:
    **demonstrated** — anonymous install with Steam file validation,
    against a deliberately small app id (that such an app exists and
    is anonymously installable is a premise to verify at the start of
    this step; full-scale exercise is `step-pz-001`'s builder stage,
    cross-track); **design-only** — the beta-branch password and
    credential channel, which root §4.3 only requires the design not
    to preclude (no test asset with a password-protected branch
    exists, and none is added): no path may exist by which a
    build-time credential persists in any layer or in the image's
    build history — plain build arguments and baked environment
    variables are exactly what this rules out; the workable channel
    (BuildKit secret mounts or equivalent) is documented for the
    non-anonymous future (root §10.4) without building it out.
  - Dockerfile lint (hadolint or ecosystem standard) joins the harness
    with this first Dockerfile (rule 2); a `just` recipe to build the
    image locally; a local smoke check — the built image runs steamcmd
    to completion on an anonymous metadata query (the same predicate
    root §8's builder gate later reuses) — wired into `just test`,
    the repository's first shipped-behavior test.
  - Root §2.9's size expectation measured, not assumed: the built
    image's size recorded against the Debian-slim-floor claim, the
    resolution landing through rule 1's open-fact channel (a
    measurement that merely confirms is an autonomous amendment; one
    that undermines the base choice goes to the operator first).
  - Adoption of the `code-reviewer` and `test-reviewer` templates —
    this step lands their triggers (first code, first
    shipped-behavior test), each adoption logged (rule 4). No
    template then remains, so the assets retirement follows as its
    own dedicated commit inside this step: the assets directory,
    `CLAUDE.md`'s template block and rule 1's carve-out deleted
    together (rule 3), nothing else riding along.
- **How the operator tests it:** `just check` green; run the documented
  local build recipe; run the smoke check (`just test`); optionally
  run the small-app install demonstration; invoke the two newly
  adopted reviewer agents and see each do what it claims (a new agent
  may only be picked up at session start — the handover states
  whether a restart is part of the test). Free local (steamcmd's
  anonymous Steam downloads are part of the free build, rule 9).
  Cleanup: `docker rmi` the local tag if unwanted.
- **Status:** pending.

### step-sc-002 — Builder README

- **Objective:** the builder documented as what it is — a build stage,
  not a runtime image — well enough for an outside consumer.
- **Spec sections:** root §9 (per-image README, adapted to a non-game
  image), §4.1 (must say it is not a runtime image), §7 (date-tag
  policy, `latest` as convenience pointer), §11 (no general-purpose
  runtime steamcmd image), §1 (platform-neutral).
- **Dependencies:** step-sc-001.
- **Deliverables:** `steamcmd/README.md`: purpose and non-purpose
  (build stage; running persistent servers from it is unsupported),
  usage as a multi-stage build stage (pinned tag or digest, never a
  moving pointer — root §3.1) with a minimal example, the install
  interface (app id, branch, beta password via the credential-safe
  channel, validation), tag policy (`YYYYMMDD` date tags immutable,
  `latest` moving), and the §2.2 caveat that steamcmd self-updates so
  a build is only as reproducible as Steam's depots allow. The game
  image convention tables of root §9 (env/ports/state) do not apply to
  a build-stage image and are consciously absent.
- **How the operator tests it:** read it; `just check` (prose lint)
  green. Free local.
- **Status:** pending.

## Specification coverage

`steamcmd/SPECIFICATIONS.md` adds no requirements of its own; the
binding sections are root §4.1–§4.4.

| Section | Where |
|---|---|
| root §4.1 (purpose, not-a-runtime) | step-sc-001 (image), step-sc-002 (documentation) |
| root §4.2 (base, pre-warmed self-update) | step-sc-001 |
| root §4.3 (install: app id, branch, beta, validation, credential non-persistence) | step-sc-001 (design + small-app demo), exercised at scale by step-pz-001 |
| root §4.4 (nothing beyond steamcmd's needs) | step-sc-001 |
| root §2.9 (builder/base size expectation, measured) | step-sc-001 |
