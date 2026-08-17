# Implementation plan — root track

The root track owns repository-wide work: the foundation and harness, the
steamcmd builder image (root §4), CI (root §8), and the repository-wide
documentation of root §9 (this repository's README, the contributor guide).
Per-game images live on their own tracks; the first is `pz`
(`project-zomboid/PLAN.md`).

`§N` references point to the root `SPECIFICATIONS.md`; `PZ §N` to
`project-zomboid/SPECIFICATIONS.md`. Step-entry shape, status vocabulary and
the compaction-on-approval rule are defined in `CLAUDE.md`.

## How to read this plan

- Steps are ordered by dependency. The order and headings define the
  sequence; the numbers are identifiers, frozen when a step enters
  `in progress`, and never reused.
- Cross-track sequencing is stated per step ("needs `step-pz-012` done"),
  never inferred from a global order.
- Exactly one step is in progress repository-wide, whichever track it
  belongs to.
- Costs are stated per test. A test that crosses the rule-9 action
  boundary says so, what it costs, and how to clean up.

---

## Milestone 1 — Repository foundation

Four steps, drawn by what a working repository needs rather than by cost
class. CI is the first step that leaves this machine, which is why it comes
last *within* the foundation — not a reason to move it into a later
milestone. The project is not bootstrapped until its CI has run green.
Closing this milestone triggers the whole-state review and the
memory-compaction pass (`CLAUDE.md`, rule 3).

### step-000 — The harness, local only — `pending`

- **Objective.** A repository that can check itself, locally, from a fresh
  clone: pinned dependencies behind one setup command, and the
  check/test/verify entry points of rule 2 — carrying only the check
  families whose artifacts already exist.
- **Spec sections implemented.** None directly — this step is rule 2's
  harness, not specification content. It brings the specification documents
  and this session's six governance files under lint retroactively.
- **Depends on.** Nothing.
- **Deliverables.**
  - `.gitignore`, rewritten with rule 5 in mind: local test-state roots and
    volume directories; env files carrying test credentials; tool caches;
    game content downloaded outside an image build; `CLAUDE.local.md`;
    `.claude/reviews/` (the reviewer agent templates write reports there and
    assume it is ignored — an untracked report otherwise blocks every
    clean-tree precondition downstream); and `.claude/worktrees/`, which the
    current `.gitignore` already carries and **must survive the rewrite** —
    a commit made while an agent worktree exists otherwise swallows its
    checkout.
  - Pinned base dependencies, installable through **one documented setup
    command**. Measured today on this machine: `just` 1.45.0, `docker`
    29.6.2, `python3` 3.14.4, `jq` 1.8.1, `gh` 2.97.0 present;
    `pre-commit`, `uv`, `pipx`, and every linter absent. The setup command
    therefore has to install `pre-commit` itself; `pip` and the `venv`
    module are available. Which bootstrap it uses is a logged workflow
    decision (rule 4).
  - The rule-2 harness, **configured rather than written**: `pre-commit`
    (<https://pre-commit.com>) as the hook runner, `just`
    (<https://github.com/casey/just>) as the task runner, each ecosystem's
    standard linter pinned in one place, no house preference.
    - `check` — "is what is committed here well-formed?" — syntax, lint and
      formatting over the working tree, **untracked files included and
      gitignored paths excluded**, with two standing exclusions keyed on the
      path and not on tracked status: everything under `.claude/spec-work/`
      (rule 1 makes that directory no session's reading material) and
      everything under `.claude/refs/` (operator-supplied reference
      material, read-only under rule 3 and owned elsewhere).
    - `check` takes a **scope**: the whole-tree gate as the default, and the
      narrowed what-changed form the development loop runs between gates —
      **one entry point taking a scope, never a second recipe**, because two
      recipes hold two lists of checks and will eventually differ in *what*
      they look for, not only in how much.
    - The file list is passed to `pre-commit` **explicitly** —
      `git ls-files --cached --others --exclude-standard` — because runners
      that enumerate from git (`pre-commit run --all-files` among them) see
      only what git already knows about. **Never**
      `git add --intent-to-add`: it writes to the index as a side effect of
      a *check*, turning `?? file` into ` A file` in `git status
      --porcelain` — the output the handover and approve rituals read for
      their clean-tree preconditions — and lets the next `git commit -a`
      sweep that file into an unrelated commit. The glue is one command
      substitution, not a bespoke runner.
    - `test` — "is the implementation right?" — fixtures and expectations
      proving the behaviour **this repository itself ships**, the cases that
      must fail included. Three limits: a third-party tool is never
      retested; a must-warn case is required only where the implementation
      already defines a warning tier; and where the repository ships no
      behaviour of its own yet, **a `test` command that says so is the
      correct state**, not a gap to fill.
    - `verify` — runs both.
    - The same harness wired into the **commit hooks**, so the local runners
      cannot diverge.
  - Check families **only for artifact classes that exist at this step**
    (rule 2's never-ahead rule): the governance and human-facing documents
    (markdown/prose lint, configured to the documents as they already are —
    the specifications are read-only under rule 1, so the lint bends to them
    and never the reverse, and excluding a document from a rule is a logged
    decision, not a quiet config line), and JSON well-formedness for
    `.claude/settings.json`. Dockerfile lint, entrypoint-language lint,
    workflow validation, Python lint and the skill/agent frontmatter parse
    arrive with their first artifact, in the step that lands it — so this
    step's green gate says nothing about files that are not there.
  - Documented commands, runnable by the operator too, listed in
    `README.md`.
- **How I test it.** All free and local. From a fresh clone of this branch
  (`git clone . /tmp/gs-clone`): run the documented setup command; run
  `just check`; make a trivial commit and watch the hook run. Then, in the
  working tree, create a file with a deliberate lint error and **do not
  `git add` it** — `just check` must fail on it; delete it. Cleanup: remove
  the clone directory.
- **Status.** `pending`

### step-001 — The permission and hook baseline — `pending`

- **Objective.** Rule 9's boundary enforced mechanically, proposed to the
  operator as one reviewable whole, with every mechanism measured rather
  than assumed.
- **Spec sections implemented.** None — workflow enforcement.
- **Depends on.** `step-000` (the guard's `--liveness` is wired into the
  commit hooks and its `--selftest` into `test`).
- **Deliverables.** The guard decides the shape of the settings, not the
  other way round.
  - **The guard first.** Instantiate
    `.claude/spec-work/handoff/assets/bash_guard.py` as
    `.claude/hooks/bash_guard.py` (executable), read its module docstring in
    full, and edit **only** its `REGISTRY`. That docstring is the doctrine
    for this deliverable: how to choose between *rules* and *grants* per
    tool, what must land in `.claude/settings.json`, what the guard cannot
    see, and the rule that its `GIT` ground rules are the same in every
    project and are **added to, never weakened**.
  - An inventory of what this project actually runs, each tool given the
    acts rule 9 gates *for this project*: the harness (`just`,
    `pre-commit`), `docker` and its relatives, `steamcmd` invocations, `gh`.
  - The guard cannot see inside a `just` recipe — it sees `just release`,
    never the `docker push` inside it. That is why rule 2 carries the
    **no-gated-act justfile invariant**; record it here as a rule of the
    baseline, and keep the justfile honest to it whenever a recipe changes.
  - Every rule added gets a `CASES` entry: `--selftest` fails on a rule no
    case reaches, which is what keeps the intent executable rather than
    remembered.
  - **Then the settings**, per the docstring's pairing: one broad allow per
    registry tool; **no `ask` rule for anything the guard gates** (a
    matching `ask` prompts even where the guard says allow, so it cancels
    every carve-out); no prefix rule restating a guard decision (a prefix is
    strictly weaker and gives two sources of truth); and, as the **one
    deliberate exception**, a short `deny` backstop for the acts that cannot
    be undone — a hook fails open, and a prefix rule that binds without it
    is worth more than the duplication costs. Keep it short enough that the
    exception stays visible as one. `ask` stays for tools the guard has no
    registry entry for (`curl`, whatever else this project reaches for).
    **`git push` is not one of them**: it is gated in the guard's ground
    rules, and restating it as a prefix rule is the two-sources-of-truth
    case, the weaker of which misses `git -C dir push`. What holds for a
    push wherever it is expressed is the *tier*: **it asks and is never
    denied** — a denied pattern cannot be approved in the very exchange rule
    9 relies on. `deny` stays reserved for what has no authorised use at
    all, each named in the proposal.
  - Auto memory is already off (`.claude/settings.json`) — keep it off.
  - **Gated twice, two different questions.** `bash_guard.py --liveness` in
    the pre-commit lint: the file is executable, the registry builds, every
    rule and grant is well-formed, a payload still comes back as a verdict —
    no behaviour cases, so a lint stays a lint, and the silent deaths (a
    syntax error from an edit, a lost `+x`, a rename) fail the commit.
    `bash_guard.py --selftest` in the *test* entry point: liveness, then
    every case, then coverage.
  - The proposal says plainly **what a dead guard would leave open** — a
    broad allow plus a dead hook is a wider surface than a narrow allow list
    ever was, which is exactly where the `deny` backstop earns its place.
  - The **governance well-formedness** family gains its first behavioural
    member here: the hook path in `.claude/settings.json` **resolves** — a
    path naming a file that is not there leaves valid JSON, a settings file
    that loads, a green lint, and a guard that never runs.
  - The **Python check family** arrives with this file (rule 2's never-ahead
    rule): the guard is the repository's first Python, and it ships whatever
    the entrypoint language turns out to be. It carries the **width
    exemption its own docstring names for that one path** (88 columns) —
    with `pre-commit`, the exemption also needs `force-exclude`, since
    filenames are passed explicitly.
  - **Then measure, and write down what was measured.** Rule 2's probes for
    this step's mechanisms run here, and the results land in a
    `.claude/docs/` file — never in `CLAUDE.md` and never in a plan: a
    version-stamped fact restated in standing instructions outlives its
    version in silence. Every claim carries the version it was taken on
    (Claude Code 2.1.233 today), the method, and a short re-measure recipe
    to re-run after a Claude Code update. Probe at least: whether the
    settings keys set here are honoured (`autoMemoryEnabled: false`
    included); which spelling of a path rule the file tools actually match;
    whether the hook is **reached** at all; and the three-command liveness
    check the session rituals of `step-002` can run — one command that must
    run silently, one the guard *grants*, and one it must **refuse, naming
    the rule that read it**. That third probe is the only one that says the
    hook is reached: if it merely prompts, the hook is not wired and the
    `deny` backstop is all that is left, while `--selftest` and `--liveness`
    would still pass — they answer whether the file is correct, not whether
    anything calls it.
  - **The permission mode**, named in the proposal and set as a committed
    setting (`permissions.defaultMode`), not left to a per-session choice —
    it decides how much the rest has to carry. This plan names no modes and
    asserts no mode behaviour deliberately: the mode set, and what each mode
    does to an unmatched command, are properties of the installed version.
    Take the list from the running version and **probe the mode proposed**:
    what an unmatched command does under it, and **whether a hook `ask`
    still prompts** — the close ritual attempts its push in reliance on
    that, and a gate that has stopped gating says nothing about it. Set the
    mode rather than working around it (a mode that auto-accepts file edits
    is what removes the need for a blanket `Edit(/**)` allowance), and let
    it decide whether the mode-disabling keys belong in the baseline at all.
  - The step summary reports **what each mechanism actually did, including
    the ones that turned out to enforce nothing**.
- **How I test it.** Free and local. Read the proposal (the registry, the
  settings baseline, the named `deny` list, the proposed permission mode)
  and the `.claude/docs/` measurements file; run `.claude/hooks/bash_guard.py
  --selftest` and see it green; run the three liveness commands from the
  measurements file and observe silence, a grant, and a refusal **naming its
  rule**. The permission baseline is explicitly outside the "should"
  latitude — this step exists to put it to the operator.
- **Status.** `pending`

### step-002 — The workflow tooling — `pending`

- **Objective.** The rituals and reviewers that every later step runs,
  instantiated from the handoff assets and adapted to this repository.
- **Spec sections implemented.** None — workflow tooling.
- **Depends on.** `step-001` (the rituals cite the boundary it enforces and
  run the liveness commands it measured).
- **Deliverables.**
  - Instantiated from `.claude/spec-work/handoff/assets/` per rule 3, every
    placeholder filled with this repository's real commands and paths:
    `orient`, `resume-step`, `handover-step`, `approve-step` (skills, under
    `.claude/skills/<name>/SKILL.md`), the `step-reviewer` agent, and the
    agents whose trigger is a **certainty of this plan** — `state-reviewer`
    and `optimize-memory`, which a milestone close needs to *exist* before
    it arrives rather than improvised at the boundary. A recovery ritual
    created during the crisis it is needed for is too late.
  - The **governance placeholder semantics** of rule 3: `{{PLAN}}`,
    `{{DECISIONS}}`, `{{SPEC}}` and `{{STEP_ID}}` are the exception to
    literal filling. Each template is instantiated **once**,
    repository-wide, and those placeholders resolve to the **active track at
    invocation** — from the track map and `CLAUDE.md`'s `Current state`
    pointer — never to one literal path. On a `pz`-track step, `{{SPEC}}`
    includes the root specification. **One exception, and it is the one that
    fails silently:** rituals fired as part of *closing* a step — the
    milestone state review and the memory compaction above all — key on the
    track of the step **just closed**, named explicitly by the close ritual,
    never on the pointer, which the close ritual has already advanced. At a
    cross-track milestone boundary, resolve-at-invocation would aim both
    passes at the wrong track, and a state reviewer reading the wrong
    track's plan reports nothing wrong.
  - Where a template's own enumeration of a routine is narrower than the
    rule it claims to execute, **the rule wins** and the enumeration is
    rewritten to match (`orient`'s steps 1–2 against `CLAUDE.md`'s
    multi-track session routine is the known instance).
  - A placeholder whose referent does not exist yet — the state reviewer's
    `{{ARCHITECTURE_VOCABULARY}}` and `{{INSPECTION_COMMANDS}}`, in a
    repository where nothing is built — is seeded from the specification's
    own vocabulary and kept current under rule 6 as the system
    materialises.
  - **No instantiated file may name a skill or agent that was not adopted**:
    trim the reference or adopt it, because a dangling name is a ritual that
    silently skips a step. One carve-out: a name on `CLAUDE.md`'s
    not-yet-adopted list is not dangling — it is the documented fallback the
    milestone ritual relies on.
  - The conditionally triggered rest (`code-reviewer`, `test-reviewer`) is
    **proposed only when its trigger exists** — this repository has neither
    implementation code nor a test suite yet. They stay on `CLAUDE.md`'s
    not-yet-adopted list until then.
  - The **governance frontmatter parse** check family arrives with these
    files (rule 2, never-ahead): the skill and agent frontmatter must parse,
    because a malformed skill does not fail — it silently never loads. The
    parse has no standard ecosystem tool, so a few-line custom check is
    sanctioned here. Checking further is a *should*, worth doing only where
    it is exact (an agent name against `.claude/agents/`, a path against the
    tree) and worth refusing where it is not: scanning prose for backticked
    tokens and asserting each resolves is a false-positive machine that
    grows worse as the repository does.
  - Each adoption logged (rule 3, rule 4).
  - **Probes, run at this step because these are this step's mechanisms.**
    Whether an agent's `tools:` frontmatter restricts anything at all; and
    **whether `CLAUDE.md` reaches a subagent's context at all** — one
    exchange with the first agent this step spawns ("quote rule 9's opening
    line"), never the bootstrap cold reviewer, whose context must stay
    confined to the specifications and the six governance files. Every
    reviewer agent's boundary rests on that answer. **Pre-committed
    unfavourable branch:** if `CLAUDE.md` does not reach a subagent's
    context, each agent's body carries the gated set **inlined** — a logged
    decision naming the single-source-of-truth cost — never a citation to a
    rule the agent cannot read. Results land in the `.claude/docs/`
    measurements file with their version, method and re-measure recipe.
    `.claude/rules/` is probed only if a step ever adopts a rules file; none
    does today.
- **How I test it.** Free and local. **A new skill or agent may only be
  picked up at session start, so restart the session (or `/clear`) before
  testing.** Then invoke `/orient` and see the session-routine report;
  invoke `/resume-step` and see it verify against git rather than the
  transcript; read `/handover-step` and `/approve-step` and confirm every
  command they name exists and runs; confirm the probe results in
  `.claude/docs/`. `just check` covers the new frontmatter family.
- **Status.** `pending`

### step-003 — The same harness on the forge — `pending`

- **Objective.** CI running `step-000`'s entry points on GitHub Actions —
  the step that finishes the bootstrap.
- **Spec sections implemented.** §2.8 (the idle-schedule fact, honoured by
  *not* inventing a schedule here), §8 in part (the forge is GitHub; this
  step establishes the workflow ground the image jobs later build on).
- **Depends on.** `step-000` (the entry points), `step-002` (the tooling the
  workflow's own lint covers).
- **Deliverables.**
  - A GitHub Actions workflow that **reuses `step-000`'s entry points**
    rather than restating a single check — CI and the local runners must
    never be able to disagree about what "green" means.
  - Check and test as **separate jobs once both exist**; the toolchain
    cached.
  - A way of proving a **fresh setup** still works. That proof may later
    ride a scheduled job the specification already requires (§8's refresh
    and update detection) rather than becoming a second scheduled workflow
    of its own — but none of those jobs can exist at this step, so until
    they do, **CI's own per-run fresh setup** (a clean checkout plus the
    documented setup command) is the proof, and the §8 schedule takes the
    duty over when it arrives. **Do not invent a temporary schedule now**
    (§2.8 is why an unnecessary schedule is a liability, not a freebie).
  - The workflow-validation check family arrives with this, the first
    workflow file (rule 2, never-ahead).
  - The forge is settled: GitHub (§8, §2.8).
- **How I test it.** **This is the one foundation step nothing local can
  exercise, so its gate is a real run.** External prerequisites needed *at
  bootstrap*, not late: the GitHub repository and its remote (verified
  present: `git@github.com:yannlugrin/docker-game-servers.git`,
  **public**), and the operator's authorisation of the first push. The
  workflow stays **unverified** until that push is authorised and the run
  comes back green. Test: authorise the push, then watch the Actions run
  (`gh run watch`). Cost: a GitHub write (the push) plus Actions minutes —
  free on a public repository. Cleanup: none; a failed run is fixed
  forward.
- **Status.** `pending`

*Nothing in this milestone is exempt from the small-step rule. If any of
the four is still too big for a single test, it is split further in this
plan rather than defended.*

---

## Milestone 2 — The steamcmd builder image

§3.1's build direction gives the spine: the builder precedes any game
image.

### step-004 — The builder image — `pending`

- **Objective.** A working, minimal steamcmd builder image, built locally,
  usable on its own as a generic "install a Steam app" builder.
- **Spec sections implemented.** §4.1–§4.4, §3.1 (the shared Debian 13 slim
  base), §2.1 (32-bit glibc, certificates, linux/amd64 only), §2.2
  (steamcmd self-updates; pre-warmed at build time), §5.8 in part (the
  builder's own OCI annotations: source, description, license).
- **Depends on.** `step-000`.
- **Deliverables.**
  - A Dockerfile on `debian:13-slim` (`trixie-slim`) with a working
    steamcmd, **already run once at build time** so its self-update is baked
    into the layer (§4.2) — otherwise every consumer's first build step
    re-downloads the steamcmd runtime.
  - Nothing beyond steamcmd's needs: certificates, 32-bit libraries. No
    editors, no locale packs, no convenience tooling (§4.4) — every
    megabyte here is inherited by every game build's cache.
  - The ability to install a given app id from a given branch (including
    password-protected beta branches) with anonymous login, and Steam file
    validation (§4.3). For non-anonymous apps the design must not preclude
    build-time credentials, and the guarantee is channel-neutral: a
    credential **never persists in a layer or in the image's build
    history** — which rules out a plain build argument or a baked
    environment variable (§4.3, §10.4).
  - The **Dockerfile lint** family arrives with this, the first Dockerfile
    (rule 2, never-ahead).
  - **Measurements** that §2.9 ordered taken at implementation, recorded in
    `.claude/docs/`: the base image's own size and the builder's size on top
    of it — the evidence for or against "Debian slim is the smallest
    workable base". A result that moves the expectation moves the named
    consequence, not the architecture (§2.9); a result that changes a
    requirement comes back to the operator first.
  - A local build recipe in the justfile (no gated act — rule 2's
    invariant).
- **How I test it.** Free and local, but not instant: building runs
  steamcmd, which downloads its own runtime from Steam (anonymous steamcmd
  downloads are free per rule 9 — tens of megabytes here, not the
  gigabytes a game build pulls). Build it (`just builder-build`), read the
  reported size, then run an **anonymous metadata query** inside it
  (`+login anonymous +app_info_print 380870 +quit`) and see it complete.
  Cleanup: `docker image rm` the local tag by name (free — this project's
  own artifact).
- **Status.** `pending`

### step-005 — The builder image README — `pending`

- **Objective.** The builder's per-image documentation, which is also its
  GHCR page.
- **Spec sections implemented.** §9 (per-image README), §4.1 (**it is not a
  runtime image and its documentation must say so**), §7 (the builder's
  date-stamped tag policy), §11 (the no-general-purpose-runtime-steamcmd
  non-goal, stated where a reader would otherwise assume otherwise).
- **Depends on.** `step-004`.
- **Deliverables.** A README for the builder image covering: what it is and
  what it is **not**; how to use it as a build stage and standalone; the app
  id / branch / validation interface of §4.3 and the credential
  non-persistence rule; the date-stamped tag scheme plus moving `latest`,
  and that consumers pin a date tag or digest (§7); platform-neutral
  throughout (§9's last bullet). The per-image README table shape of §9
  applies as far as it is meaningful for a non-runtime image — a builder has
  no ports, no state root and no shutdown semantics, and says so rather than
  shipping empty sections.
- **How I test it.** Free and local. Read it; follow its standalone example
  against the locally built image and see the documented result.
- **Status.** `pending`

### step-006 — Builder publication on CI — `pending`

- **Objective.** The builder published to GHCR by CI, gated, with the tag
  scheme §7 requires.
- **Spec sections implemented.** §7 (builder date tags `YYYYMMDD`, ordinal
  suffix `YYYYMMDD.1` for a same-day rebuild so no immutable tag is ever
  reused; moving `latest`; linux/amd64 only, no architecture suffix), §8
  (on-demand builds; **builder publishes get a minimal gate of their own** —
  the built image must run steamcmd to completion on an anonymous metadata
  query before the date tag is pushed), §2.6 (GHCR, anonymous pulls, native
  Actions integration; the one-time per-package visibility flip; the Docker
  Hub anonymous-pull rate limit, **decided deliberately here** — mirror,
  authenticated pulls, or accept the risk — rather than after the first
  failed build), §5.8 (the builder's annotations as published).
- **Depends on.** `step-003` (CI exists), `step-004`, `step-005`.
- **Deliverables.** A manually triggered publish workflow; the date-tag
  computation including the ordinal-suffix rule; the anonymous-metadata gate
  before the push; the never-reuse enforcement of §7 applied to date tags
  (a publish that would overwrite an existing immutable tag **fails the
  job**); the §2.6 base-pull decision, logged; the GHCR namespace recorded
  (`ghcr.io/yannlugrin`, subject to the operator's confirmation).
- **How I test it.** **Crosses the boundary.** The operator authorises the
  workflow dispatch (a GitHub write) and the resulting **publish to GHCR**;
  then flips the new `steamcmd` package to public visibility — a one-time
  manual step only the owner can do (§2.6, §8), without which CI goes green
  while no consumer can pull. Verify with an anonymous pull from a
  logged-out client (`docker logout ghcr.io` first). Then dispatch a second
  run the same day and see `YYYYMMDD.1`, and a third contrived attempt at an
  existing tag and see the job **fail**. Cost: Actions minutes (free,
  public) and GHCR storage (free, public). Cleanup: none — published
  builder tags are retained deliberately (§7). Development iterations before
  this step, if any are pushed at all, use the non-release namespace of §7
  and may be pruned.
- **Status.** `pending`

---

## Milestone 3 — Game image automation

Everything here needs a complete game image to build and to gate, so the
milestone opens only when the `pz` track has delivered one. Ordered so that
nothing goes live before its day-two operations exist: the smoke gate
precedes the first release publish, and update detection precedes the
refresh that depends on the same comparison.

### step-007 — Game build workflow, development namespace only — `pending`

- **Objective.** CI can build the Project Zomboid image and publish it
  under a namespace that carries none of §7's promises.
- **Spec sections implemented.** §8 (on-demand builds: a manually triggered
  workflow that builds a chosen image; the branch its per-game
  specification declares, whose *current* content determines the version;
  pushes and pull requests that touch an image's sources get a
  build-and-smoke run **without publishing**, and where a test genuinely
  needs a pullable image it publishes under the development namespace), §7
  (**development builds never consume the release namespace** — mutable,
  prunable, excluded from the never-reuse rule and the moving pointers, and
  absent from consumer documentation).
- **Depends on.** `step-006`; `step-pz-012` done (labels and the published
  builder digest pin).
- **Deliverables.** The workflow, its game/branch inputs, the development
  tag naming (visibly not a release tag), and the path filters that decide
  which pushes trigger a build.
- **How I test it.** **Crosses the boundary.** The operator authorises a
  workflow dispatch; the run builds the image (a multi-gigabyte Steam
  download on GitHub's runners, no local cost) and publishes a `dev-` tag.
  Verify the tag exists and carries no `-rN`. Cleanup: development tags are
  prunable — delete the package version afterwards if wanted (a registry
  delete is a gated act; ask).
- **Status.** `pending`

### step-008 — The smoke-test gate — `pending`

- **Objective.** The §8 gate that stands between a built game image and any
  publish, asserting the silent-failure path of §5.6 before the image
  reaches anyone.
- **Spec sections implemented.** §8 (the smoke test in full), §5.6 (the
  stop path it asserts), §5.5 (healthy within a **stated bound**, past which
  the gate fails rather than hangs), §5.1 and §3.4 (read-only rootfs and
  arbitrary non-root uid exercised rather than trusted).
- **Depends on.** `step-007`; `step-pz-011` done (the healthcheck) and
  `step-pz-010` done (stop mediation).
- **Deliverables.** A gate that starts the built image on the image's
  **default configuration profile** with only the documented mandatory
  variables supplied, waits for healthy within the stated bound, sends the
  stop signal, and requires **exit 0**; runs under an **arbitrary non-root
  uid** with a root filesystem as read-only as the image's own
  documentation claims — writable mounts exactly at the documented paths (an
  image whose per-game specification states a reasoned deviation is tested
  against its own documented writable set). Where a supported alternative
  profile switches the healthcheck onto a different code path — PZ's
  non-Steam profile (PZ §6) — that profile **should** be exercised too.
  External connectivity, Steam included, is a permitted dependency of the
  gate. **A build that cannot pass this does not publish.** The gate is
  written so the local harness can run it too (`just`), because a gate only
  CI can run is one nobody debugs.
- **How I test it.** Two halves. Locally and free: run the gate against a
  locally built image and see it pass, then break it deliberately (mount the
  state root read-only, or shorten the stop timeout below the save) and see
  it **fail with an attributable message** rather than hang. Then, crossing
  the boundary: authorise a dispatch and watch CI run the same gate.
  Cleanup: `docker rm`/`docker volume rm` this project's own test
  containers and volumes by name (free); never a prune.
- **Status.** `pending`

### step-009 — Release publication and tag policy — `pending`

- **Objective.** The `-rN` release stream, its moving pointers, and the
  never-reuse enforcement that protects them.
- **Spec sections implemented.** §7 in full for game images (immutable
  `<game-version>-rN` with `N` starting at 0; the moving `<game-version>`
  and `latest`; **"newest" decided by publication order of new-version
  builds, not by parsing version strings**; a rebuild at unchanged version
  *and* unchanged buildid is a legitimate revision bump; no branch axis;
  the buildid-derived fallback where a game exposes no machine-readable
  version string; superseded immutable tags **retained indefinitely** — no
  cleanup job may delete them), §8 (the revision tag computed against what
  the registry already holds, never overwriting; first publish is not fully
  automatic), §5.8 (the labels the computation reads and writes), §2.6 (the
  visibility flip).
- **Depends on.** `step-008` (the gate must precede the first release).
- **Deliverables.** The version/revision computation reading what the
  registry holds; **enforced-loudly-at-publish** never-reuse (a publish that
  would overwrite an existing immutable tag — a lost race between two build
  triggers, a recomputed revision — **fails the job, never proceeds**); the
  moving-pointer updates; the publication-order record that decides "newest"
  without parsing version strings; fixtures for the computation, including
  the cases that must fail.
- **How I test it.** Locally and free: run the computation's fixtures,
  including a contrived existing-tag collision, and see it refuse. Then
  **crossing the boundary**: the operator authorises the first release
  publish, then **flips the `project-zomboid` package to public
  visibility** (§2.6, §8 — only the owner can). Verify `-r0` exists, the
  moving tags point at it, an anonymous pull works, and a second run at the
  same content produces `-r1` rather than moving `-r0`. Cost: GHCR storage,
  free and public, **retained deliberately and permanently** — this is the
  first tag consumers may pin. Cleanup: none, by design.
- **Status.** `pending`

### step-010 — Scheduled update detection — `pending`

- **Objective.** A new Steam buildid becomes a published image without
  human action.
- **Spec sections implemented.** §8 (scheduled update detection), §2.3
  (buildid queryable without downloading — what makes this possible), §5.8
  (the buildid label as the machine-readable side of the comparison), §7
  (a changed version string as a new version tag, an unchanged one as a
  revision bump).
- **Depends on.** `step-009`.
- **Deliverables.** A periodic job comparing each game's current Steam
  buildid against the buildid label of the newest published **release**
  image — never a development tag, whose newer buildid would otherwise
  silently suppress a release publish — and, on **any** buildid change,
  building and publishing automatically. A comparison that **cannot be
  established** (Steam unreachable, a newest image without a parseable
  buildid label) **fails the job loudly and is never treated as "no
  change"**: a green job that has stopped comparing is a detector that
  silently died.
- **How I test it.** Locally and free: run the comparison against the real
  registry and Steam (GitHub API reads and Steam metadata queries are free
  per rule 9) and see it report "no change"; then force the unestablishable
  case (point it at a tag with no buildid label) and see it **fail rather
  than pass**. Then **crossing the boundary**: authorise one dispatch of the
  scheduled workflow and watch it decide correctly. Cleanup: none unless it
  publishes; if it does, the tag is a legitimate release and is retained.
- **Status.** `pending`

### step-011 — Scheduled refresh, builder pin advance, staleness check — `pending`

- **Objective.** The only path by which security patches reach baked game
  images, and the deactivation-resistance §2.8 demands of it.
- **Spec sections implemented.** §8 (the scheduled refresh as **one flow**;
  the in-repo staleness check; superseded game versions never re-patched),
  §3.1 (the pinned builder reference, which **only moves by this
  deliberate, automated act** — that is what makes it a pin rather than a
  moving pointer in disguise), §2.8 (idle scheduled workflows are disabled
  after ~60 days in a public repository), §10.7 (named as deferred, with
  the blind spot stated rather than hidden).
- **Depends on.** `step-010`.
- **Deliverables.** One flow that publishes a fresh builder date tag,
  **advances the pinned builder reference** the game builds use, and
  rebuilds every game image against the refreshed base and builder. The pin
  advance becomes final **only when the game rebuilds succeed** — a failed
  refresh leaves or restores the previous working pin, or a broken builder
  blocks every later on-demand build, urgent ones included. Each rebuilt
  image's tag follows §7's mapping. Plus the **in-repo staleness check**
  that runs whenever anything else triggers CI and fails loudly when the
  refresh is overdue — the honest interim accepted deliberately, whose
  blind spot (an idle repository whose deactivation notice goes unread) is
  documented and closed later by §10.7's external watchdog. The cadence is
  this implementation's choice and is logged; the mechanism is not.
- **How I test it.** Locally and free: run the staleness check with a
  contrived old timestamp and see it fail loudly; run the pin-advance logic
  with a failing game rebuild and see the **previous pin survive**. Then
  **crossing the boundary**: authorise one dispatch of the refresh and watch
  a new builder date tag, an advanced pin, and rebuilt game images. Cost:
  Actions minutes, a multi-gigabyte rebuild on GitHub's runners, GHCR
  storage. Cleanup: none — the results are legitimate releases.
- **Status.** `pending`

---

## Milestone 4 — Repository-wide documentation

Written after one game has been walked through, so the conventions are
described as they were actually honoured rather than as they were planned.

### step-012 — The repository README's content requirements — `pending`

- **Objective.** `README.md` satisfies §9's repository-README
  requirements, on top of the neutral entry point it already is.
- **Spec sections implemented.** §9 (repository README: project scope,
  image inventory, **the shared conventions of §5 stated once** — per-image
  docs link here rather than restating them; platform-neutral throughout),
  §1 (scope and the platform-neutrality rule), §5 (the conventions
  summarised in one place), §11 (non-goals worth a reader's attention),
  §7 (tag policy pointed at rather than restated).
- **Depends on.** `step-pz-013` done (the PZ README exists and links here).
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
  per-game specification to write **first**, and its minimum contents),
  §5 (the checklist itself), §10.5 and §10.6 (more games, non-Steam games —
  the shape the guide has to leave room for), §3.3 (a game image is mostly
  convention plus a small delta).
- **Depends on.** `step-012`; the whole `pz` track (the guide describes a
  path actually walked).
- **Deliverables.** `docs/adding-a-game.md` (human-facing — never
  `.claude/docs/`): the per-game specification first, then the §5
  checklist convention by convention, the track registration of rule 6
  (directory, step-id prefix, plan, log), and what CI needs from a new
  game. Written from what the `pz` track actually did, not from the
  specification alone.
- **How I test it.** Free. Read it against `project-zomboid/` and check
  that every convention the PZ image honours appears as a checklist item,
  and that nothing in it is PZ-specific without saying so.
- **Status.** `pending`

---

## External prerequisites

Things only the operator can prepare, each with the step that first needs
it.

| Prerequisite | First needed | State |
|---|---|---|
| **Step-tag namespace collision.** Tags `step-000` and `step-001` already exist in this repository, from an earlier attempt whose history lives on `main`; this branch (`handoff-3`) is an unrelated root commit, so they are unreachable from `HEAD` but the **names are taken** and `git tag step-000` will fail at the first close. The operator decides: delete the old tags, or rename them out of the `step-*` namespace, or something else. `git describe --match 'step-*'` already behaves correctly (it finds nothing, which rule 3 reads as "before the first step tag"); `git tag -l 'step-*'`, which the rituals also use, does not. | `step-000` close | **Open — operator decision needed before the first step close** |
| Public GitHub repository and its remote | `step-003` | **Satisfied**: `git@github.com:yannlugrin/docker-game-servers.git`, public, default branch `main`. The relationship between `main` and `handoff-3` is the operator's call (see above). |
| Authorisation of the first push | `step-000` close (rule 6 attempts a push at every close); mandatory at `step-003` | Open |
| GHCR owner namespace (§7) | `step-006` | Expected `ghcr.io/yannlugrin`; **operator to confirm** |
| One-time per-package visibility flip at first publish (§2.6, §8) | `step-006` (`steamcmd`), `step-009` (`project-zomboid`) | Open — only the owner can do it; without it CI goes green while no consumer can pull |
| A registry credential, **conditionally** — only if §2.6's Docker Hub anonymous-pull rate limit is resolved via authenticated pulls rather than a mirror | `step-006` (the first CI build that pulls the Debian base) | Conditional; the decision itself is `step-006`'s |
| Bandwidth and disk for the multi-gigabyte Project Zomboid download | `step-pz-001` | Measured today: 948 GB free on this machine |

## Coverage map — root `SPECIFICATIONS.md`

Every section appears in at least one step, or below with the reason it is
excluded.

| Section | Step(s) |
|---|---|
| §1 Goal | `step-012` (scope and platform-neutrality as documentation); binds every image step |
| §2.1 steamcmd is 32-bit glibc; amd64 only | `step-004` |
| §2.2 steamcmd self-updates, no versions | `step-004` (pre-warm), `step-006` (date tags) |
| §2.3 app ids, branches, buildid | `step-004`, `step-010` |
| §2.4 PID 1 signal semantics | `step-pz-007`, `step-pz-010` (`pz` track) |
| §2.5 Steam query protocol | `step-pz-003`, `step-pz-011` (`pz` track) |
| §2.6 Registry: GHCR, visibility flip, Docker Hub rate limit | `step-006`, `step-009` |
| §2.7 `steamclient.so` at runtime | `step-pz-001` (`pz` track) |
| §2.8 Idle scheduled workflows disabled | `step-003` (no schedule invented), `step-011` (staleness check) |
| §2.9 What §2 is least sure of — the measurement items | `step-004` (base and builder sizes), `step-pz-001` (PZ `steamclient.so` resolution), `step-pz-002` and `step-pz-003` (§5.5 client sizes) |
| §3.1 Two tiers, one base, pinned builder reference | `step-004`, `step-006`, `step-011`, `step-pz-001`, `step-pz-012` |
| §3.2 Baked at build time | `step-pz-001` |
| §3.3 One repository, one set of conventions | `step-012`, `step-013` |
| §3.4 uid-agnostic; no default user; uid-0 fatal; `ALLOW_UID0`; complete writable-path set | `step-pz-001`, `step-pz-007`, `step-pz-005` (writable set), `step-008` (exercised) |
| §3.5 The entrypoint is the adapter | `step-pz-007` and the `pz` entrypoint steps |
| §4.1–§4.4 The builder image | `step-004`, `step-005` |
| §5.1 Filesystem and state | `step-pz-001`, `step-pz-005` |
| §5.2 Ports | `step-pz-003`, `step-pz-010`, `step-pz-013` |
| §5.3 Configuration | `step-pz-008` |
| §5.4 Secrets | `step-pz-008`, `step-pz-009` |
| §5.5 Observability | `step-pz-005` (logs), `step-pz-011` (health, clients) |
| §5.6 Lifecycle and shutdown | `step-pz-010`, `step-008` (gate) |
| §5.7 Backup knowledge | `step-pz-006`, `step-pz-013` |
| §5.8 Image metadata | `step-pz-012`, `step-004`/`step-006` (builder labels), `step-010` (buildid label read) |
| §6 Per-game specifications | The `pz` track exists because of it; `step-013` states the rule for future games |
| §7 Versioning and publication | `step-006` (builder), `step-009` (game), `step-011` (refresh mapping) |
| §8 Build automation | `step-003`, `step-006`, `step-007`, `step-008`, `step-009`, `step-010`, `step-011` |
| §9 Documentation deliverables | `step-005`, `step-012`, `step-013`, `step-pz-013`; **LICENSE (MIT) already exists at the repository root — verified, no step needed** |

**Deliberately not implemented in this pass:**

- **§10 Future Considerations** (§10.1 Wine/Proton, §10.2 arm64, §10.3
  mod-baked variants, §10.4 non-anonymous games, §10.5 more games, §10.6
  non-Steam games, §10.7 external refresh watchdog) — the section's own
  instruction is "not built now; nothing in the present design may preclude
  them". Each step above respects that; §10.7 is named in `step-011` as the
  deferred closure of a stated blind spot, and §10.4's requirement on the
  builder (credentials that never persist) *is* implemented, at `step-004`.
- **§11 Non-Goals** — conscious renunciations, nothing to build. They are
  documented where a reader would otherwise assume otherwise: `step-005`
  (no runtime steamcmd image), `step-012` (the rest).

## Open facts owned by this track

§2.9's measurement items, one by one. Root §2.9's third item — each game's
`steamclient.so` resolution — is per-game and is owned by the `pz` plan.

| Open fact | Settled at | Pre-committed response |
|---|---|---|
| The ~megabytes cost of the §5.5 clients (Steam-query client, RCON client) | `step-pz-002` (RCON), `step-pz-003` (Steam-query) | Autonomous if the size only confirms the expectation; a client costing tens of megabytes is a §5.5 "should" deviation — logged, and back to the operator if it changes what the image documents |
| Debian slim as the smallest workable base (the base-size expectation) | `step-004` | A measurement that moves the expectation moves the named consequence, not the architecture (§2.9). A result implying a different base is a §3.1 **requirement** change — back to the operator |
| steamcmd's undocumented behaviour (self-update format, anonymous-login scope) may shift under Valve's control | `step-004`, re-observed at every `step-011` refresh | Already absorbed by design: the builder is date-stamped and pre-warmed rather than assumed stable |

## Open questions for the operator

1. **The step-tag collision, and what `handoff-3` is for.** The prerequisite
   table states the mechanical problem. Behind it is a question this plan
   cannot answer: is this branch intended to replace `main` (whose history
   holds an earlier attempt at steps 000–002), to merge into it, or to live
   beside it? The answer changes what the first close does and whether the
   old tags may be deleted. I have deliberately not read that earlier
   attempt's implementation — but its tag messages were unavoidably visible
   while inventorying the `step-*` namespace, so I have seen a handful of
   its measurements (a setup time, a `pre-commit --all-files` finding, a
   `check-added-large-files` flag). Say whether that history is input I may
   use or a dead end I should ignore; until you do, I will treat it as
   unverified hearsay and measure everything myself.
2. **Milestone 3's dependency on the `pz` track is heavy.** Steps 007–011
   cannot start until the PZ image is complete, which means a long stretch
   of `pz`-track work with no root-track progress. That is what the
   dependencies dictate, and splitting CI earlier would mean gating
   workflows against an image that cannot yet report healthy or stop
   cleanly. Flagged so the sequencing is a choice rather than a surprise.
3. **`step-008`'s local half assumes the gate is runnable outside CI.**
   Writing it that way costs a little (it must not depend on Actions-only
   context) and buys a debuggable gate. If you would rather have the gate
   exist only in CI, say so — it removes the local half of that step's
   test.
4. **The §2.6 Docker Hub decision is `step-006`'s to make, but the choice
   is partly yours**: a GHCR mirror of the Debian base costs a little
   machinery and no credential; authenticated pulls cost a credential you
   have to supply. I will propose the mirror unless you prefer otherwise.
5. **Cadence numbers are unset on purpose.** §8 leaves the refresh cadence
   and the staleness threshold to the implementation; I will propose them at
   `step-011` with reasons rather than fixing them here, where they would be
   a number nobody has thought about since.
6. **`CLAUDE.md` does not fit its 220-line budget, and I am raising that
   rather than packing the file** (rule 3 says to). It stands at **297
   lines** (18.6 KB): the eleven rules take **185** — rule 9's boundary
   enumeration alone is **35** and must be carried whole — and the sections
   the workflow requires by name take **112** (session routine, layout, track
   map, plan conventions, the temporary templates block, `Current state`).
   I have already applied rule 3's eviction order: there is no
   context-specific matter left that a `.claude/docs/` read-trigger could
   reach, the templates block is down to its three mandated items with the
   instantiation detail moved into `step-002`'s entry here, and per-track
   detail (the open-facts escalation list above all) now lives in the plans
   and is cited from `CLAUDE.md` rather than duplicated. What remains is
   operative clauses; the next 77 lines can only come out by deleting rules
   or by deleting a section the workflow names. Two remedies, and the choice
   is yours:
   - **Log a project-specific budget** — I suggest a 320-line cap with a
     ~280 target, which preserves real headroom and the same discipline. This
     is rule 3's own named outcome, logged as a deviation with what makes it
     necessary: a long boundary enumeration carried whole, eleven rules that
     tooling and decision entries cite by number (so renumbering is not
     available as a compression), and six required source-of-truth sections.
   - **Cut scope from the file** — name what may go (candidates, in the order
     I would sacrifice them: the `Where things live` block, since
     `README.md` carries the map; the `Plan conventions` section, if you
     accept that closes are driven from the plans' own headers instead).
     Both cost something real, which is why I am not choosing.
   Until you rule, `CLAUDE.md`'s rule 3 states the overshoot in the file
   itself and points here, so no session mistakes it for compliance.
