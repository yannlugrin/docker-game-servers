# Implementation plan — root track

The root track owns what lives at the repository root or in a shared
directory: the foundation and harness, CI in `.github/workflows/` — **all
publication, including of images another track owns** — and the
repository-wide documentation of root §9 (this repository's README, the
contributor guide). The criterion, and what it deliberately excludes, is
`DECISIONS.md` D-005.

Images live on their own tracks: `sc` (the steamcmd builder, `steamcmd/`) and
`pz` (Project Zomboid, `project-zomboid/`).

`§N` references point to the root `SPECIFICATIONS.md`; `PZ §N` to
`project-zomboid/SPECIFICATIONS.md`. The step-entry shape, the status
vocabulary and the compaction-on-approval rule live in
`.claude/docs/workflow.md` §1.

## How to read this plan

- Steps are ordered by dependency. The order and headings define the
  sequence; numbers are identifiers, frozen when a step enters
  `in progress`, never reused.
- Cross-track sequencing is stated per step ("needs `step-pz-013` done"),
  never inferred from a global order — and the same holds within a track:
  a step's own dependency line names what it needs, never its position.
- Exactly one step is in progress repository-wide, whichever track it
  belongs to.
- Costs are stated per test. A test that crosses the rule-9 action boundary
  says so, what it costs, and how to clean up.
- **Paths: a deliverable inside the active track's directory needs no path;
  anything outside it names its path.** This track's directory is the
  repository root, so its deliverables name paths — `.github/workflows/`,
  `docs/adding-a-game.md`, `justfile`.
- **Deliverables state what a step decides or builds beyond the
  specification, and cite the sections for the rest** — the session routine
  reads those sections anyway, and a copy of a read-only document can only
  go stale. The six foundation steps are the deliberate exception: they carry
  their prescriptions in full, because the bootstrap prompt that stated them
  is consumed once and a later session has only this plan.

---

## Milestone 1 — Repository foundation

Six steps, drawn by what a working repository needs rather than by cost
class. CI is the first step that leaves this machine, which is why it comes
last *within* the foundation — not a reason to move it into a later
milestone grouped by cost. The project is not bootstrapped until its CI has
run green.

**They are separate steps because each is separately testable, and because
they must not all be built before the operator has seen any of them:** a
foundation delivered whole arrives with everything already written, and the
operator's first correction then costs the lot.

The bootstrap prompt prescribed four steps here and invited a further split
where one was too big for a single gate, or cut in the wrong place. The cold
review of this plan found two such cases and they are split below: the
harness mechanism is separated from the document lint it carries
(`step-000`/`step-001`), because tuning prose lint to 2,700 lines of
read-only specification is a high-iteration task that should not hold a
green harness hostage; and the workflow tooling is separated into reviewer
agents then session rituals (`step-003`/`step-004`), because the rituals
reference the agents — so agents must come first or the reference dangles —
and because `step-003`'s probe has a pre-committed unfavourable branch that
rewrites every agent body. The permission baseline (`step-002`) is
deliberately **not** split: the prompt requires it proposed for review *as a
whole*, and its gate is one judgement.

**No component-track step starts before this milestone closes.** The `sc` and
`pz` tracks both gate on `step-005`, stated in their dependency lines and in
every cross-track table: `step-sc-001` builds images and runs steamcmd
downloads, which is the surface `step-002`'s guard exists to gate, and it
hands over through the rituals `step-003` and `step-004` provide.

Closing this milestone triggers the whole-state review and then the
memory-compaction pass (`CLAUDE.md`, rule 3).

### step-000 — The harness skeleton, local only — `done`

- **Outcome (approved 2026-08-17, tag `step-000`):** the repository checks
  itself from a fresh clone. `just setup` installs a pinned toolchain into
  `./.venv` and wires the commit hooks; `just check [scope]` is one entry
  point taking a scope, passing its file list explicitly so untracked files
  are seen without ever writing to the index; `just test` states that no
  behaviour of this repository's own exists yet; `just verify` runs both.
  `.pre-commit-config.yaml` is the single declaration both `just check` and
  the commit hook run, with `.claude/spec-work/` and `.claude/refs/` excluded
  by path. Nothing it runs rewrites a file. D-006 settles the venv bootstrap
  and why `just` is a prerequisite rather than a pinned dependency; D-007 what
  `check` covers — three well-formedness families plus hygiene guards admitted
  on blast radius, with three hook behaviours measured rather than assumed;
  D-008 adopts `detect-secrets`, closing the absence of any mechanical guard
  for rule 5 that a grep of all three plans had exposed. First
  `.claude/docs/` file: `environment.md`. Detail in git history between
  `a49f8ed` (the last pre-step commit — `step-000` is the first step tag) and
  tag `step-000`.

### step-001 — The governance and prose lint — `done`

- **Outcome (approved 2026-08-17, tag `step-001`):** the documents are linted
  like the code they effectively are — `pymarkdown` v0.9.39 for structure,
  `codespell` v2.4.3 for spelling, both pinned by revision and both
  report-only, which now holds for the whole harness: no hook rewrites
  anything, so a failing `check` cannot edit a read-only specification.
  Configured to the documents as they already are, in three bends (D-009);
  with those, every other rule of both tools reports zero across the thirteen
  governance and human-facing documents. Two bends were measured rather than
  reasoned — `md013`'s table exemption is inert until the `markdown-tables`
  extension is enabled, since CommonMark has no tables, and `--config` must be
  explicit because 0.9.39 does not auto-discover `.pymarkdown.yaml`. The
  `.claude/docs/` note this step owed **for any repairing hook** is
  deliberately absent: none was adopted, so the condition never fired. One
  read-only specification line was rewrapped on the operator's authorisation,
  no word changed, retiring a fourth bend. Detail in git history between tags
  `step-000` and `step-001`.

### step-002 — The permission and hook baseline — `done`

- **Outcome (approved 2026-08-17, tag `step-002`):** rule 9's boundary is
  enforced mechanically and every mechanism was measured rather than assumed.
  `.claude/hooks/bash_guard.py` is instantiated from the template with **only
  its `REGISTRY` edited**: `git` and `docker` keep the template's rules, `gh`
  is expressed as grants because rule 9 rules API reads free and gates writes,
  `steamcmd` as a vocabulary grant; `just` and `pre-commit` get no entry,
  because what keeps them safe is rule 2's no-gated-act invariant, which lives
  outside the guard. Gated twice: `--liveness` in the commit path on every
  commit (`always_run`, since a rename would skip a path-keyed hook), and
  `--selftest` as `just test` — 133 registry cases, 174 engine cases, 57/57
  rules and grants covered. The operator applied the settings baseline (D-010):
  broad allow per registry tool, no `ask` for anything the guard gates, an
  eight-entry `deny` backstop, `defaultMode: acceptEdits`. Python arrived as a
  check family (`ruff check` only — `ruff-format` rewrites and would reflow the
  vendored guard), and governance well-formedness gained
  `scripts/check_settings_hooks.py`.
  **Measured, and three findings changed what is believed:** a hook **fails
  open** — with the guard non-executable a refused command ran unprompted;
  installing settings does **not** activate a hook in the session that wrote
  them; and both mode-dependent behaviours differ between `auto` and
  `acceptEdits`, including that **the implementer can edit its own permission
  boundary** under what ships. This baseline stops mistakes, not a determined
  agent. Open and deliberately not applied: the hardening in
  `.claude/docs/permissions.md` §7. Detail in git history between tags
  `step-001` and `step-002`.

### step-003 — The reviewer agents — `done`

- **Outcome (approved 2026-08-17, tag `step-003`):** three agents exist at
  `.claude/agents/` — `step-reviewer`, `state-reviewer`, `optimize-memory` —
  so the milestone close at `step-005` finds its passes already built rather
  than improvising them (D-011). `code-reviewer` and `test-reviewer` stay
  unadopted, their triggers being genuinely absent, and remain on
  `CLAUDE.md`'s not-yet-adopted list so a ritual citing them does not dangle.
  Four template departures are logged: governance placeholders resolve at
  invocation through a track table, with the track **named at spawn** for the
  two close passes; `optimize-memory`'s budget follows D-002's 280/~250, a
  template enumeration narrower than its rule losing to the rule; the
  architecture vocabulary is seeded from the specification and says so; and
  `tools:` was left as set after checking this build's inventory.
  **Both probes were run, not argued** — `.claude/docs/agents.md` carries them
  with version, method and re-measure recipe: `CLAUDE.md` **does** reach a
  subagent, arriving as project instructions before its first tool call and
  never fetched with a tool, so **the pre-committed inlining branch does not
  fire**; and `tools:` **binds by omission**. Recorded with the limit that
  outlives the result — `tools:` restricts which tools exist, not what they
  do, and `Bash` writes, so a reviewer's read-only discipline rests on its
  prose. Also measured: a new agent loads only at session start, so no step
  can test an agent it creates. The governance **frontmatter parse** family
  arrived with the first files of its class, deliberately narrow, and
  `pymarkdown` gained the `front-matter` extension. Detail in git history
  between tags `step-002` and `step-003`.

### step-004 — The session rituals — `done`

- **Outcome (approved 2026-08-18, tag `step-004`):** the four rituals every
  later step runs exist at `.claude/skills/<name>/SKILL.md` — `orient`,
  `resume-step`, `handover-step`, `approve-step` — so orientation, resumption,
  handover and close stop being improvised (D-012). Where `step-003` had a
  selection question, this one did not: all four triggers were already firing.
  Six template departures are logged, two of them load-bearing: the governance
  placeholders resolve at invocation **with no track table copied in**, a skill
  executing in the session that has just read `CLAUDE.md`'s map; and `orient`'s
  steps 1–2 were rewritten from the template's single-track shape to the
  multi-track routine, a narrower enumeration losing to the rule it executes.
  A defect the harness could not see drove the second half: four rituals
  pointed at `.claude/docs/agents.md` §5 where the section is §4 — written from
  the numbering as it stood before a section was inserted ahead of it, in the
  same commit. `scripts/check_section_references.py` (D-013) now asserts a
  backticked path, its §N **and** a quoted title where the class requires one;
  the first draft checked the number only and **passed the defect as
  committed**, which is the whole argument for the title. It covers 8 of 29
  pointers, and requiring titles everywhere is deferred to the operator. The
  `agent-frontmatter` family was extended to `.claude/skills/*/SKILL.md`, the
  first files of its class, proven red on both failure modes first. **Measured:**
  a skill created mid-session is not loaded until the session restarts, the same
  as an agent — which shapes every later step's test instructions. The
  pre-handover review found nine, seven applied: the heaviest were
  `approve-step` transcribing some fifty lines of `.claude/docs/workflow.md` §1,
  §5 and §3 and then naming `CLAUDE.md` as the tie-breaker — a document emptied
  of plan conventions at `step-002` — and `resume-step` claiming `orient`'s
  orientation without performing it, leaving a resumed session able to work from
  no specification. Detail in git history between tags `step-003` and
  `step-004`.

### step-005 — The same harness on the forge — `done`

- **Outcome (approved 2026-08-20, tag `step-005`):** the harness runs on the
  forge, and the run that proved it found a defect nothing local could.
  `.github/workflows/ci.yml` reuses the entry points rather than restating a
  check — `just setup`, then `just check` and `just test` as two gates from
  one matrix definition, so CI and a local run cannot disagree about green.
  Every run is a clean checkout doing the documented setup in full, which is
  how a fresh setup is proven without inventing the schedule §2.8 forbids.
  D-014 carries the shape: triggers narrowed to `main` plus pull requests and
  dispatch, one run per ref with `main` exempt from cancellation,
  `contents: read`, `ubuntu-24.04` pinned, and **no cache** — 474 MB of hook
  environments against a 37 s cold setup, measured, implemented, then dropped
  on the operator's ruling before the first run rather than after. D-015
  fetches `just` from its own release checksum-verified, rejecting both a
  third-party action and `apt` (Ubuntu freezes universe, so `ubuntu-24.04`
  cannot offer the pinned version, and `just --fmt` is version-sensitive);
  actions are SHA-pinned, and `.github/dependabot.yml` is the updater without
  which a pin only looks maintained. D-016 adds actionlint as the
  workflow-validation family, arriving with the first workflow file and with
  its two ambient integrations off so CI cannot be stricter than a local run;
  D-017 settles the first `detect-secrets` false positive inline.
  **The first run failed, on exactly the divergence D-014 had accepted:** the
  vendored guard calls `PurePath.full_match`, added in Python 3.13, and
  `ubuntu-24.04` ships 3.12.3 — `just check` passed and `just test` died,
  because only the guard needs it, and this machine's 3.14.4 could never have
  shown it. The floor was declared nowhere; CI now installs 3.14 and the
  requirement is stated in `README.md` and `.claude/docs/environment.md` §1.
  Patching the guard was deliberately not done and reported instead, its
  `step-002` instantiation having changed only its `REGISTRY`. Green at
  1m14s and 1m03s. `.pre-commit-config.yaml`'s commentary was cut from 238
  lines to 119 in the same step, the reasoning living in the decision log.
  Detail in git history between tags `step-004` and `step-005`.

*Nothing in this milestone is exempt from the small-step rule. If any of
these six is still too big for a single test — **or cut in the wrong place
for this project**, which is the harder failure to notice, since a step can
be the right size and still draw its seam badly — it is split or re-cut in
this plan rather than defended.*

---

## Milestone 2 — Publication and automation

Everything root §7 and root §8 ask for, on both images: the builder's publish
workflow, the smoke gate that stands in front of every game-image publish, the
release stream and its never-reuse enforcement, update detection, and the
refresh that is the only path by which security patches reach baked images.

CI lives in `.github/workflows/`, a root directory, so publication is
root-track work even when what it publishes belongs to another track
(`DECISIONS.md` D-005). The builder image and its README are the `sc` track's
(`steamcmd/PLAN.md`); the game image is the `pz` track's.

Ordered so nothing goes live before its day-two operations exist: the smoke
gate is built and proven locally before any workflow can publish a game image,
the gate is wired into the publish path before the first publish, and the
consumer documentation exists before the first pinnable release tag.

### step-006 — Builder publication on CI — `pending`

- **Objective.** The builder published to GHCR by CI, gated, with §7's tag
  scheme.
- **Spec sections implemented.** §7 (builder date tags, the ordinal suffix,
  moving `latest`, amd64-only with no architecture suffix), §8 (on-demand
  builds; the **builder's own minimal gate** — steamcmd must run to
  completion on an anonymous metadata query before the date tag is pushed),
  §2.6 (GHCR; the per-package visibility flip; the Docker Hub anonymous-pull
  rate limit, **decided deliberately here** rather than after the first
  failed build), §5.8.
- **Depends on.** `step-005`; `step-sc-001` and `step-sc-002` done (an image
  and its README exist to publish).
- **Deliverables.** The manually triggered publish workflow; the date-tag
  computation with the ordinal-suffix rule; the anonymous-metadata gate
  before the push; §7's never-reuse enforcement applied to date tags (a
  publish that would overwrite an existing immutable tag **fails the job**);
  the §2.6 base-pull decision, logged; the GHCR namespace recorded.
- **How I test it.** **Crosses the boundary.** The operator authorises the
  workflow dispatch (a GitHub write) and the resulting **publish to GHCR**,
  then flips the new `steamcmd` package to public visibility — a one-time
  manual step only the owner can do (§2.6, §8), without which CI goes green
  while no consumer can pull. Verify with an anonymous pull from a
  logged-out client. Then dispatch a second run the same day and see the
  ordinal suffix, and a contrived attempt at an existing tag and see the job
  **fail**. Cost: Actions minutes and GHCR storage. Cleanup: none —
  published builder tags are retained deliberately (§7).
- **Status.** `pending`

### step-007 — The smoke-test gate, locally — `pending`

- **Objective.** The §8 gate that stands between a built game image and any
  publish, built and proven where it is free to iterate.
- **Spec sections implemented.** §8 (the smoke test itself), §5.6 (the stop
  path it asserts), §5.5 (healthy within a **stated bound**, past which the
  gate fails rather than hangs), §5.1 and §3.4 (read-only rootfs and
  arbitrary non-root uid exercised rather than trusted).
- **Depends on.** `step-pz-011` and `step-pz-012` done (stop mediation and
  the healthcheck must exist to be asserted).
- **Deliverables.** A gate, runnable from the justfile against a locally
  built image, that starts the image on its **default configuration
  profile** with only the documented mandatory variables, waits for healthy
  within the stated bound, sends the stop signal, and requires **exit 0** —
  under an **arbitrary non-root uid** with a root filesystem as read-only as
  the image's own documentation claims, writable mounts exactly at the
  documented paths (an image whose per-game specification states a reasoned
  deviation is tested against its own documented writable set). PZ's
  non-Steam profile (PZ §6) is exercised too, being the supported
  alternative profile that switches the healthcheck onto a different code
  path. Local runnability is a deliberate requirement: a gate only CI can
  run is one nobody debugs.
- **How I test it.** Free and local. Run the gate against a locally built
  image and see it pass; then break it deliberately — mount the state root
  read-only, and separately set the stop timeout below the save — and see it
  **fail with an attributable message** rather than hang; then run it
  against the non-Steam profile. Cleanup: remove this project's own
  containers and volumes by name; never a prune.
- **Status.** `pending`

### step-008 — The game build workflow in CI — `pending`

- **Objective.** CI can build the Project Zomboid image, gate it, and
  publish it under a namespace carrying none of §7's promises.
- **Spec sections implemented.** §8 (on-demand builds for a chosen image on
  the branch its per-game specification declares, whose current content
  determines the version; **the smoke test gating every game-image publish**,
  this namespace included; **pushes and pull requests that touch an image's
  sources getting a build-and-smoke run without publishing**), §7 (development
  builds never consume the release namespace — mutable, prunable, excluded
  from the never-reuse rule and the moving pointers, absent from consumer
  documentation).
- **Depends on.** `step-006`, `step-007` (the gate it wires in),
  `step-pz-013` done (labels and the published builder digest pin).
- **Deliverables.** The dispatchable build workflow; the `step-007` gate as
  a job that **blocks the publish** when it fails; the development tag
  naming, visibly not a release tag; and the push/pull-request job that
  builds and smoke-tests **without publishing**, with the path filters that
  decide when it runs.
- **How I test it.** **Crosses the boundary.** The operator authorises a
  dispatch; the run builds the image (a multi-gigabyte Steam download on
  GitHub's runners, no local cost), runs the gate, and publishes a
  development tag. Verify the tag exists, carries no `-rN`, and that a
  deliberately failing gate blocks the publish. Then open a throwaway pull
  request touching the image sources and see a build-and-smoke run that
  publishes nothing. Cleanup: development tags are prunable — deleting the
  package version is a gated act; ask.
- **Status.** `pending`

### step-009 — Release publication and tag policy — `pending`

- **Objective.** The `-rN` release stream, its moving pointers, and the
  never-reuse enforcement that protects them.
- **Spec sections implemented.** §7 in full for game images, §8 (the
  revision tag computed against what the registry already holds, never
  overwriting; first publish is not fully automatic), §5.8, §2.6.
- **Depends on.** `step-008`; **`step-pz-014` done** — the first `-rN` is
  the first tag a consumer may pin and is retained forever, so it must not
  publish before the per-image README that is also its GHCR page: §5.7's
  version-upgrade warning and §9's mount-ownership step have to reach a
  consumer *before* the pull, not after.
- **Deliverables.** The version/revision computation reading what the
  registry holds; **enforced-loudly-at-publish never-reuse** (a publish that
  would overwrite an existing immutable tag — a lost race, a recomputed
  revision — **fails the job, never proceeds**); the moving-pointer updates;
  and the mechanism that decides "newest" by publication order rather than
  by parsing version strings. **Measure before building state for that
  last one:** GHCR's package-version list carries creation timestamps and
  manifests carry §5.8's labels, so the ordering may be derivable from what
  the registry already stores. An in-repo record is a second source of truth
  for this project's strongest promise, and is built only if the registry's
  own metadata proves insufficient — with the reason logged. Fixtures for
  the computation, including the cases that must fail.
- **How I test it.** Locally and free: run the computation's fixtures,
  including a contrived existing-tag collision, and see it refuse. Then
  **crossing the boundary**: the operator authorises the first release
  publish, then **flips the `project-zomboid` package to public
  visibility** (§2.6, §8 — only the owner can). Verify `-r0` exists, the
  moving tags point at it, an anonymous pull works, and a second run at the
  same content produces `-r1` rather than moving `-r0`. Cost: GHCR storage,
  **retained deliberately and permanently**. Cleanup: none, by design.
- **Status.** `pending`

### step-010 — Scheduled update detection — `pending`

- **Objective.** A new Steam buildid becomes a published image without human
  action.
- **Spec sections implemented.** §8 (scheduled update detection), §2.3,
  §5.8, §7.
- **Depends on.** `step-009`; the schedule prerequisite in the table below.
- **Deliverables.** A periodic job comparing each game's current Steam
  buildid against the buildid label of the newest published **release**
  image — never a development tag, whose newer buildid would otherwise
  silently suppress a release publish — publishing automatically on **any**
  buildid change. A comparison that **cannot be established** (Steam
  unreachable, a newest image without a parseable buildid label) **fails the
  job loudly and is never treated as "no change"**. **Premise to verify
  first:** what GHCR actually exposes without pulling — the package-version
  list, per-version timestamps, and manifest labels — since the whole job
  rests on reading a label cheaply.
- **How I test it.** Locally and free: run the comparison against the real
  registry and Steam and see it report "no change"; then force the
  unestablishable case (a tag with no buildid label) and see it **fail
  rather than pass**. Then **crossing the boundary**: authorise one dispatch
  and watch it decide correctly. Cleanup: none unless it publishes; a
  publish is a legitimate release and is retained.
- **Status.** `pending`

### step-011 — Scheduled refresh, builder pin advance, staleness check — `pending`

- **Objective.** The only path by which security patches reach baked game
  images, and the deactivation-resistance §2.8 demands of it.
- **Spec sections implemented.** §8 (the refresh as **one flow**; the
  in-repo staleness check; superseded game versions never re-patched), §3.1
  (the pin moves only by this deliberate, automated act), §2.8, §10.7 (named
  as deferred, blind spot stated rather than hidden).
- **Depends on.** `step-010`; the schedule prerequisite in the table below.
- **Deliverables.** One flow that publishes a fresh builder date tag,
  **advances the pinned builder reference**, and rebuilds every game image
  against the refreshed base and builder — the pin advance becoming final
  **only when the game rebuilds succeed**, so a failed refresh leaves or
  restores the previous working pin rather than blocking every later
  on-demand build. Each rebuilt image's tag follows §7's mapping. Plus the
  **in-repo staleness check** that runs whenever anything else triggers CI
  and fails loudly when the refresh is overdue. The cadence and the
  staleness threshold are this implementation's choice and are proposed with
  reasons here rather than fixed in advance; the mechanism is not a choice.
- **How I test it.** Locally and free: run the staleness check with a
  contrived old timestamp and see it fail loudly; run the pin-advance logic
  with a failing game rebuild and see the **previous pin survive**. Then
  **crossing the boundary**: authorise one dispatch and watch a new builder
  date tag, an advanced pin, and rebuilt game images. Cost: Actions minutes,
  a multi-gigabyte rebuild on GitHub's runners, GHCR storage. Cleanup: none —
  the results are legitimate releases.
- **Status.** `pending`

---

## Milestone 3 — Repository-wide documentation

Written after one game has been walked through, so the conventions are
described as they were actually honoured rather than as they were planned.

### step-012 — The repository README's content requirements — `pending`

- **Objective.** `README.md` satisfies §9's repository-README requirements
  on top of the neutral entry point it already is.
- **Spec sections implemented.** §9 (project scope, image inventory, **the
  shared conventions of §5 stated once** — per-image docs link here rather
  than restating them; platform-neutral throughout), §1, §5, §11, §7.
- **Depends on.** `step-pz-014` done (the PZ README exists and links here).
- **Deliverables.** The §5 conventions stated once; the image inventory;
  scope and non-goals; the authority order and reviewer framing this file
  already carries, kept. Rule 8 still binds: descriptive, never directive
  toward the implementer.
- **How I test it.** Free. Read it as someone who has never seen the
  repository, follow one link per image, and check that no per-image README
  restates the conventions.
- **Status.** `pending`

### step-013 — The contributor guide for adding a game — `pending`

- **Objective.** The §5 checklist an implementer walks a new game image
  through.
- **Spec sections implemented.** §9 (the contributor guide), §6 (the
  per-game specification to write **first**, and its minimum contents), §5,
  §10.5, §10.6, §3.3.
- **Depends on.** `step-012`; the whole `pz` track (the guide describes a
  path actually walked).
- **Deliverables.** `docs/adding-a-game.md` (human-facing — never
  `.claude/docs/`): the per-game specification first, then the §5 checklist
  convention by convention, the track registration of rule 6 (directory,
  step-id prefix, plan, log), and what CI needs from a new game. Written
  from what the `pz` track actually did, not from the specification alone.
- **How I test it.** Free. Read it against `project-zomboid/` and check that
  every convention the PZ image honours appears as a checklist item, and
  that nothing in it is PZ-specific without saying so.
- **Status.** `pending`

---

## Cross-track dependencies

Stated here as well as in each step's `Depends on` line, so both endpoints of
every edge are visible from either side.

| This track | needs | for |
|---|---|---|
| `step-006` | `step-sc-001`, `step-sc-002` done | an image and its README before CI publishes them |
| `step-007` | `step-pz-011`, `step-pz-012` done | stop mediation and health, before the smoke gate can assert them |
| `step-008` | `step-pz-013` done | labels and the digest pin, before CI builds and publishes |
| `step-009` | `step-pz-014` done | the per-image README that is the GHCR page, before the first pinnable release |
| `step-012` | `step-pz-014` done | a per-image README that links to the repository README |
| `step-013` | the whole `pz` track | a path actually walked, before the guide describes it |
| **Other tracks need from here** | | |
| `step-sc-001` (`sc`) | **`step-005` done** — the whole foundation, CI green | no component-track step starts before the foundation is complete; `step-000` within it is what the Dockerfile lint family joins. **Closing `step-005` is what unblocks every component track.** |
| `step-pz-001` (`pz`) | `step-sc-001` done, and through it `step-005` | the same foundation edge, restated at both ends rather than inherited silently |
| `step-pz-013` (`pz`) | `step-006` done | a published builder digest to pin |

## External prerequisites

Things only the operator can prepare, each with the step that first needs
it.

| Prerequisite | First needed | State |
|---|---|---|
| **Branch topology for CI.** Scheduled workflows fire only from the **default branch**, and a workflow generally has to exist there to be dispatchable. Work is on `main`, which is the default branch, so `step-005`'s `push`-triggered gate and the `schedule` deliverables of `step-010` and `step-011` are all unblocked. Recorded because a later session would otherwise re-derive it. | `step-005`, `step-010` | **Satisfied** — work is on `main`, pushed |
| Public GitHub repository and its remote | `step-005` | **Satisfied**: `git@github.com:yannlugrin/docker-game-servers.git`, public |
| Authorisation of the first push | `step-000` close (rule 6 attempts a push at every close); mandatory at `step-005` | Open — asked at each close by the permission gate |
| GHCR owner namespace (§7) | `step-006` | **Confirmed**: `ghcr.io/yannlugrin` |
| One-time per-package visibility flip at first publish (§2.6, §8) | `step-006` (`steamcmd`), `step-009` (`project-zomboid`) | Open — only the owner can do it; without it CI goes green while no consumer can pull |
| A **Docker Hub credential, conditionally** — pulls stay anonymous until throttling is actually observed, then the operator supplies one as a CI secret (D-003) | `step-006` onward, only if limits bite | Conditional, and the decision is already taken — D-003 |
| Bandwidth and disk for the multi-gigabyte Project Zomboid download | `step-pz-001` | Ample free space measured at bootstrap; recorded in `.claude/docs/environment.md` from `step-000` |

## Coverage map — root `SPECIFICATIONS.md`

Generated from the steps' own "Spec sections implemented" lines. Every
section appears in at least one step, or below with the reason it is
excluded.

| Section | Step(s) |
|---|---|
| §1 Goal | `step-012`; binds every image step |
| §2.1 steamcmd is 32-bit glibc; amd64 only | `step-sc-001` |
| §2.2 steamcmd self-updates, no versions | `step-sc-001` (pre-warmed layer), `step-006` (date tags) |
| §2.3 app ids, branches, buildid | `step-sc-001`, `step-010` |
| §2.4 PID 1 signal semantics | `step-pz-007`, `step-pz-011` |
| §2.5 Steam query protocol | `step-pz-003`, `step-pz-012` |
| §2.6 Registry; visibility flip; Docker Hub rate limit | `step-006`, `step-009` |
| §2.7 `steamclient.so` at runtime | `step-pz-001` |
| §2.8 Idle scheduled workflows disabled | `step-005` (no schedule invented), `step-011` |
| §2.9 The measurement items | `step-sc-001` (base and builder sizes), `step-pz-001`, `step-pz-002`, `step-pz-003` |
| §3.1 Two tiers, one base, pinned builder reference | `step-sc-001`, `step-006`, `step-011`, `step-pz-001`, `step-pz-013` |
| §3.2 Baked at build time | `step-pz-001` |
| §3.3 One repository, one set of conventions | `step-012`, `step-013` |
| §3.4 uid-agnostic; no default user; uid-0 fatal; `ALLOW_UID0`; complete writable-path set | `step-pz-001`, `step-pz-005`, `step-pz-007`, `step-007` (exercised) |
| §3.5 The entrypoint is the adapter | `step-pz-007` and the `pz` entrypoint steps |
| §4.1–§4.4 The builder image | `step-sc-001`, `step-sc-002` (`sc` track) |
| §5.1 Filesystem and state | `step-pz-001`, `step-pz-005`, `step-007` |
| §5.2 Ports | `step-pz-003`, `step-pz-008`, `step-pz-011`, `step-pz-014` |
| §5.3 Configuration | `step-pz-008`, `step-pz-009`, `step-pz-010`, `step-pz-012` |
| §5.4 Secrets | `step-pz-008`, `step-pz-010` |
| §5.5 Observability | `step-pz-005` (logs), `step-pz-012` (health, clients), `step-007` |
| §5.6 Lifecycle and shutdown | `step-pz-007`, `step-pz-011`, `step-007` |
| §5.7 Backup knowledge | `step-pz-006`, `step-pz-014` |
| §5.8 Image metadata | `step-pz-013`, `step-sc-001`/`step-006` (builder labels), `step-010` |
| §6 Per-image specifications | Satisfied at bootstrap by the documents themselves: `project-zomboid/SPECIFICATIONS.md` (per-game form) and `steamcmd/SPECIFICATIONS.md` (pointer form, D-004). `step-013` carries the per-game half into the contributor guide; the pointer form needs no step until a second non-game component exists (rule 11 — built at the moment of need), and root §6 plus D-004 already state the rule |
| §7 Versioning and publication | `step-006` (builder), `step-008` (development namespace), `step-009` (releases), `step-011` |
| §8 Build automation | `step-005`, `step-006`, `step-007`, `step-008`, `step-009`, `step-010`, `step-011` |
| §9 Documentation deliverables | `step-sc-002`, `step-012`, `step-013`, `step-pz-014`; **LICENSE (MIT) already exists at the repository root — verified, no step needed** |

**Deliberately not implemented in this pass:**

- **§10 Future Considerations** (§10.1 Wine/Proton, §10.2 arm64, §10.3
  mod-baked variants, §10.4 non-anonymous games, §10.5 more games, §10.6
  non-Steam games, §10.7 external refresh watchdog) — the section's own
  instruction is "not built now; nothing in the present design may preclude
  them". §10.7 is named in `step-011` as the deferred closure of a stated
  blind spot, and §10.4's requirement on the builder (credentials that never
  persist) *is* implemented, at `step-sc-001`.
- **§11 Non-Goals** — conscious renunciations, nothing to build. Documented
  where a reader would otherwise assume otherwise: `step-sc-002` (no runtime
  steamcmd image), `step-012` (the rest).

## Open facts owned by this track

§2.9's measurement items. §2.9's third item — each game's `steamclient.so`
resolution — is per-game and owned by the `pz` plan.

| Open fact | Settled at | Pre-committed response |
|---|---|---|
| The ~megabytes cost of the §5.5 clients | `step-pz-002` (RCON), `step-pz-003` (Steam-query) | Autonomous if the size confirms the expectation; a client costing tens of megabytes is a §5.5 "should" deviation — logged, and back to the operator if it changes what the image documents |
| Debian slim as the smallest workable base | `step-sc-001` | A measurement that moves the expectation moves the named consequence, not the architecture (§2.9). A result implying a different base is a §3.1 **requirement** change — back to the operator |
| steamcmd's undocumented behaviour may shift under Valve's control | `step-sc-001`, re-observed at every `step-011` refresh | Already absorbed by design: the builder is date-stamped and pre-warmed rather than assumed stable |

## Open questions for the operator

Settled in the bootstrap exchange, recorded so they are not reopened: the
work is on `main`, the default branch, and `main` is the project;
other branches are **not** readable, so the earlier attempt's history is a dead
end and nothing from it is used (`CLAUDE.md` rule 1 now says so); the GHCR
namespace is `ghcr.io/yannlugrin`; base pulls stay anonymous with a Docker Hub
credential held in reserve (D-003); `CLAUDE.md`'s budget is D-002's.

Resolved without needing a ruling: **reading a published game image's buildid
label** — `step-010`'s comparison — is attempted first through the GitHub
Packages API via `gh`, which rule 9 already rules free. Only if that cannot
answer does the question of a bare registry manifest read arise, and I will
ask then rather than in advance.

Still open:

1. **Most of the root track waits on the `pz` track.** `step-007` through
   `step-013` cannot start until the PZ image is complete — the smoke gate
   needs stop mediation and health, everything after it needs the gate — so
   there is a long stretch of `pz`-track work with no root-track progress.
   That is what the dependencies dictate; gating workflows against an image
   that cannot yet report healthy or stop cleanly would be worse. Flagged so
   the sequencing is seen rather than discovered.
2. **Cadence numbers are unset on purpose.** §8 leaves the refresh cadence and
   the staleness threshold to the implementation; I will propose them at
   `step-011` with reasons rather than fixing them here, where they would be a
   number nobody has thought about since.
3. **Five fact-finding steps on the `pz` track cost five gates.** The question
   is stated where it belongs, in `project-zomboid/PLAN.md`'s open questions;
   noted here because the gate count is yours to spend.
