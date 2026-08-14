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
