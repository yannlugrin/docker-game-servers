# Root track — implementation plan

Owns repository-wide work: foundation and harness, permission baseline,
workflow tooling, CI, shared documentation, publication. Step entry
shape, status values and the cost taxonomy are defined in `CLAUDE.md`
(Plan conventions). Cross-track sequence: the foundation milestone
precedes everything; then `step-sc-001`–`step-sc-002` (builder image),
then the project-zomboid track, then this track's CI-and-publication
milestone. `step-004` may interleave earlier, any time after `step-003`,
once the operator authorizes the first push.

## Milestone R1 — Repository foundation

The three gated foundation steps are `step-000`–`step-002`
(`DECISIONS.md` D-001's "foundation steps" means exactly those);
step-003 rides in this milestone because it is cheap, local and needed
before any image build. Closing this milestone triggers the
memory-compaction pass and state review of rule 3 (improvised inline
until step-002's agents exist — R1 closes after step-003, so they will
exist).

### step-000 — The harness, local only

- **Objective:** a fresh clone plus one documented setup command yields
  a working toolchain; one command answers "is what is committed here
  well-formed?"; nothing else changes.
- **Spec sections:** none directly (workflow foundation; rule 2).
- **Dependencies:** none.
- **Deliverables:**
  - `.gitignore` written with rule 5 in mind: local test state roots and
    downloaded game/steamcmd content (multi-gigabyte); local environment
    or credential files used in testing; tool caches;
    `.claude/reviews/` (the reviewer templates assume it is ignored — an
    untracked report otherwise blocks every clean-tree precondition
    downstream); `CLAUDE.local.md`.
  - Pinned base dependencies installable through **one documented setup
    command**.
  - The check/test/verify harness of rule 2, configured not written:
    the `pre-commit` framework (<https://pre-commit.com>) as hook
    runner; `just` (<https://github.com/casey/just>) as task runner
    carrying the entry points. No house linters — the standard tool of
    each ecosystem; anything bespoke is a logged decision put to the
    operator *before* it is built.
  - `just check` — well-formedness of the whole working tree, untracked
    files included, gitignored paths excluded, with one standing
    exception decided at bootstrap: everything under `.claude/spec-work/`
    is excluded from the harness (keyed on path, not tracked status).
    Because `pre-commit run --all-files` enumerates tracked files only
    (a tool-behavior claim to verify against the pinned pre-commit
    version at this step — the negative test below proves it
    empirically), check passes the file list explicitly:
    `pre-commit run --files $(git ls-files --cached --others
    --exclude-standard)` — read-only glue, never index-priming
    (`git add --intent-to-add` writes state and corrupts the clean-tree
    signal). A lint error in an untracked file must fail check.
  - `just test` — "is the implementation right?". The repository ships
    no behaviour of its own yet, so a test command that says exactly
    that is the correct state, not a gap. Three standing limits:
    third-party tools are never retested; a must-warn case is required
    only where a warning tier already exists; no fixtures ahead of
    shipped behaviour.
  - `just verify` — both.
  - The same harness wired into the commit hooks so the two local
    runners never diverge.
  - Prose lint over the governance documents as they already are — the
    specifications are read-only (rule 1) and `.claude/refs/` too
    (rule 3), so the lint config bends to them, never the reverse;
    excluding a document from a rule is a logged decision, not a quiet
    config line. JSON well-formedness for `.claude/settings.json`
    (first file of that class already exists).
  - **CI is deliberately not in this step**: nothing local can exercise
    a workflow, and a tagged step must not carry an artifact its own
    gate never ran. It is `step-004`, sequenced at the moment the
    operator authorizes the first push.
- **How the operator tests it:** fresh clone, run the setup command,
  run `just check`, make one commit — all green. Then the negative
  paths this step's own musts assert: drop a deliberately broken
  untracked file → `just check` fails; the same file placed under
  `.claude/spec-work/` → `just check` passes; run `just test` (reports
  the no-shipped-behaviour state) and `just verify` once. Free local;
  cleanup: delete the two throwaway files.
- **Status:** pending.

### step-001 — Permission and hook baseline

- **Objective:** rule 9's boundary enforced mechanically, not just
  textually; the enforcement mechanisms proven, not assumed.
- **Spec sections:** none directly (rule 9; rule 2's probe duty).
- **Dependencies:** step-000.
- **Deliverables:**
  - **Extend the committed `.claude/settings.json`** (auto memory is
    already off — keep it off) with a baseline proposed for operator
    review: **allow** the harness, the setup command, the free side of
    rule 9's boundary, and the additive and read-only subset of local
    git (add, commit, status, diff, log, show, rev-parse, describe, tag
    listing, annotated tags); **ask** for everything rule 9 gates,
    `git push` included — a denied pattern cannot be overridden in the
    very exchange rule 9 relies on — and for state-destroying local
    git, stated as a **classifier, not a list**: anything that rewrites
    history (`commit --amend`, `rebase`), moves or deletes tags or
    branches, or destroys uncommitted or untracked work (`reset
    --hard`, `git clean`) asks first. An allow pattern must not
    silently admit one of them — the trap: a bare `git commit`
    allowance admits `--amend`. **Deny** is reserved for what has no
    authorized use at all, each named in the proposal rather than
    leaving "destructive" to interpretation. A guard hook wherever a
    permission pattern cannot express the rule — instructions shape
    behaviour, but only settings and hooks enforce it.
  - Rule 2's enforcement probes for this step's mechanisms: prove what
    each settings key and permission pattern actually does in the
    running Claude Code version — including that `autoMemoryEnabled`
    is honoured, and the known trap that (as of 2.1.231) file-edit
    rules match `Edit(path)` while `Write(path)` rules never fire.
    Probes are independent — one passing says nothing about another.
    Report what each probe found, including mechanisms that turned out
    to enforce nothing; what binds is what is kept.
- **How the operator tests it:** review the proposed baseline (rule 4:
  the baseline is never mine alone) plus the probe results — and one
  live demonstration, so enforcement is observed rather than
  self-reported: watch a gated command (e.g. `git push --dry-run`)
  produce an ask prompt while an allowed one (`git status`) does not.
  Free local.
- **Status:** pending.

### step-002 — Workflow tooling

- **Objective:** the step rituals and reviewer agents exist before the
  events they handle; nothing improvised at a milestone boundary.
- **Spec sections:** none directly (rule 3's tooling namespace).
- **Dependencies:** step-001.
- **Deliverables:**
  - Instantiated from `.claude/spec-work/handoff/assets/`: the four
    skills `orient`, `resume-step`, `handover-step`, `approve-step`;
    the `step-reviewer` agent; and the agents whose trigger is a
    certainty of this plan — `state-reviewer` and `optimize-memory`
    (every milestone close needs both; tooling created during the event
    it handles arrives too late). `code-reviewer` and `test-reviewer`
    wait for their conditional triggers — first code and first
    shipped-behavior test, both landing at `step-sc-001`, which owns
    their adoption — and stay on `CLAUDE.md`'s not-yet-adopted list,
    the documented-fallback carve-out.
  - Every placeholder filled with this repository's real commands and
    paths — with the monorepo exception: the governance set
    (`{{PLAN}}`, `{{DECISIONS}}`, `{{SPEC}}`, `{{STEP_ID}}`) resolves
    the active track **at invocation** from `CLAUDE.md`'s track map and
    Current state pointer, `{{SPEC}}` on a component track including
    the root specification; rituals fired while closing a step key on
    the track of the step **just closed**, named by the close ritual,
    never the advanced pointer. Where a template's enumeration of a
    routine is narrower than the rule it executes, the rule wins and
    the enumeration is rewritten. A state-reviewer placeholder whose
    referent does not exist yet (architecture vocabulary, inspection
    commands) is seeded from the specification's component vocabulary
    and kept current under rule 6. No instantiated file names a skill
    or agent not adopted (the not-yet-adopted list is the one
    carve-out). Each adoption logged (rule 4).
  - Governance well-formedness checks join the harness with this
    step's first files of the class: skill/agent frontmatter must
    parse.
  - Rule 2's probe for the mechanism this step introduces: agent
    `tools:` frontmatter — does it actually restrict? Reported like
    step-001's probes. (The `.claude/rules/` probe waits for the step
    that first adopts a rules file, if any.)
- **How the operator tests it:** invoke each ritual and see it do what
  it claims — a new skill or agent may only be picked up at session
  start, so the handover states whether a restart is part of the test.
  Free local.
- **Status:** pending.

### step-003 — LICENSE

- **Objective:** the repository's license exists before any image build
  bakes the license annotation.
- **Spec sections:** root §9 (LICENSE deliverable), §5.8 (license
  annotation value).
- **Dependencies:** step-000 (prose lint applies to it if configured
  for it).
- **Deliverables:** `LICENSE` at the repository root, MIT — licensing
  the image recipes and tooling, not the game content inside the
  images (root §9 states this; the README restates it at step-006).
- **How the operator tests it:** read the file; `just check` green.
  Free local.
- **Status:** pending.

## Milestone R2 — CI and publication

Runs after the project-zomboid track completes (except step-004, which
may interleave any time after step-003 once the first push is
authorized). Every step here except step-006 crosses rule 9's boundary:
GitHub and GHCR are shared public state, and each test names its cost
and cleanup.

### step-004 — Harness CI workflow

- **Objective:** CI runs exactly the local harness; the two never
  diverge.
- **Spec sections:** root §8 (the repository's CI obligation), rule 2.
- **Dependencies:** step-003; **external:** GitHub repository (existing,
  public, Actions enabled), its remote configured, and the operator's
  authorization of the first push.
- **Deliverables:** a GitHub Actions workflow reusing `just check` /
  `just test` as its entry points, check and test as separate jobs once
  both exist, toolchain cached; a way of proving a fresh setup still
  works — a "should" planned to ride the scheduled refresh (step-010)
  rather than become a second scheduled workflow. Actions-YAML
  validation (actionlint or ecosystem standard) joins the harness with
  this first workflow file.
- **How the operator tests it:** authorize the push; watch the workflow
  run green on the pushed commit. **Crosses the boundary:** `git push`
  to the public repository — the history becomes public; cleanup is
  none (additive, and the repository is meant to be public).
- **Status:** pending.

### step-005 — Image build-and-smoke CI (no publish)

- **Objective:** an entrypoint regression is caught at push time, not
  at the next publish attempt.
- **Spec sections:** root §8 (build-and-smoke-test without publishing;
  builder gate; §2.6 throttling decision).
- **Dependencies:** step-004, step-sc-001, step-pz-010 (the smoke
  script this workflow reuses).
- **Deliverables:** a workflow triggered by pushes and pull requests
  touching an image's sources: builds the touched image, runs the
  builder's minimal gate (steamcmd to completion on an anonymous
  metadata query) and the game image's smoke test (step-pz-010's
  script — default profile, mandatory variables only, healthy within
  the stated bound, stop, exit 0, arbitrary non-root uid, read-only
  rootfs per the image's documented claims). No publish; if a test
  ever genuinely needs a pullable image, it uses §7's development
  namespace, never a release tag. This step also decides root §2.6's
  Docker Hub anonymous-pull throttling response deliberately (mirror /
  authenticated pulls / accept) — a logged decision; if authenticated
  pulls are chosen, a Docker Hub credential becomes a CI-secret
  prerequisite and is flagged to the operator the moment the choice is
  made.
- **How the operator tests it:** push (authorized) a trivial change
  under an image directory; watch build+smoke run green without
  publishing. **Crosses the boundary:** pushes and Actions minutes;
  the smoke test's default-profile start briefly registers on the
  Steam server browser from a runner (accepted, per rule 9); cleanup:
  none needed.
- **Status:** pending.

### step-006 — Repository README and contributor guide

- **Objective:** the shared conventions stated once; adding a game has
  a checklist.
- **Spec sections:** root §9 (repository README, contributor guide),
  §1 (platform-neutral wording), §3.3, §5 (the conventions being
  stated).
- **Dependencies:** step-pz-012 (conventions materialized and
  documented once, so this README can state them accurately).
- **Deliverables:** `README.md` grown into the root §9 repository
  README — project scope, image inventory, §5 conventions stated once,
  per-image docs linking here; `docs/CONTRIBUTING-A-GAME.md` (name
  final at implementation) — the §5 checklist a new game walks
  through, starting with the per-game specification of §6. All
  platform-neutral. The bootstrap README's For-reviewers and file-map
  content is preserved or relocated, not lost.
- **How the operator tests it:** read both; `just check` green. Free
  local.
- **Status:** pending.

### step-007 — Publish workflow and first builder publish

- **Objective:** on-demand publication exists; the builder is public.
- **Spec sections:** root §8 (on-demand builds, builder gate, first
  publish), §7 (builder date tags, `latest`, immutability guard, dev
  namespace), §2.6 (visibility flip), §4.1 (public product).
- **Dependencies:** step-005, step-sc-002; **external:** GHCR owner
  namespace (`ghcr.io/<owner>`); the operator's one-time flip of the
  `steamcmd` package to public visibility at first publish.
- **Deliverables:** the on-demand publish workflow, scoped to what
  this step's gate can exercise: the **builder path** — new date tag
  (`YYYYMMDD`, `.1` ordinal on same-day rebuilds) plus `latest`,
  gated by the builder smoke of root §8 (the step-sc-001 predicate) —
  and the **shared publish machinery**: a publish that would
  overwrite an existing immutable tag **fails the job, never
  proceeds** (root §7), and any test publish uses §7's development
  namespace. The game publish path is deliberately step-008's
  deliverable — this step's gate never runs it. First real run
  publishes the builder.
- **How the operator tests it:** dispatch the workflow for the builder;
  see the date tag and `latest` on GHCR; flip visibility; anonymous
  `docker pull` succeeds. **Crosses the boundary:** registry write —
  a public, indefinitely retained artifact (release tags are never
  deleted, root §7); cleanup: none intended — this is the first
  release.
- **Status:** pending.

### step-008 — Game publish path and first Project Zomboid publish

- **Objective:** the game image is public as `<version>-r0`, through a
  gated publish path.
- **Spec sections:** root §7 (game tags, moving pointers,
  publication-order rule), §8 (smoke gate on every game-image publish,
  visibility flip), §5.8 (labels: version, revision, buildid, branch,
  builder reference).
- **Dependencies:** step-006 (the README this publish's GHCR page
  links to for shared conventions), step-007, step-pz-012 (image and
  README complete); **external:** the operator's visibility flip of
  the `project-zomboid` package.
- **Deliverables:** the **game publish path** added to step-007's
  workflow: declared branch only, version tag from current branch
  content, revision computed against what the registry holds, moving
  `<game-version>` and `latest` pointers advanced by **publication
  order of new-version builds, never a version-string sort**
  (root §7), every game publish **gated by the step-pz-010 smoke
  script** (root §8) and by step-007's immutable-tag overwrite guard.
  First real run publishes `<game-version>-r0` with correct labels.
- **How the operator tests it:** dispatch, watch the gate, flip
  visibility, `docker pull` and inspect labels; optionally run the
  documented quickstart against the published image. **Crosses the
  boundary:** registry write, public and retained; the smoke gate's
  default-profile start registers briefly on the Steam browser;
  cleanup: none intended.
- **Status:** pending.

### step-009 — Scheduled update detection

- **Objective:** a game update publishes a new image without human
  action; a comparison that cannot be established fails loudly.
- **Spec sections:** root §8 (update detection), §2.3 (buildid), §5.8
  (buildid label as the comparison side), §7 (tag mapping).
- **Dependencies:** step-008 (a published release image to compare
  against).
- **Deliverables:** a scheduled workflow comparing each game's current
  Steam buildid against the buildid label of the newest published
  **release** image (never a dev tag); on any change, build and
  publish per §7 (new version tag, or revision bump on unchanged
  version string) — **through step-008's gated game publish path**
  (smoke gate and overwrite guard), never a parallel one. Steam
  unreachable or an unparseable label **fails the job** — never "no
  change".
- **How the operator tests it:** dispatch the detection job manually
  once: with no upstream change it reports "up to date" and publishes
  nothing; the failure path is exercised by pointing the comparison at
  a deliberately broken input in a dry-run mode or test, stated at
  handover. **Crosses the boundary:** workflow dispatch; a real
  upstream change would publish (that is its job); cleanup: none.
- **Status:** pending.

### step-010 — Scheduled refresh and staleness watchdog

- **Objective:** security patches keep reaching multi-gigabyte public
  images; the refresh cannot die silently.
- **Spec sections:** root §8 (scheduled refresh, pin advance,
  staleness check), §2.8 (idle-schedule deactivation), §3.1 (pinned
  builder reference).
- **Dependencies:** step-009.
- **Deliverables:** one scheduled flow that publishes a fresh builder
  date tag (through step-007's gated builder path), advances the
  pinned builder reference the game builds use (the pin moves only by
  this deliberate automated act), and rebuilds every game image
  against the refreshed base — the pin advance final **only when the
  game rebuilds succeed**, a failed refresh leaving or restoring the
  previous working pin; tags per §7 (new version's `-r0` if the
  branch moved, else revision bump), all game publishes **through
  step-008's gated path** — root §8's smoke gate binds every
  game-image publish, scheduled ones included; superseded versions
  never re-patched (root §8's stated choice). Plus the in-repo
  staleness check: runs whenever anything else triggers CI, fails
  loudly when the refresh is overdue — blind spot (idle repo, unread
  deactivation notice) documented, external watchdog deferred to
  root §10.7. The fresh-setup proof from step-004 rides this refresh.
- **How the operator tests it:** dispatch the refresh manually; see
  new builder tag, pin-advance commit, rebuilt game images with
  correct tags; then a dry-run or fixture exercise of the failure path
  (pin not advanced). **Crosses the boundary:** registry writes and a
  workflow-authored commit+push; cleanup: none intended (all
  additive).
- **Status:** pending.

## Specification coverage (root document)

| Section | Where |
|---|---|
| §1 Goal | All tracks; platform-neutrality enforced in every doc step (006, sc-002, pz-012) |
| §2.1–§2.2 | step-sc-001 (base, self-update baked) |
| §2.3 | step-pz-001 (buildid capture), step-009 (comparison) |
| §2.4 | step-pz-007 (signal chain) |
| §2.5 | step-pz-008 (query probe) |
| §2.6 | step-005 (throttling decision), 007/008 (GHCR, visibility) |
| §2.7 | step-pz-001/pz-002 (Steam client libraries) |
| §2.8 | step-010 (deactivation-resistant refresh) |
| §2.9 | its three items each owned: steamclient resolution → step-pz-002; the size claims measured → step-sc-001 (builder/base) and step-pz-008 (§5.5 clients); steamcmd behavioral drift → a standing risk absorbed by the date-stamped, pre-warmed builder design (§4, §7) and Open questions #4 |
| §3.1–§3.2 | step-sc-001, step-pz-001 |
| §3.3 | step-006 (conventions stated once) |
| §3.4 | step-pz-003, step-pz-010 |
| §3.5 | step-pz-003…pz-007 |
| §4 | steamcmd track (see `steamcmd/PLAN.md`) |
| §5.1 | step-pz-003, pz-010 |
| §5.2 | step-pz-002, pz-004, pz-012 |
| §5.3 | step-pz-004, pz-006 |
| §5.4 | step-pz-004, pz-006, pz-012 |
| §5.5 | step-pz-008, pz-011 |
| §5.6 | step-pz-007 |
| §5.7 | step-pz-011 |
| §5.8 | step-sc-001, step-pz-001, steps 007–009 |
| §6 | per-game documents exist; honored across the pz track |
| §7 | steps 007–010 (and pz-001's tag inputs) |
| §8 | steps 004, 005, 007–010 |
| §9 | steps 003, 006; step-sc-002; step-pz-012 |
| §10 Future considerations | **Excluded**: explicitly deferred by the spec; nothing here may preclude them (checked at review, not built) |
| §11 Non-goals | **Excluded**: conscious renunciations; no step implements them |

## External prerequisites (operator-only)

| Prerequisite | First needed at |
|---|---|
| GitHub repository — existing, public, Actions enabled — its remote, and authorization of the first push | step-004 |
| GHCR owner namespace `ghcr.io/<owner>` (names every published image, root §7) | step-007 |
| GHCR package visibility flip: `steamcmd` | step-007 |
| GHCR package visibility flip: `project-zomboid` | step-008 |
| *Conditional:* Docker Hub pull credential as a CI secret — only if step-005 resolves root §2.6's throttling with authenticated pulls; flagged the moment that choice is made | step-005 |
| *Conditional / verify:* repository workflow write permission (`GITHUB_TOKEN` `contents: write` or equivalent) for the refresh's pin-advance commit+push — verified at step-010; only the owner can flip the setting if required | step-010 |

## Open questions and risks (all tracks)

1. **steamcmd track has two steps** — too small to group under
   milestones. I propose treating that track's completion (after
   step-sc-002) as its one milestone close, triggering the rule 3
   compaction and state review. Confirm or reorder.
2. **When to run step-004.** It can interleave any time after step-003
   once you authorize the first push. Earlier gives CI coverage over
   the whole pz track's commits; later keeps everything local longer.
   Your call; the plans assume "at your convenience".
3. **Open-fact fallout.** Several project-zomboid open items can only
   resolve at pz steps, and unfavorable resolutions of (d), (e), (f),
   (g), (k), (l) come back to you before any amendment (rule 1).
   Expect possible mid-milestone exchanges there; the plan cannot
   pre-decide them.
4. **steamcmd behaviour is undocumented upstream** (root §2.2, §2.9):
   the buildid-capture mechanism at build time (needed for §5.8
   labels) is designed in step-pz-001 and may need iteration if
   steamcmd's output format shifts.
5. **Version-string source for tags** (pz open item e): if it resolves
   unfavorably, PZ tags become buildid-derived (root §7 fallback) —
   an operator-facing naming change, so it would come to you first.
6. **Actions runner capacity — feasibility to verify, not assume:**
   the pz image build downloads multi-gigabyte Steam content in CI
   (steps 005, 008–010), and hosted-runner disk headroom for the
   builder stage plus final image plus layer cache is a measurement,
   not a given. Step-005's first CI build measures it; if disk or
   build time proves prohibitive, the options (cache strategy,
   self-hosted runner) come to you as a decision, not an assumption.
