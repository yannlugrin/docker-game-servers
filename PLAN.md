# Root track — implementation plan

Track: root (repository-wide work — foundation and harness, CI, shared
documentation). Step prefix: `step-NNN`. Governed by `CLAUDE.md`; image
tracks: `steamcmd/PLAN.md`, `project-zomboid/PLAN.md`.

## Plan conventions (all tracks — image plans reference this header)

- Every step entry carries: **Objective**, **Spec sections** (its review
  checklist), **Deliverables**, **Dependencies** (cross-track ones named
  explicitly, `needs step-xx-NNN`), **How to test** (the operator's
  manual test), and **Status**: `pending` / `in progress` /
  `awaiting test` / `done`.
- Steps are small enough for the operator to test alone. **Exception,
  decided at bootstrap: step-000 is deliberately composite** — its parts
  gate nothing separately testable; the fresh-clone test is the gate,
  the enforcement probes report in the step summary, and the CI workflow
  is verified at first push. Never a granularity finding.
- **Boundary-crossing cost rule**: when a step's test crosses rule 9's
  boundary (CLAUDE.md), the entry states that it does, what it costs,
  and how to clean up afterwards. Local builds and smoke runs are free
  (a PZ build downloads several gigabytes — slow, costless); anything
  that publishes is not (GHCR release tags are immutable and retained
  forever, root §7).
- Exactly one step in progress repository-wide (rule 6). Step numbers
  freeze at `in progress`; `pending` steps may be renumbered with a
  reference sweep. Completed steps compact to their outcome (rule 3).

## Milestone R1 — Foundation

### step-000 — Repository foundation (composite)

- **Objective**: everything the workflow itself needs, before any
  project code.
- **Spec sections**: root §2.6 (registry/CI facts), §2.8 (schedule
  staleness, for the CI skeleton's guard), §9 (documentation lint
  applies to load-bearing documents); CLAUDE.md rules 2, 3, 4, 9.
- **Deliverables**:
  - `.gitignore` written with rule 5 in mind: local test-state roots and
    volumes (game saves, Steam-downloaded content from smoke runs);
    `.env` and any local credential file; steamcmd and image-build
    caches; `.claude/reviews/` (reviewer templates assume it is
    ignored); `CLAUDE.local.md`.
  - Pinned base dependencies installable through **one documented setup
    command**.
  - The rule 2 harness: *check* (whole working tree well-formed,
    untracked included, gitignored paths and `.claude/spec-work/`
    excluded by path), *test*, *verify* — documented commands, native
    mechanism of my choice, runnable by the operator; pre-commit hooks
    running the same harness.
  - **GitHub Actions workflow running the same harness** (origin is
    `github.com/yannlugrin/docker-game-servers`; images will publish to
    `ghcr.io/yannlugrin`): check and test as separate jobs once both
    exist; toolchain cached, plus a periodic uncached run proving fresh
    setup (its `schedule` trigger sits under the same staleness guard
    root §8 gives the refresh). Treated as **verified only at first
    authorized push** (step-002).
  - Lint coverage over the governance documents themselves (the
    specifications, plans, decision logs, CLAUDE.md, README) —
    configured to them as they already are; the lint bends to read-only
    documents, never the reverse.
  - **`.claude/settings.json` extended** (auto memory stays off) with a
    permission-and-hook baseline enforcing rule 9, **proposed to the
    operator for review**: allow the harness, the setup command, the
    local container lifecycle and free remote reads, and the additive
    and read-only subset of local git (add, commit, status, diff, log,
    show, rev-parse, describe, tag listing, annotated tags); **ask** for
    everything rule 9 gates (`git push` included) and for
    state-destroying local git stated as a classifier — anything that
    rewrites history (`commit --amend`, `rebase`), moves or deletes tags
    or branches, or destroys uncommitted/untracked work (`reset --hard`,
    `git clean`) — with no allow pattern silently admitting one (a bare
    `git commit` allowance admits `--amend`); **deny** reserved for what
    has no authorized use at all, each named in the proposal; a guard
    hook where a pattern cannot express the rule (e.g. `gh api`
    read/write split).
  - Workflow tooling instantiated from `.claude/spec-work/handoff/
    assets/`: skills `orient`, `resume-step`, `handover-step`,
    `approve-step`; agent `step-reviewer`. Every placeholder filled with
    real commands and paths per CLAUDE.md's Tooling-templates block; no
    instantiated file names a non-adopted skill/agent except via the
    documented not-yet-adopted list. Adoptions logged.
  - **One-time enforcement probes**, results reported in the step
    summary: the settings baseline actually binds; skill-frontmatter
    restrictions actually bind (a separate mechanism); the
    `autoMemoryEnabled` key is honored by the running version; if
    `.claude/rules/` path-scoped rules are used, proof they load.
- **Dependencies**: none.
- **How to test**: fresh clone → documented setup command → check
  command → one commit — all green. Local and free.
- **Status**: pending.

### step-001 — LICENSE verification

- **Objective**: verify the existing root `LICENSE` satisfies root §9
  (MIT; licenses recipes and tooling, not game content — that framing
  belongs to documentation steps).
- **Spec sections**: root §9 (LICENSE), §5.8 (license annotation value).
- **Deliverables**: verification recorded (decision entry only if a
  change is needed — a non-MIT or malformed license is a question for
  the operator, not a silent fix).
- **Dependencies**: none.
- **How to test**: read `LICENSE`; confirm it is stock MIT with the
  expected copyright holder. Free.
- **Status**: pending.

### step-002 — First push and harness-CI verification

- **Objective**: the harness CI of step-000 proven live on GitHub.
- **Spec sections**: root §2.6, §2.8; CLAUDE.md rule 9 (push is gated).
- **Deliverables**: pushed `main`; harness workflow green on GitHub;
  Actions settings confirmed known-good by the operator — Actions
  enabled, and the workflow-token permission model for GHCR publishing
  **verified against GitHub's current behavior, not assumed** (the
  `packages: write` mechanism is a premise the specification does not
  state; whatever step-004's publishes actually need is what gets
  confirmed here, while we are looking); any divergence between local
  and CI harness runs fixed.
- **Dependencies**: needs step-000 done. **External prerequisite**:
  operator authorizes the push and confirms the Actions settings.
- **How to test**: **crosses rule 9's boundary** — one `git push`
  (operator-authorized; publishes nothing to GHCR, the repository is
  already public). Cost: none beyond visibility of the pushed files.
  Cleanup: none needed. Observe: the workflow runs and is green.
- **Status**: pending.

## Milestone R2 — CI and publication

### step-003 — Build-and-smoke-test workflow (no publish)

- **Objective**: pushes and PRs touching an image's sources build that
  image and run its smoke test, publishing nothing.
- **Spec sections**: root §8 (build-and-smoke without publishing; smoke
  gate definition), §2.6 (Docker Hub rate-limit decision: mirror or
  authenticated base pulls — decided and logged here).
- **Deliverables**: workflow building the builder and the PZ image and
  running the PZ smoke suite and builder gate script; the base-image
  pull mitigation decided (decision entry; Docker Hub credential listed
  as an external prerequisite only if the authenticated-pull option is
  chosen).
- **Dependencies**: needs step-002 done, `step-sc-001` done,
  `step-pz-007` done (smoke suite exists).
- **How to test**: **crosses rule 9's boundary** — an operator-
  authorized push of a branch/PR touching image sources. Cost: CI
  minutes and a multi-gigabyte Steam download on the runner; publishes
  nothing. Cleanup: delete the test branch (operator or authorized).
- **Status**: pending.

### step-004 — Publish workflow (on-demand)

- **Objective**: the manually triggered build-and-publish flow of
  root §8, with §7's tag discipline enforced.
- **Spec sections**: root §7 (tag scheme, immutability, dev namespace,
  moving pointers, publication-order "newest"), §8 (on-demand builds,
  smoke gate on every game publish, builder gate), §5.8 (labels the tags
  rest on), §2.6.
- **Deliverables**: workflow publishing a chosen image — builder: new
  date tag (`YYYYMMDD`, `.1` ordinal on same-day rebuilds) + `latest`;
  game: `<version>-rN` computed against what the registry holds, moving
  `<version>` and `latest` pointers by publication order; **a publish
  that would overwrite an existing immutable tag fails the job**; smoke
  gate before any game publish, steamcmd metadata-query gate before any
  builder publish; dev-namespace publishing path for tests, never
  advancing `-rN`.
- **Dependencies**: needs step-003 done.
- **How to test**: **crosses rule 9's boundary** — operator-authorized
  workflow dispatches publishing **dev-namespace tags only** (root §7:
  mutable, prunable, no release promises). Cost: GHCR storage for dev
  tags. Cleanup: delete dev packages/tags (a GHCR package operation —
  operator or authorized). The overwrite guard is exercised against a
  dev tag.
- **Status**: pending.

### step-005 — First release publishes and visibility flips

- **Objective**: `steamcmd` and `project-zomboid` released: first date
  tag and first `-rN`, publicly pullable.
- **Spec sections**: root §7, §8 (first publish is not fully automatic),
  §2.6.
- **Deliverables**: both packages published and public; anonymous pull
  verified from a clean environment; per-image READMEs live as GHCR
  pages (needs `step-sc-002` and `step-pz-008` done).
- **Dependencies**: needs step-004 done, `step-sc-002` done,
  `step-pz-008` done. **External prerequisite**: the operator flips each
  GHCR package to public visibility (one-time, per package) and
  authorizes the release dispatches.
- **How to test**: **crosses rule 9's boundary** — release publishes are
  immutable and retained forever (root §7); this is the deliberate first
  spend of that budget. Cost: permanent public tags. Cleanup: none — by
  design, release tags are never deleted. Observe: `docker pull` of both
  images anonymously succeeds; labels match §5.8.
- **Status**: pending.

### step-006 — Scheduled update detection

- **Objective**: the periodic buildid comparison of root §8, publishing
  automatically on any change.
- **Spec sections**: root §8 (update detection), §2.3 (buildid), §5.8
  (buildid label as comparison source), §7 (version vs revision mapping).
- **Deliverables**: scheduled job comparing each game's current Steam
  buildid against the newest published **release** image's label
  (never a dev tag); any change → build and publish per §7 (new version
  tag or revision bump) with no human action; a comparison that cannot
  be established (Steam unreachable, unparseable label) **fails the job
  loudly**, never "no change".
- **Dependencies**: needs step-005 done (a release image with a buildid
  label must exist to compare against).
- **How to test**: **crosses rule 9's boundary** — operator-authorized
  dispatch of the detection job. Steady case: no change → job green with
  an explicit "compared, equal" result; failure case: exercised by
  pointing the comparison at a dev tag lacking the label in a test run —
  job fails loudly. A real publish only happens if Steam shipped an
  update; that publish is a legitimate release. Cleanup: none.
- **Status**: pending.

### step-007 — Scheduled refresh and staleness guard

- **Objective**: the one flow that keeps published images patched:
  fresh builder date tag → pin advance → all game images rebuilt.
- **Spec sections**: root §8 (scheduled refresh, staleness check), §2.8
  (idle-schedule deactivation), §3.1 (the pin only moves by this act),
  §7 (tags of the rebuilt images).
- **Deliverables**: refresh workflow — publishes a builder date tag,
  advances the pinned builder reference the game builds use, rebuilds
  every game image (tags per §7: version moved → new `-r0`, else
  revision bump); the pin advance final **only when game rebuilds
  succeed**, else the previous working pin is left/restored; the
  **in-repo staleness check** running on every CI trigger and failing
  loudly when the refresh is overdue (blind spot documented per §8;
  external watchdog stays deferred, root §10.7).
- **Dependencies**: needs step-005 done. (step-006 and step-007 are
  order-independent between themselves.)
- **How to test**: **crosses rule 9's boundary** — operator-authorized
  dispatch of the refresh. Cost: one new builder date tag and one
  revision bump per game — legitimate releases, retained. Cleanup: none.
  The failure path (pin restored) is exercised in the no-publish
  workflow with a deliberately broken rebuild, not against the registry.
- **Status**: pending.

## Milestone R3 — Shared documentation

### step-008 — Repository README consumer content

- **Objective**: the root README's consumer half per root §9: project
  scope, image inventory, the §5 conventions stated once (per-image docs
  link here), platform-neutral throughout.
- **Spec sections**: root §9 (repository README), §3.3, §1; §5 (the
  conventions being restated).
- **Deliverables**: root `README.md` extended (its bootstrap file map
  and reviewer sections stay); links to per-image READMEs.
- **Dependencies**: needs `step-sc-002` and `step-pz-008` done (an
  inventory needs images and their docs to point at).
- **How to test**: read it; markdown/prose lint green. Free.
- **Status**: pending.

### step-009 — Contributor guide for adding a game

- **Objective**: the root §9 contributor guide: the §5 checklist a new
  game image walks through, starting with the per-game specification to
  write first (§6), plus the track/plan mechanics a new game registers.
- **Spec sections**: root §9 (contributor guide), §6, §10.5.
- **Deliverables**: `docs/adding-a-game.md` (human documentation —
  `docs/`, never `.claude/docs/`), linked from the root README.
- **Dependencies**: needs step-008 done (it links into the conventions
  section rather than restating it).
- **How to test**: read it; walk one §5 convention through the checklist
  and confirm the checklist would have caught its absence. Free.
- **Status**: pending.

## Coverage and exclusions

Every section of both specification documents maps to a step (root plan
above; `steamcmd/PLAN.md` covers root §4; `project-zomboid/PLAN.md`
covers `project-zomboid/SPECIFICATIONS.md`). Explicitly excluded from
this pass, with reason:

- **Root §10 (Future Considerations, 10.1–10.7)** — deferred by the
  specification itself; the standing obligation ("nothing may preclude
  them") binds design in every step but builds nothing now. §10.7's
  external watchdog: deferred, needs an operator-supplied service.
- **Root §11 (Non-Goals)** — conscious renunciations; nothing to build.
- **PZ §1's Build 41 non-goal** (`legacy41`) — out of scope by
  specification.
- Root §2 is constraints, not buildable scope; each fact is named in the
  step(s) it drives.

## External prerequisites (operator-only, listed at first need)

1. **step-002**: authorize the first `git push`; confirm GitHub Actions
   enabled and workflow token allowed `packages: write`.
2. **step-003**: a Docker Hub credential **only if** the §2.6 mitigation
   decided there chooses authenticated base-image pulls (no Steam
   credential is ever needed — installs are anonymous; the repository is
   already public, which root §2.8's schedule behavior rests on).
3. **step-004**: authorize dev-namespace test publishes; authorize
   cleanup of dev tags afterwards.
4. **step-005**: flip GHCR package visibility to public for `steamcmd`
   and `project-zomboid` (one-time each); authorize the release
   dispatches.
5. **step-006/007**: authorize the verification dispatches.

## Open questions and risks (bootstrap; operator to rule)

1. **Fact-verification step granularity** (`step-pz-001`): PZ §2's open
   facts are verified in one exploratory step feeding several design
   steps. If its findings force design changes mid-track (items d, e, g,
   k, l come back to you by rule 1), later PZ steps may be renumbered —
   expected, but worth knowing up front.
2. **Version-string extraction (PZ §2 item e)** decides the entire tag
   scheme (root §7 fallback to buildid-derived tags). Flagged as the
   single open fact with the widest blast radius (tags, workflows,
   README) — resolved in `step-pz-001`, before any workflow that names
   tags is written.
3. **CI runner disk**: a PZ build needs several gigabytes on hosted
   runners; assumed to fit standard GitHub-hosted runners. Verified at
   step-003; if wrong, the mitigation (cleanup steps, larger runner) is
   a decision at that step.
4. **Smoke-test Steam dependency in CI**: root §8 permits it, but
   flakiness of Steam endpoints on shared runners may argue for retries
   or a documented rerun policy — decided at step-003 if observed.
5. **Ordering choice made here**: per-image READMEs (`step-sc-002`,
   `step-pz-008`) land before first publish (step-005) so the GHCR
   pages are never empty — at the cost of documenting an unpublished
   image. Say the word if you prefer publishing first.
