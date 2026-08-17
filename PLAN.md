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

### step-000 — The harness skeleton, local only — `in progress`

- **Objective.** A repository that can check itself, locally, from a fresh
  clone: pinned dependencies behind one setup command, and the
  check/test/verify entry points of rule 2 — carrying only the check
  families whose artifacts already exist.
- **Spec sections implemented.** None directly — this step is rule 2's
  harness, not specification content.
- **Depends on.** Nothing.
- **Deliverables.**
  - `.gitignore`, rewritten with rule 5 in mind: local test-state roots and
    volume directories; env files carrying test credentials; tool caches;
    game content downloaded outside an image build; `CLAUDE.local.md`;
    `.claude/reviews/` (the reviewer agents write reports there and assume it
    is ignored — an untracked report otherwise blocks every clean-tree
    precondition downstream); and `.claude/worktrees/`, which the current
    `.gitignore` already carries and **must survive the rewrite** — a commit
    made while an agent worktree exists otherwise swallows its checkout.
  - Pinned base dependencies, installable through **one documented setup
    command**. The measured toolchain state of this machine goes in
    `.claude/docs/environment.md` — the first `.claude/docs/` file, with each
    figure's date and a re-measure recipe — not into this plan or
    `CLAUDE.md`, neither of which has staleness discipline. What matters to
    the design: `pre-commit` and every linter are absent and the setup
    command must install them, while `pip` and the `venv` module are
    available. Which bootstrap it uses is a logged workflow decision
    (rule 4).
  - The rule-2 harness, **configured rather than written**: the
    **`pre-commit` framework** (<https://pre-commit.com>) as the hook
    runner — **the tool of that name, not merely git hooks** — and **`just`**
    (<https://github.com/casey/just>) as the task runner, because **this
    stack brings no runner of its own**; each ecosystem's standard linter
    pinned in one place, no house preference.
    - `check` — "is what is committed here well-formed?" — syntax, lint and
      formatting over the working tree, **untracked files included and
      gitignored paths excluded**, with two standing exclusions **settled
      here and not re-litigable**, keyed on the path and not on tracked
      status: everything under `.claude/spec-work/` (rule 1 makes that
      directory no session's reading material) and everything under
      `.claude/refs/` (operator-supplied reference material, read-only under
      rule 3 and owned elsewhere — **not this repository's product to
      lint**).
    - `check` takes a **scope**, **in both of rule 2's forms from the
      start — since every step after this one uses it**: the whole-tree gate
      as the default, and the narrowed what-changed form the development loop
      runs between gates — **one entry point taking a scope, never a second
      recipe**, because two recipes hold two lists of checks and will
      eventually differ in *what* they look for, not only in how much. A fast
      narrowed pass is legitimate mid-step; **the commit that receives a step
      tag runs the full one — that commit is the state every later session
      treats as known-good.**
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
      correct state**, not a gap to fill — which is exactly its state at this
      step.
    - `verify` — runs both.
    - The same harness wired into the **commit hooks**, so the local runners
      cannot diverge.
  - Check families **only for artifact classes that exist at this step**
    (rule 2's never-ahead rule): JSON well-formedness for
    `.claude/settings.json` — **which is the enforcement mechanism itself, so
    malforming it after `step-002`'s one-time probe fails exactly as quietly
    as a malformed skill that silently never loads**. Markdown structural
    lint may land here where it needs no tuning; the prose lint over the
    governance documents is `step-001`. Dockerfile lint, entrypoint-language
    lint, workflow validation, Python lint and the skill/agent frontmatter
    parse arrive with their first artifact, in the step that lands it — so
    this step's green gate says nothing about files that are not there.
  - Documented commands, runnable by the operator too, listed in
    `README.md`.
  - **The CI workflow is deliberately not in this step** but in `step-005`:
    nothing local can exercise a workflow, and **a tagged step must not carry
    an artifact its own gate never ran**. Adding anything under
    `.github/workflows/` here is out of scope, however convenient the moment
    looks.
- **How I test it.** All free and local. From a fresh clone of this branch
  (`git clone . /tmp/gs-clone`): run the documented setup command; run
  `just check`; make a trivial commit and watch the hook run; run `just
  test` and see it state that the repository ships no behaviour of its own
  yet. Then, in the working tree, create a file with a deliberate JSON error
  and **do not `git add` it** — `just check` must fail on it; delete it.
  Cleanup: remove the clone directory.
- **Status.** `in progress`

### step-001 — The governance and prose lint — `pending`

- **Objective.** The documents this repository runs on are linted, because
  **in this repository documents are load-bearing**.
- **Spec sections implemented.** None — harness.
- **Depends on.** `step-000`.
- **Deliverables.**
  - Prose and markdown lint over **the governance documents themselves —
    the specifications, the plans, the rest** — and the human-facing
    documents, joining `step-000`'s `check` families.
  - **Configured to the documents as they already are.** The specifications
    are read-only under rule 1, so **the lint bends to them and never the
    reverse**; excluding a document from a rule is a **logged decision**
    (rule 4), not a quiet config line.
  - A note in `.claude/docs/` for any repairing hook adopted: a hook that
    rewrites rather than reports means a failing `check` can modify files,
    read-only specifications included — which must be documented rather than
    discovered.
- **How I test it.** Free and local. `just check` passes over the tree as it
  stands — the specifications included, unmodified. Then introduce a real
  prose fault in a plan and see it flagged; revert. Read the logged
  decisions for every rule excluded from a document, and confirm no
  specification file was rewritten by the run (`git status` clean).
- **Status.** `pending`

### step-002 — The permission and hook baseline — `pending`

- **Objective.** Rule 9's boundary enforced mechanically, proposed to the
  operator as one reviewable whole, with every mechanism measured rather
  than assumed.
- **Spec sections implemented.** None — workflow enforcement.
- **Depends on.** `step-000` (the guard's `--liveness` is wired into the
  commit hooks and its `--selftest` into `test`).
- **Deliverables.** The guard decides the shape of the settings, not the
  other way round; the guard lands and is demonstrable before the settings
  half is proposed, so the operator's single review has something working to
  read.
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
  - Every rule **and every grant** added gets a `CASES` entry: `--selftest`
    fails on **a rule or a grant** no case reaches, which is what keeps the
    intent executable rather than remembered — and grants are the carve-out
    half of the registry, the half that widens the surface.
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
    every case, then coverage — **a rule or grant no case reaches fails
    it**. Both are prescribed; the proposal records what `--liveness` costs
    in the commit path, so the split stays a measured choice. **A guard that
    stops working must fail a gate, not fail quietly** — which binds any
    further way the guard might die, not only these two.
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
    `.claude/docs/` file — **never in `CLAUDE.md`**, which has no staleness
    discipline: a version-stamped fact restated in standing instructions
    outlives its version in silence. Every claim carries the version it was
    taken on, the method, and a short re-measure recipe to re-run after a
    Claude Code update. Probe at least: whether the settings keys set here
    are honoured (`autoMemoryEnabled: false` included); which spelling of a
    path rule the file tools actually match; whether the hook is **reached**
    at all; and the three-command liveness check the session rituals of
    `step-004` can run — one command that must run silently, one the guard
    *grants*, and one it must **refuse, naming the rule that read it**. That
    third probe is the only one that says the hook is reached: if it merely
    prompts, the hook is not wired and the `deny` backstop is all that is
    left, while `--selftest` and `--liveness` would still pass — they answer
    whether the file is correct, not whether anything calls it. **Assume
    nothing here, including from this plan:** a mechanism that turns out to
    enforce nothing is a guard on paper, and the failure announces nothing.
    **Whatever the probe finds, what binds is what you keep** — measurement
    beats documented belief, including this plan's.
  - **The permission mode**, named in the proposal and set as a committed
    setting (`permissions.defaultMode`), not left to a per-session choice —
    it decides how much the rest has to carry. This plan names no modes and
    asserts no mode behaviour deliberately: the mode set, and what each mode
    does to an unmatched command, are properties of the installed version —
    **modes exist that prompt, that auto-approve, and that judge by
    classifier and can deny outright: three different answers to what backs
    the guard's silence**. Take the list from the running version and
    **probe the mode proposed**: what an unmatched command does under it, and
    **whether a hook `ask` still prompts** — the close ritual attempts its
    push in reliance on that, and a gate that has stopped gating says nothing
    about it. Set the mode rather than working around it (a mode that
    auto-accepts file edits is what removes the need for a blanket
    `Edit(/**)` allowance), and let it decide whether the mode-disabling keys
    belong in the baseline at all.
  - The step summary reports **what each mechanism actually did, including
    the ones that turned out to enforce nothing**.
  - **Premises to settle by probe before the settings design rests on
    them** (the specification states none of these): that
    `permissions.defaultMode` exists as a key; that a matching `ask` prompts
    even where a hook returns allow; that a denied pattern cannot be
    approved in-exchange; that a hook fails open. Probe first, design second.
- **How I test it.** Free and local. Read the proposal (the registry, the
  settings baseline, the named `deny` list, the proposed permission mode)
  and the `.claude/docs/` measurements file; run `.claude/hooks/bash_guard.py
  --selftest` and see it green; run the three liveness commands from the
  measurements file and observe silence, a grant, and a refusal **naming its
  rule**. The permission baseline is explicitly outside the "should"
  latitude — this step exists to put it to the operator.
- **Status.** `pending`

### step-003 — The reviewer agents — `pending`

- **Objective.** The subagents later steps and every milestone close depend
  on, plus the probes that decide whether their boundary text can be a
  citation or must be inlined.
- **Spec sections implemented.** None — workflow tooling.
- **Depends on.** `step-002` (the agents cite the boundary it enforces).
- **Deliverables.**
  - Instantiated from `.claude/spec-work/handoff/assets/` per rule 3:
    `step-reviewer`, plus the two agents whose trigger is a **certainty of
    this plan** — `state-reviewer` and `optimize-memory`, which a milestone
    close needs to *exist* before it arrives rather than improvised at the
    boundary. A recovery ritual created during the crisis it is needed for is
    too late. **This anticipates need deliberately, and rule 3 settles it:
    what waits is decided by the certainty of the trigger, not by whether the
    trigger has fired yet** — the first milestone close is this milestone's
    own, at `step-005`.
  - The conditionally triggered rest (`code-reviewer`, `test-reviewer`) is
    **proposed only when its trigger exists** — this repository has neither
    implementation code nor a test suite yet. They stay on `CLAUDE.md`'s
    not-yet-adopted list until then.
  - The **governance frontmatter parse** check family arrives with these,
    the first files of their class (rule 2, never-ahead): the frontmatter must
    parse, because a malformed agent does not fail — it silently never loads.
    The parse has no standard ecosystem tool, so a few-line custom check is
    sanctioned here. Checking further is a *should*, worth doing only where
    it is exact (an agent name against `.claude/agents/`, a path against the
    tree) and worth refusing where it is not: scanning prose for backticked
    tokens and asserting each resolves is a false-positive machine that grows
    worse as the repository does.
  - **A template arrives with placeholders on purpose:** a leftover one is
    visible, while a plausible wrong filename is not — so a placeholder is
    filled with a verified real path or left as a placeholder, never guessed
    at. A placeholder whose referent does not exist yet — the state
    reviewer's architecture vocabulary and inspection commands, in a
    repository where nothing is built — is seeded from the specification's
    own vocabulary and kept current under rule 6 as the system materialises.
  - **No instantiated file may name a skill or agent that was not adopted**:
    trim the reference or adopt it, because a dangling name is a ritual that
    silently skips a step. One carve-out: a name on `CLAUDE.md`'s
    not-yet-adopted list is not dangling — it is the documented fallback the
    milestone ritual relies on.
  - Each adoption logged (rule 3, rule 4).
  - **Probes, run at this step because these are this step's mechanisms —
    and the probes are independent, so one passing says nothing about
    another** (pinning them all to the first step would mean probing
    mechanisms that do not exist yet, which reports a pass for nothing).
    Whether an **agent's `tools:` frontmatter** restricts anything at all;
    and **whether `CLAUDE.md` reaches a subagent's context at all** — one
    exchange with the first agent this step spawns ("quote rule 9's opening
    line"). Every reviewer agent's boundary rests on that answer.
    **Pre-committed unfavourable branch:** if `CLAUDE.md` does not reach a
    subagent's context, each agent's body carries the gated set **inlined** —
    a logged decision naming the single-source-of-truth cost — never a
    citation to a rule the agent cannot read. Results land in the
    `.claude/docs/` measurements file with version, method and re-measure
    recipe. `.claude/rules/` is probed only if a step ever adopts a rules
    file; none does today.
- **How I test it.** Free and local. **A new agent may only be picked up at
  session start, so restart the session (or `/clear`) before testing.** Then
  spawn `step-reviewer` over this step's own diff and see it apply
  `README.md`'s review frame and report without modifying anything; read the
  probe results in `.claude/docs/`, including the answer to whether
  `CLAUDE.md` reached the agent. `just check` covers the new frontmatter
  family.
- **Status.** `pending`

### step-004 — The session rituals — `pending`

- **Objective.** The four skills every later step runs, so that orientation,
  resumption, handover and close stop being improvised.
- **Spec sections implemented.** None — workflow tooling.
- **Depends on.** `step-003` (`handover-step` runs the `step-reviewer` agent
  and `approve-step` names the two milestone agents; instantiating the skills
  first would leave dangling names, which the no-dangling-name rule
  forbids), `step-002` (the liveness commands `resume-step` may run).
- **Deliverables.**
  - `orient`, `resume-step`, `handover-step`, `approve-step`, instantiated
    at `.claude/skills/<name>/SKILL.md` per rule 3, every placeholder filled
    with this repository's real commands and paths.
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
    passes at the wrong track, and a state reviewer reading the wrong track's
    plan reports nothing wrong.
  - Where a template's own enumeration of a routine is narrower than the
    rule it claims to execute, **the rule wins** and the enumeration is
    rewritten to match (`orient`'s steps 1–2 against `CLAUDE.md`'s
    multi-track session routine is the known instance).
  - `CLAUDE.md`'s pointer for a resumed session updated from rule 3's
    fallback routine to `/resume-step`, in the same commit (rule 6).
  - Each adoption logged.
- **How I test it.** Free and local. **Restart the session before testing —
  a new skill may only be picked up at session start.** Then **invoke each
  ritual and see it do what it claims**, not read it: `/orient` delivers the
  session-routine report and stops; `/resume-step` verifies the claimed
  state against git rather than the transcript; `/handover-step` hands **this
  very step** over — checks green, staleness sweep, `step-reviewer` over the
  step's diff — which is its natural first use; and `/approve-step` closes
  it once the operator approves, which is also the first exercise of the
  compacted-entry and annotated-tag shape, and of the push attempt rule 6
  makes at a close.
- **Status.** `pending`

### step-005 — The same harness on the forge — `pending`

- **Objective.** CI running the harness entry points on GitHub Actions — the
  step that finishes the bootstrap.
- **Spec sections implemented.** §2.8 (the idle-schedule fact, honoured by
  *not* inventing a schedule here), §8 in part (the forge is GitHub; this
  step establishes the workflow ground the image jobs later build on).
- **Depends on.** `step-000` and `step-001` (the entry points and families
  it runs), `step-004` (the close ritual it will be closed by).
- **Deliverables.**
  - A GitHub Actions workflow, **written from scratch — there is no existing
    workflow of the operator's to copy or adapt** — that **reuses the
    harness entry points** rather than restating a single check: CI and the
    local runners must never be able to disagree about what "green" means.
  - Check and test as **separate jobs once both exist**; the toolchain
    cached.
  - A way of proving a **fresh setup** still works. That proof may later
    ride a scheduled job the specification already requires (§8's refresh
    and update detection) rather than becoming a second scheduled workflow
    of its own — but none of those jobs can exist at this step, so until
    they do, **CI's own per-run fresh setup** (a clean checkout plus the
    documented setup command) is the proof, and the §8 schedule takes the
    duty over when it arrives. **Do not invent a temporary schedule now.**
  - The workflow-validation check family arrives with this, the first
    workflow file (rule 2, never-ahead).
  - Recorded deliberately: this first green run covers **only the harness
    over documents and the guard** — no Dockerfile, no image, no workflow
    but its own. That is what "bootstrapped" means here, and it is why the
    run is worth having before the builder rather than after it.
- **How I test it.** **This is the one foundation step nothing local can
  exercise, so its gate is a real run.** External prerequisites needed *at
  bootstrap*, not late: the GitHub repository and its remote (verified
  present and public), the operator's authorisation of the first push, **and
  a branch topology on which Actions will actually run** — see the
  prerequisites table. The workflow stays **unverified** until the push is
  authorised and the run comes back green. Test: authorise the push, then
  watch the Actions run (`gh run watch`). Cost: a GitHub write (the push)
  plus Actions minutes. Cleanup: none; a failed run is fixed forward.
- **Status.** `pending`

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
