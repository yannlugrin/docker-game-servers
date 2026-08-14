# Root track — decision log

Decisions governing repository-wide files land here; each component
track keeps its own log, and decision ids are per log — a citation
crossing logs names the file (`project-zomboid/DECISIONS.md D-003`).

The root specification is a repository-wide file: an amendment to it
logs **here**, even when the resolution lands during a
component-track step. When one resolution amends the root document
and a per-game document in the same breath, a single entry in this
log carries both, the component log is not duplicated into, and
rule 1's one-commit rule spans the entry and both amendments.

Entry format — ids are assigned in file order, frozen once assigned,
never reused:

- **D-NNN — short title**
  - **Date:**
  - **Step:** the plan step (not-yet-started steps cited by number
    *plus title*)
  - **Context:**
  - **Decision:**
  - **Alternatives considered:**
  - **Approved by:** operator, or implementer-within-latitude (naming
    which latitude: "should" deviation, or workflow choice)

---

- **D-001 — Adoption of the implementation workflow**
  - **Date:** 2026-08-14
  - **Step:** bootstrap (pre-`step-000`)
  - **Context:** Handoff from the specification phase to
    implementation. The operator's bootstrap prompt defines the
    working rules: read-only specifications with a decision-gated
    amendment channel, one operator-gated step at a time, file-based
    memory (one plan and one decision log per track, a single
    `CLAUDE.md`), per-track step identifiers with annotated `step-*`
    tags on approval, logged decisions, a secrets bar, an enforced
    permission boundary, and a proportion rule.
  - **Decision:** Adopt the workflow as restated in `CLAUDE.md`
    (rules 1–11, kept under that numbering); organize the work in
    three tracks (root, steamcmd, project-zomboid) per the track map;
    derive the plans from the specification with the foundation steps
    (`step-000`–`step-002`) first and the cost taxonomy ordering the
    rest.
  - **Alternatives considered:** none — the workflow is the operator's
    prescription; restating it faithfully is the task.
  - **Approved by:** operator (bootstrap prompt).

- **D-002 — Local harness toolchain**
  - **Date:** 2026-08-14
  - **Step:** step-000 — The harness, local only
  - **Context:** the plan fixes `pre-commit` as hook runner and `just`
    as task runner, but leaves open how they are obtained and pinned.
    Rule 9 reserves system-level installs to the operator; `just` and
    `python3` are already present on this machine, `pre-commit` is not.
  - **Decision:** the Python tooling lives in a repository-local
    virtualenv `.venv/`, created by `just setup` from a fully pinned
    `requirements.txt` (transitive tree included). `just setup` is the
    one documented setup command and also runs `pre-commit install`
    and `install-hooks`. `git`, `just` and `python3` with `venv` stay
    hand-installed prerequisites, named in `README.md`. `just check`
    passes pre-commit an explicit file list built with
    `git ls-files --cached --others --exclude-standard -z`, never
    priming the index. The justfile is this step's new artifact class
    and gets its check family: a parse check
    (`just --summary --justfile`). Formatting is not enforced —
    `just --fmt` is still an unstable flag in just 1.45.
  - **Alternatives considered:** `uv` or `pipx` to manage the tooling —
    one more bootstrap dependency for a repository holding no Python
    code; a system-wide `pip install pre-commit` — wants root, which
    rule 9 reserves to the operator; hash-pinned requirements — needs
    a lock-file compiler the repository would otherwise not carry.
  - **Approved by:** implementer-within-latitude (workflow choice).

- **D-003 — Prose lint: tools, and the rules turned off**
  - **Date:** 2026-08-14
  - **Step:** step-000 — The harness, local only
  - **Context:** the plan asks for prose lint over the governance
    documents *as they already are*. The specifications and
    `.claude/refs/` are read-only (rules 1 and 3), so the config bends
    to the documents; excluding anything from a rule is a logged
    decision rather than a quiet config line.
  - **Decision:** `pymarkdown` for Markdown structure and `codespell`
    for misspellings, both pinned pre-commit hooks. Three rules are
    off repository-wide, each with its reason inline in
    `.pymarkdown.yaml`: **md013** (line length — prose already wraps
    near 72 columns, but tables and reference links legitimately run
    long), **md001** (heading increment — every plan puts step
    headings at h3, so a track with a single implicit milestone jumps
    h1 to h3, and uniform step-heading depth across the three plans is
    worth more than the rule), **md036** (emphasis-as-heading — the
    decision-log entry format is a bold lead-in inside a list item,
    which the rule cannot tell from a heading). `.codespellrc` accepts
    *unparseable*, the variant spelling the read-only root
    specification uses. No document is excluded from any rule.
  - **Alternatives considered:** `markdownlint-cli2`, the more
    standard Markdown linter — rejected because pre-commit would pull
    a whole Node runtime into a repository with no JavaScript, for one
    linter (rule 11); `vale` — a prose-*style* linter needing a
    downloaded binary and a style package, heavier than the
    well-formedness bar this harness sets; editing the documents to
    satisfy the rules — excluded by the plan for the read-only ones,
    and inconsistent to apply to the rest alone.
  - **Approved by:** implementer-within-latitude (workflow choice).

- **D-004 — Local test state lives under `/.local/`**
  - **Date:** 2026-08-14
  - **Step:** step-000 — The harness, local only
  - **Context:** `.gitignore` must cover local test state roots and
    downloaded game or steamcmd content before any of it exists.
    Letting later steps invent directories and append ignore patterns
    as they go leaves multi-gigabyte content one forgotten line away
    from being staged.
  - **Decision:** one ignored root, `/.local/` at the repository root,
    holds every local and disposable artifact a hand-run container or
    smoke test writes on the host. Later steps place bind-mount roots
    and downloaded content there instead of adding ignore patterns.
  - **Alternatives considered:** per-step ignore entries — the
    forgotten-line risk above; state outside the checkout (`/tmp`, an
    `XDG` cache) — harder to find and clean, and detached from the
    clone it belongs to; relying on Docker named volumes alone —
    right for most cases, but bind-mount tests still write on the
    host.
  - **Approved by:** implementer-within-latitude (workflow choice).

- **D-005 — `check` takes a `scope` parameter: `all` gates, `changed`
  iterates**
  - **Date:** 2026-08-14
  - **Step:** step-000 — The harness, local only
  - **Context:** the operator raised that running every hook over every
    file on every invocation does not scale as the repository grows,
    and asked for a narrowed development-loop form. Rule 2 already
    allows a narrowed fast form mid-step and requires the full `check`
    on every commit that receives a step tag. Measured at this size,
    19 files: full `check` 1.03 s, `check changed` on a one-file diff
    0.45 s — the dominant cost is hook process startup, not file count,
    so the gain grows with the tree rather than being large today.
  - **Decision:** one recipe, `check scope="all"`, taking the scope as
    a parameter — `just check` for the whole tree, `just check changed`
    for what differs from `HEAD` (staged, unstaged and untracked,
    deletions filtered out). An unknown scope is a hard error naming
    the valid values, not a silent fallback; an empty file list reports
    why rather than passing quietly. `all` stays the default and the
    gate for step handover, milestone review and CI, so `just verify`
    inherits it. Nothing holds its own list of checks: both scopes,
    plus the git pre-commit hook, read `.pre-commit-config.yaml`, so
    the scopes can differ and the check set cannot. Parameters are the
    reason this repository uses `just` over `make`; a second recipe
    would have been a `make` shape.
  - **Alternatives considered:** a separate `check-changed` recipe —
    built first and rejected by the operator: it duplicates the recipe
    body for a difference that is one argument, and forgoes the
    capability `just` was chosen for. (The reason given against the
    parameter when it was first weighed — that `just --list` would hide
    the scopes — was simply false: `--list` prints `check scope="all"`,
    parameter and default included.) Making `changed` the default and
    the full sweep opt-in — inverts the safety default, and the fast
    scope provably cannot catch a committed file broken by a later
    config change. Leaving the git pre-commit hook as the only fast
    path — it sees staged files only, so it misses the unstaged and
    untracked work the loop is actually editing.
  - **Approved by:** operator (requested during step-000, and corrected
    to the parameter form).

- **D-006 — The repairing hooks are documented, not suppressed**
  - **Date:** 2026-08-14
  - **Step:** step-000 — The harness, local only
  - **Context:** three hooks in the harness — `end-of-file-fixer`,
    `trailing-whitespace`, `mixed-line-ending` — rewrite what they find
    instead of only reporting it. So a failing `just check` can modify
    the working tree, and rule 1 makes every `SPECIFICATIONS.md`
    read-only, `.claude/refs/` too (rule 3). The operator asked whether
    to suppress the rewriting under the check commands or to document
    it.
  - **Decision:** keep the repair behaviour and document it — in
    `README.md` under Local checks, and in the justfile header.
    Checked against the pinned hooks rather than assumed: only
    `mixed-line-ending` offers a report-only mode (`--fix=no`);
    `trailing-whitespace` and `end-of-file-fixer` have none. Suppressing
    one of three would leave the harness inconsistent and the exposure
    intact. A passing check never writes; a failing one announces
    `files were modified by this hook` and the change stays visible in
    `git diff`. Every document in the tree is whitespace-clean today,
    so nothing fires there; the residual exposure is a hook behaviour
    change, which can only arrive through a deliberate `rev:` bump.
  - **Alternatives considered:** report-only replacements for the two
    hooks that lack the mode — a bespoke linter, which the plan bars
    without prior operator agreement, built to remove a risk that is
    currently zero; excluding the read-only documents from the three
    hooks — a documented exclusion that would also stop the harness
    noticing a CRLF arriving in a specification, the one whitespace
    defect that would genuinely matter there; dropping the three hooks
    — forfeits the CRLF guard that protects the shell entrypoints later
    baked into Linux images.
  - **Approved by:** operator (put the choice to the implementer at
    step-000; ratified with the step's approval).

- **D-007 — The permission and hook baseline**
  - **Date:** 2026-08-14
  - **Step:** step-001 — Permission and hook baseline
  - **Context:** rule 9's boundary was textual only; instructions shape
    behaviour, settings and hooks enforce it. The plan requires the
    mechanisms proven rather than assumed, so the baseline was designed
    against measurements, recorded in `.claude/docs/permissions.md`
    (Claude Code 2.1.232). Three of those measurements decided the
    shape. `deny` beats `ask` beats `allow` regardless of specificity,
    so an ask rule overlapping an intended allow silently cancels it —
    and cancels a hook's carve-outs with it. A permission rule matches a
    command's *prefix*, so `Bash(git commit -m *)` provably ran
    `git commit -a --amend -m x` unprompted while the ask rule written
    for `--amend` never matched; no narrower pattern helps, since any
    prefix allow admits a trailing flag. And a hook *can* turn an
    allowed call into a prompt: `permissionDecision: "ask"` overrides a
    matching allow rule. An earlier probe suggested otherwise, but it
    used `escalate`, which is not one of the four values the harness
    accepts and is discarded — the correction is what makes gating by
    prompt possible at all here.
  - **Decision:** a committed, reviewable baseline in
    `.claude/settings.json`, paired with a guard hook that decides on
    parsed arguments, `.claude/hooks/bash_guard.py`. The hook is a
    shared template; only its registry is this project's. **Allow** is
    deliberately broad where the guard is watching — `Bash(git:*)`,
    `Bash(docker:*)`, `Bash(rm:*)` — because a prefix pattern cannot
    express "a force push however it is spelled", and a long enumerated
    allow list is brittle in exactly the way measured above. **For those
    three tools the guard is the boundary, not the rule list**; every
    other command has no allow rule and is gated by that absence.
    **The guard** carries the gating: git's ground rules (force push and
    history rewriting denied, push, amend, reset, clean, tag and branch
    deletion asked) plus four project rules — `--no-verify` and
    `git config`, both of which can disable the pre-commit harness rule
    2 requires, and `remote add` / `remote set-url`, which decide where
    a push lands; docker's registry writes, host-global sweeps and
    credential handling; and `rm`, gated by default with one proven-safe
    shape, paths under `.local/` (D-004), resolved before comparison so
    a `..` traversal is not a granted shape. **Ask** in settings is only
    what carves out of the broad `Edit(/**)` — the boundary's own files,
    the documents rule 1 keeps read-only, environment files — plus the
    tools the guard says nothing about. No `ask` rule may name a tool
    the guard gates. **Deny** is the fail-open backstop: a hook that
    stops loading is skipped silently, so the acts that cannot be undone
    are denied by pattern as well, prefix-weak but unconditional. Bypass
    and auto permission modes are disabled, which is what makes gating
    by absence real: under either, an unmatched command is
    auto-approved.
  - **Alternatives considered:** the enumerated allow list this
    replaced — some eighty prefix patterns, which is the brittleness the
    measurements describe, and which still admitted `git commit -a
    --amend`; a guard that denies rather than asks — what the `escalate`
    mistake forced, and it takes away the in-exchange approval rule 9 is
    written around; restating the guard's asks in settings as well —
    a prefix rule is strictly weaker (`Bash(git push:*)` misses
    `git -C dir push`), so it would be a second source of truth, and for
    a gated tool it would cancel the guard's own carve-outs; keeping the
    baseline in `.claude/settings.local.json` — not committed, so not
    reviewable and not shared, the opposite of what rule 9 asks for.
  - **Approved by:** operator (proposed at step-001 under rule 4, which
    excludes the baseline from implementer latitude; ratified with the
    step's approval).

- **D-008 — Python enters the repository: hook language, test runner
  and check family**
  - **Date:** 2026-08-14
  - **Step:** step-001 — Permission and hook baseline
  - **Context:** the guard hook is the first executable code in the
    repository. A PreToolUse hook is handed its tool call as JSON on
    stdin, so the language has to parse JSON; rule 2 requires the new
    artifact class to get its check family in this step, and the hook
    is shipped behaviour, so `just test` stops being a placeholder.
  - **Decision:** the hook is Python 3 using only the standard library,
    and `python3` is already a documented prerequisite of this
    repository. It carries its own tests: `bash_guard.py --selftest`
    runs the case table beside the registry, and fails on a rule no case
    reaches, so a rule added without a case is a lint error rather than
    an oversight. `just test` executes the file — shebang and exec bit,
    the exact path Claude Code uses, which `python3 <file>` would not
    exercise — and `just check` runs the same selftest through
    pre-commit, deliberately: the commit hook is what stops a broken
    guard from landing, while `just test` is what answers "is the
    implementation right?". One definition, two callers. The check
    family for the class is `check-ast` (it parses) plus `ruff-check`
    run unconfigured; its default rules are the defect classes a test
    suite can miss. Formatting stays unenforced, as it is for the
    justfile (D-002). No new dependency enters `requirements.txt`.
  - **Alternatives considered:** a POSIX shell hook — it would need
    `jq` to read its input, a system-level install rule 9 reserves to
    the operator, or `python3` anyway; a separate `tests/` suite under
    `unittest` or `pytest` — built first and dropped when the guard
    arrived with its own cases, since a second suite would have tested
    the same contract from further away, and `pytest` would have added a
    pinned dependency tree for one file; `bats` or `shellspec` for a
    shell hook — the same system-install problem, one layer further out;
    `ruff-format` or a house style — formatting was deliberately left
    unenforced at step-000 and nothing here changes that argument.
  - **Approved by:** implementer-within-latitude (workflow choice).
