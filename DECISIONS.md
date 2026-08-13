# Decisions — root track

Decision log for repository-wide and cross-track choices (CLAUDE.md
rule 4). Entry format: `D-NNN` id (file order, frozen once assigned,
never reused; ids are per-log — cross-log citations name the file, e.g.
`project-zomboid/DECISIONS.md D-003`), date, plan step, context,
decision, alternatives considered, approved by. Entries citing
not-yet-started steps give number *plus title*.

## D-001 — Adoption of the gated, file-memory workflow with per-track organization

- **Date**: 2026-08-13
- **Step**: bootstrap (pre-`step-000`)
- **Context**: implementation of the two-document specification begins;
  sessions do not persist, so all workflow state must live in versioned
  files, and the operator gates every step.
- **Decision**: adopt the workflow encoded in `CLAUDE.md` rules 1–10:
  read-only specifications with a decision-before-amendment channel;
  one operator-gated step in progress repository-wide; per-track memory
  — three tracks (root `step-NNN`, steamcmd `step-sc-NNN`,
  project-zomboid `step-pz-NNN`), each owning its `PLAN.md` and
  `DECISIONS.md`, cross-track order expressed only as named
  dependencies; annotated `step-*` tags marking approved states; small
  prefixed commits carrying their documentation; secrets never in the
  repository; English files; a persistence budget. Tooling templates
  from `.claude/spec-work/handoff/assets/` are adopted selectively at
  `step-000` (per-adoption entries to follow).
- **Alternatives considered**: a single global plan and log (rejected:
  every session would load every track's context, against rule 3's
  economy); per-track numbering without track prefixes (rejected:
  ambiguous tags and commit subjects); transcript-based continuity
  (rejected outright: transcripts are not versioned, reviewable memory).
- **Approved by**: operator (bootstrap prompt,
  `.claude/spec-work/handoff/PROMPT.md`).

## D-002 — Harness toolchain, entry points and lint scope

- **Superseded by D-006** (same step): the bespoke runner it describes was
  replaced by pre-commit before hand-over. Kept for the reasoning it records.
- **Date**: 2026-08-13
- **Step**: step-000
- **Context**: rule 2 requires a check family for every language and
  artifact the repository ships, each tool pinned, all of it runnable by the
  operator through one documented setup command, locally and in CI.
- **Decision**: `make` is the entry point (`setup`, `check`, `test`,
  `verify`), implemented by POSIX-ish bash in `tools/`. Pins: Python tools
  (yamllint, pymarkdownlnt, ruff, check-jsonschema) by exact version in
  `tools/requirements.txt`, installed into a repository-local `.venv`;
  shellcheck and hadolint by version **and** sha256 in
  `tools/tool-versions.sh`, downloaded to `.tools/bin`. Nine families:
  markdown, yaml, workflows (GitHub schema), compose (`docker compose
  config`), shell (`bash -n` + shellcheck), dockerfile (hadolint), python
  (ruff + byte-compile), json, governance (Makefile parse +
  `tools/lint_governance.py`).
  `make test` is fixture-driven: each case snapshots the tree, plants one
  broken or borderline artifact, and asserts how `check` reacts — must-fail
  cases per family, plus the must-warn case of the CLAUDE.md line budget.
  Scope: `check` sees tracked and untracked files, git drops gitignored
  ones, and three paths are excluded by path — `.claude/spec-work/`
  (rule 1), `.claude/refs/` (operator-supplied, never edited by me, so a
  finding there could not be acted on) and `tools/tests/fixtures/`
  (deliberately malformed inputs). Markdown rule MD013 (line length) is
  disabled: the specifications and reference material are read-only
  documents with their own wrapping, and the lint bends to them (rule 2).
  The toolchain installs for linux/x86_64 only, matching the images'
  linux/amd64 constraint (root §2.1); `make setup` fails loudly elsewhere.
- **Alternatives considered**: linters run from pinned Docker images
  (rejected: slower per run, and it makes the harness unusable while the
  Docker daemon is the thing under repair); `--require-hashes` pip installs
  (rejected for now: transitive-hash maintenance for no gain over exact
  version pins on PyPI); a Node toolchain for markdownlint (rejected: it
  would add a second language runtime to install and pin for one family).
- **Approved by**: implementer (rule 4, workflow choice left to me);
  operator informed at the step-000 gate.

## D-003 — Harness CI workflow shape

- **Date**: 2026-08-13
- **Step**: step-000
- **Context**: root §2.6 makes GitHub Actions the CI, and rule 2 wants the
  same harness to run there; root §2.8 warns that scheduled workflows in a
  public repository are disabled after ~60 idle days.
- **Decision**: one workflow, `.github/workflows/harness.yml`, running the
  same `make setup` / `make check` / `make test` as a local clone. Revised
  to the operator's house style (`infra`, `.github/workflows/ci.yml`): the
  file is `ci.yml`, `check` and `test` are one matrix job with
  `fail-fast: false`, and the weekly proof that setup works from nothing is
  the same jobs with the cache step skipped rather than a third job.
  `cancel-in-progress` is off on main, where a commit's verdict is a
  record.
  `permissions: contents: read` — this workflow never publishes. The
  schedule's own deactivation risk is documented in the workflow and is
  covered by the in-repo staleness check that arrives with the scheduled
  refresh (step-007). Treated as **unverified until the first authorized
  push** (step-002).
  Actions are pinned to major tags (`actions/checkout@v4`), not commit
  shas — deliberately weaker than the toolchain's version+sha256 pins:
  these are GitHub's own first-party actions on a repository that publishes
  nothing from this workflow, and sha pins would need manual bumping for a
  threat this workflow does not carry. Revisit when a workflow gains
  `packages: write` (step-004).
- **Alternatives considered**: a single job doing check and test (rejected:
  the plan asks for separate jobs, and a failed check should not hide a
  failed test); no uncached run (rejected: pins rot silently — a moved
  release asset would only surface on a fresh clone, months later).
- **Approved by**: implementer (rule 4, workflow choice left to me).
  Job contents updated by D-006; the shape (separate jobs, cached, plus an
  uncached weekly run) is unchanged.

## D-004 — Permission and hook baseline

- **Date**: 2026-08-13
- **Step**: step-000
- **Context**: rule 9 draws the action boundary in prose; rule 4 says the
  permission baseline is not within my latitude, so it is proposed rather
  than chosen. Prefix-matched permission patterns cannot express three of
  rule 9's distinctions.
- **Decision**: `.claude/settings.json` carries `allow` (the harness and
  setup command, the local container lifecycle, read-only remote reads, and
  the additive/read-only subset of local git — `add`, `commit`, `tag -a`,
  and the inspection commands), `ask` (everything rule 9 gates: `git push`,
  any registry publish, GitHub writes through `gh`, blanket prunes, and
  state-destroying local git — `commit --amend`, `rebase`, `reset --hard`,
  `clean`, `restore`, branch deletion, `stash`; plus edits to any
  `SPECIFICATIONS.md`, which rule 1 allows only as an agreed amendment),
  and `deny` — reserved for what has no authorized use at all: force,
  mirror and delete pushes, `filter-branch`/`filter-repo`, deleting or
  moving a `step-*` tag, expiring the reflog or `update-ref -d`, reading
  the specification-phase archive outside `handoff/assets/`, and editing
  `.claude/refs/`. A `PreToolUse` guard hook (`.claude/hooks/guard.py`)
  covers what patterns cannot: the `gh api` read/write split by method and
  fields, flags that appear late in a line (`git commit … --amend`,
  `docker … prune` without a scoping filter, `curl -X POST`), and the
  spec-work read ban for shell commands as well as file tools. The hook
  denies, asks, or stays silent so the permission rules decide; an internal
  error in it becomes an ask, never a silent allow.
  Two deliberate asymmetries: the settings `ask` on prunes fires even for
  filter-scoped ones that rule 9 makes free (the hook stays silent there) —
  erring toward one prompt rather than a host-global mistake; and
  `Bash(git commit:*)` stays allowed with the hook asking on `--amend`,
  because the alternative is a prompt on every commit of every step.
- **Verified at this step** (probes, detail in `.claude/docs/permissions.md`):
  the settings layer binds and resolves relative paths from the project
  root; the hook binds live in a running session and its verdicts are
  asserted by `make test` on every spelling that matters; `Write(path)`
  rules never fire — `Edit(path)` covers all file-editing tools; skills and
  agents are only picked up at session start. Not verifiable from here:
  that a hook `ask` visibly overrides an allow-listed prefix — that needs
  the operator's own session.
- **Alternatives considered**: patterns only (rejected: a bare `git commit`
  allowance silently admits `--amend`, and `gh api` cannot be split at
  all); hook only (rejected: patterns are the mechanism the harness enforces
  first and the operator can read at a glance); denying more broadly
  (rejected: `deny` with no override forces settings edits mid-step, so it
  stays reserved for the genuinely never-authorized).
- **Approved by**: operator — pending review at the step-000 gate; this
  entry is the proposal.

## D-005 — Workflow tooling adopted at step-000

- **Date**: 2026-08-13
- **Step**: step-000
- **Context**: nine starter templates were handed over; CLAUDE.md's
  tooling block schedules the four rituals and the pre-handover reviewer
  for this step, the rest on their trigger.
- **Decision**: instantiate `/orient`, `/resume-step`, `/handover-step`,
  `/approve-step` and the `step-reviewer` agent, with placeholders resolved
  to the per-track shape (each ritual carries the three-track map and reads
  the pointer in CLAUDE.md's "Current state"), the harness placeholders to
  `make check` / `make test` / `make verify`, and `step-reviewer`'s
  never-run list to rule 9's whole gated set. Deviation from the templates:
  their `when_to_use` frontmatter key is folded into `description` and
  restated as a "When to use" line in the body — Claude Code's skill
  frontmatter defines `name`, `description` and `allowed-tools`, and a key
  it does not define is a loading risk for no benefit; the content is kept
  verbatim in the two places that are read. `optimize-memory`,
  `state-reviewer`, `code-reviewer` and `test-reviewer` remain not adopted;
  the governance check fails any file that names one as if it existed.
- **Alternatives considered**: adopting all nine now (rejected: an agent
  adopted before its trigger is unreviewed weight); keeping `when_to_use`
  (rejected: unverifiable benefit against a real risk of the skill not
  loading).
- **Approved by**: implementer for the instantiation details (rule 4);
  the adoption set itself follows CLAUDE.md's tooling block.

## D-006 — The harness is pre-commit, not a runner of my own

- **Date**: 2026-08-13
- **Step**: step-000
- **Context**: the first implementation of rule 2's harness was ~600 lines
  of bespoke shell — a runner, a file-discovery library, a binary installer
  with sha256 pins, a fixture-driven test driver — to orchestrate tools that
  a standard runner already orchestrates. The operator rejected it as
  over-engineered.
- **Decision**: `.pre-commit-config.yaml` is the harness. One pinned
  `requirements.txt` at the root is the single source of tool versions;
  hooks run those tools from `.venv` (`language: system`), so nothing is
  pinned twice. `make setup` builds the venv and installs the git hook,
  `make check` runs pre-commit over tracked **and** untracked files
  (`--files "$(git ls-files -co --exclude-standard)"`, because
  `--all-files` reads the index and would skip a never-added file),
  `make test` runs pytest, `make verify` is both. Excluded by path:
  `.claude/spec-work/` (rule 1) and `.claude/refs/` (never edited by me).
  Only two pieces of our own code survive, each with tests:
  `tools/governance.py` (the workflow's own state — pointers, budgets,
  frontmatter, names that resolve) and `.claude/hooks/guard.py` (rule 9's
  boundary, which rule 9 itself requires). Hooks now: markdown, yaml,
  workflow schema, ruff, ruff-format, governance. Shell, Dockerfile and
  compose checks are added when the first such file arrives — a family for
  an artifact the repository does not ship yet is scaffolding, not coverage.
- **Alternatives considered**: keeping the bespoke runner (rejected by the
  operator, rightly — every part of it was a reimplementation); pre-commit
  with remote hook repos instead of `language: system` (rejected: versions
  would be pinned in two places, and the operator asked for one root
  requirements file); dropping pre-commit and calling linters from the
  Makefile (rejected: then the git hook, file-type dispatch and staged-file
  runs go back to being mine to write).
- **Approved by**: operator (this exchange).

## D-007 — Governance checks reduced to memory consistency

- **Date**: 2026-08-13
- **Step**: step-000
- **Context**: the first `tools/governance.py` listed the three tracks by
  hand (a new game meant editing it) and asserted that every backticked
  token in CLAUDE.md, the README and the tooling resolved to a real path,
  skill or agent. The operator's objection: a script that must be
  maintained per image, and a heuristic broad enough to start reporting
  things that are not wrong.
- **Decision**: plans are discovered (`PLAN.md`, `*/PLAN.md`) instead of
  listed — a new game track edits nothing. What is checked is what is exact
  and what costs a session when wrong: CLAUDE.md's line budget, the Current
  state pointer agreeing with the plan that declares that step, one step in
  progress repository-wide, settings parsing with auto memory off, and
  skill/agent frontmatter being loadable. No tests: the repository ships no
  behavior of its own yet, and testing a lint script's own assertions is
  weight without a reader. `make test` says so until the first image smoke
  test gives it something real to run (root §8).
- **Open with the operator**: the backticked-reference check is *not*
  removed yet, because CLAUDE.md rule 2 requires it in those words ("every
  named command/path/agent resolves"). Removing the heuristic means editing
  rule 2, which is the operator's call, not mine.
- **Alternatives considered**: keeping the reference check but narrowing it
  to `.claude/` files (rejected for now: it is the same heuristic with a
  smaller blast radius, and the rule-2 question is unchanged); deleting the
  script entirely (rejected: a pointer that disagrees with the plan is the
  one failure that silently misleads the next session).
- **Approved by**: operator (this exchange), bar the rule-2 question above.
