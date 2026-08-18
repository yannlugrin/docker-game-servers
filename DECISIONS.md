# Decision log — root track

Decisions governing what lives at the repository root or in a shared
directory: the harness, CI and all publication, the repository-wide
documentation of root §9, and the workflow itself. Decisions governing an
image's own files live in that image's track log —
`steamcmd/DECISIONS.md` (`sc`) or `project-zomboid/DECISIONS.md` (`pz`). The
criterion is D-005.

## How to read this log

Three kinds of decision are recorded here, and a reviewer treats them
differently:

- **Choices made with the operator** — specification amendments, scope
  calls, step reordering. The approval line names them.
- **Choices made inside a specification "should"** — the specification
  permits deviating from a recommended default *with reason*, and the reason
  is in the entry. **A reviewer judges these on the recorded reasoning**, so
  the reasoning stays in the entry in full even when the entry is later
  compacted; a deviation from a "should" with **no** entry is a finding.
  Code contradicting a **must** is a defect, never a decision.
- **Workflow choices left to the implementer** — the harness's shape and
  names, `.gitignore` contents, which tooling templates are adopted. The
  approval line says "implementer, within latitude" and names which
  latitude. The permission baseline is **not** in this latitude: it is
  proposed to the operator at `step-002`.

Ids are `D-NNN`, numbered in **file order** (which is chronological),
**frozen once assigned and never reused**. Ids are **per log**: this file,
`steamcmd/DECISIONS.md` and `project-zomboid/DECISIONS.md` each start at
`D-001`, so a citation crossing logs names the file
(`project-zomboid/DECISIONS.md D-NNN`).

A **component track's** step that amends the **root** specification logs its
decision **here**, in the same commit as the amendment, with that track's step
id in the commit subject — the log follows the document being amended, not the
step doing the work. An amendment touching two specifications is two entries,
one per log, cross-citing.

Entries cite not-yet-started steps by **number plus title**, so a missed
renumbering sweep still leaves the reference decodable.

### Entry format

```text
## D-NNN — <short title>

- **Date:** YYYY-MM-DD
- **Step:** <step id> — <step title>
- **Context:** what made a decision necessary.
- **Decision:** what was decided, in the imperative.
- **Alternatives considered:** each with why it was rejected.
- **Approved by:** operator | implementer, within latitude (<which>)
```

---

## D-001 — Adopt the staged, plan-gated implementation workflow

- **Date:** 2026-08-17
- **Step:** bootstrap (this decision precedes `step-000`)
- **Context:** The specification phase produced two specification documents
  and handed implementation to a fresh session with no memory. Sessions do
  not persist, the specifications are large, and the failure mode that
  matters is silent drift between what the specifications require and what
  the repository contains.
- **Decision:** Adopt the workflow the implementation prompt defines, and
  encode it in `CLAUDE.md` as eleven numbered standing rules. In summary:
  every `SPECIFICATIONS.md` is read-only, amended only through a logged
  decision landing in the same commit as the amendment; work proceeds one
  operator-gated step at a time, nothing handed over unverified; all memory
  lives in files — a plan and a decision log per track, one repository-wide
  `CLAUDE.md`, context-specific notes under `.claude/docs/`; decisions are
  logged in the log of the track whose files they govern; secrets never
  enter the repository; commits are small, track-qualified and carry their
  own documentation updates; repository files are in English; `README.md` is
  the neutral entry point; bug reports on the current step are the
  implementer's to drive within a stated action boundary; persistence has a
  budget and asking is part of the workflow; and the smallest thing that
  satisfies a rule is the right thing.
  Two tracks exist at adoption: the **root** track (prefix `step-NNN`, plan
  `PLAN.md`, log `DECISIONS.md`) and the **`pz`** track (directory
  `project-zomboid/`, prefix `step-pz-NNN`, plan and log in that directory).
  Each future game adds a track and registers its prefix in `CLAUDE.md`'s
  track map.
- **Alternatives considered:**
  - *Implement straight from the specifications with no plan or logs.*
    Rejected: a session that starts mid-work would have no way to establish
    what is done, and every "should" deviation would be invisible to a
    reviewer.
  - *One plan and one log for the whole repository.* Rejected: the
    repository is designed to grow one game per directory, and a single plan
    would serialise unrelated tracks and force renumbering across them.
  - *Memory in Claude Code's auto memory rather than in files.* Rejected on
    the prompt's reasoning, which holds independently: it is machine-local
    and unversioned — a second memory outside git, outside review, and
    outside these rules. It stays disabled in `.claude/settings.json`.
  - *Batch the foundation into one step.* Rejected: a foundation delivered
    whole arrives with everything already written, so the operator's first
    correction costs the lot.
- **Approved by:** operator (the workflow is the operator's own; this entry
  records its adoption rather than proposing it)

## D-002 — `CLAUDE.md`'s line budget, and the lazily-loaded mechanics file

- **Date:** 2026-08-17
- **Step:** bootstrap
- **Context:** Rule 3 sets `CLAUDE.md` a 220-line budget with headroom around
  180. Restating the eleven rules plus the six sections the workflow requires
  by name produced 301 lines. Rule 3's own eviction order was applied first
  and did not close the gap: nothing context-specific remained that a
  `.claude/docs/` read-trigger could reach, the templates block was already
  down to its three mandated items, and per-track detail had already moved to
  the plans. Rule 9's action-boundary enumeration alone is 35 lines and is
  carried whole by rule; the remaining ten rules are ~120 lines at
  operative-only density. Rule 3 says an unfittable restatement is a finding
  for the operator, never a file to pack, and names a project-specific budget
  as a legitimate outcome.
- **Decision:** Two parts.
  1. **Extract mechanics and reasoning to `.claude/docs/workflow.md`**, a
     lazily-loaded file with its own read triggers: the specification-amendment
     ritual, the plan-step entry shape, the tooling-placeholder semantics, the
     milestone-close passes, the harness contract and closing-tag shape, and
     the reasons behind the rules. `CLAUDE.md` keeps what binds and points at
     it. This took the file from 301 to 254 lines.
  2. **Set this project's budget at 280 lines, with a ~250 target.** 200 is
     not reachable: the only remaining route below ~250 is moving rule text
     itself out of the always-loaded file, and a rule that is not loaded is a
     rule that is not followed — the failure rule 3's eviction order exists to
     prevent. Rule 3 now cites this entry instead of the generic 220.
- **Alternatives considered:**
  - *Strip the rules' rationale in place, keeping rule and section count.*
    Partly done — the reasoning moved rather than being deleted, because
    reasoning is what stops a later session re-litigating a rule. Deleting it
    outright was estimated at ~30 lines recovered, which still misses 220.
  - *Delete a required section (`Where things live`, `Plan conventions`).*
    Rejected: `Plan conventions` became `.claude/docs/workflow.md` §1 with a
    read trigger rather than disappearing, which keeps it reachable for the
    closes that precede `/approve-step`.
  - *Compress rule 9's enumeration into a table.* Rejected: it is safety text
    the workflow requires carried whole, and restructuring it risks dropping a
    qualifier that bounds the free side of the boundary.
  - *Keep 220 and accept a file over budget with no ruling.* Rejected: a
    budget check that is ignored from the day it is written teaches the next
    session to ignore it.
- **Approved by:** operator

## D-003 — Base-image pulls stay anonymous until limits bite

- **Date:** 2026-08-17
- **Step:** bootstrap (executed at `step-006` — Builder publication on CI)
- **Context:** Root §2.6 records that Docker Hub rate-limits anonymous pulls,
  which makes every CI pull of the Debian base from shared-IP hosted runners
  an intermittent-throttling risk, and asks the implementation to decide about
  it **deliberately rather than after the first failed build**.
- **Decision:** CI pulls the base anonymously. The pre-committed response to
  throttling is **authenticated pulls with a Docker Hub credential the
  operator supplies**, wired as a CI secret at the moment limits are actually
  observed. `step-006` therefore builds no mirror and adds no credential now,
  and its prerequisite row records the credential as conditional. This is a
  deliberate decision taken in advance, which is what §2.6 asks for; it is not
  "wait and see", because the response is fixed and the trigger is named.
- **Alternatives considered:**
  - *Mirror the base into GHCR.* Rejected for now: it costs machinery to build
    and keep fresh, and its benefit is unmeasured — a rebuild cadence this low
    may never touch the limit. Reopen if throttling recurs after
    authentication.
  - *Authenticate from the start.* Rejected: it spends a credential and a
    secret on a risk not yet observed.
- **Approved by:** operator

## D-004 — Every shipped image directory carries a specification document

- **Date:** 2026-08-17
- **Step:** bootstrap
- **Context:** Root §6 named the per-document class **per-game**, and the
  steamcmd builder is the one shipped image that is not a game, so it had no
  document of its own. I used that absence as an argument for keeping the
  builder on the root track. The operator identified it as a
  specification-phase gap rather than a design signal: the doctrine behind this
  workflow holds that in a multi-document specification, a component with
  nothing of its own still gets a `SPECIFICATIONS.md` — a pointer to the
  section that specifies it — so the layout stays uniform and a missing file
  never has to be interpreted. The rule never fired here because §6 named the
  class by *game* rather than by *component*.
- **Decision:** Amend root §6 so the document class covers **every shipped
  image directory**, in two forms: the per-game specification §6 already
  defines, and — for an image the root document specifies in full, today only
  the builder (§4) — a **pointer** document carrying no requirements of its
  own, because a requirement stated twice is a requirement that drifts.
  Retitle §6 "Per-image specifications"; its per-game content list is
  unchanged and still defines that term, so every existing `§6` and "per-game
  specification" citation stays true. **`*/SPECIFICATIONS.md` now matches a
  non-game directory** (`steamcmd/`) — recorded because a later document lint,
  or any tooling keyed on that glob, must expect a pointer document with no
  requirements in it.
- **Alternatives considered:**
  - *State the builder's document rule under §4, with §6 restated as the
    general rule.* Rejected: it puts one rule in two places, which is the
    drift this amendment exists to prevent.
  - *Leave §6 alone and let `steamcmd/` have no specification document.*
    Rejected: that is the gap itself, and it forces every reader to interpret
    a missing file.
  - *Keep the "Per-game specifications" title.* Rejected: a section whose
    opening paragraph governs every shipped image should not be titled for one
    class of them, and cold reviewers read this document without context.
- **Approved by:** operator (who identified the gap and ordered the amendment)
- **Sequel:** the track and ownership consequences are D-005.

## D-005 — Track ownership follows artifacts, not blast radius

- **Date:** 2026-08-17
- **Step:** bootstrap
- **Context:** The bootstrap prompt assigned the steamcmd builder to the root
  track, and the first plan transcribed that without examining it. Asked to
  argue the choice, I defended it and was overruled. The criterion needed
  writing down, because the same question will arrive with every future
  component — a second builder line (root §10.1), a non-Steam fetcher
  (root §10.6) — and the answer must not be re-derived from a transcript
  nobody can read.
- **Decision:** Ownership follows **where the artifacts live**, not how far
  their effects reach.
  - The **root track** owns what lives at the repository root or in a shared
    directory: the harness (`justfile`, `.pre-commit-config.yaml`), the
    governance files, `docs/`, `README.md`, and **CI in
    `.github/workflows/`**. That enumeration is **closed**; widening it is a
    logged decision, not a judgement call made in the moment.
  - **CI stays root-owned even when it publishes another track's image**, for
    exactly that reason: the workflow file is in a root directory. So the
    builder's publish workflow is `step-006` on the root track, as the game
    image's publication is `step-008`/`step-009`.
  - Every **shipped image directory** is a track, and carries a
    specification document — the per-game form, or the pointer form where the
    root document specifies it in full (D-004). Today: `sc` (`steamcmd/`,
    prefix `step-sc-NNN`) and `pz` (`project-zomboid/`, prefix
    `step-pz-NNN`). This supersedes D-001's statement that two tracks exist
    at adoption and that a track is added per *game*.
  - **Downstream ripple is what cross-track dependency edges are for.** That
    a builder change rebuilds every game image is coupling, and coupling is
    expressed by a dependency line, never by moving ownership.
- **Alternatives considered** — the three grounds I argued for keeping the
  builder on the root track, each rejected:
  - *"A track is anchored to a specification document, and the builder has
    none."* Rejected: true only because of the specification-phase gap D-004
    closed. The builder now has a document, and the premise evaporates.
  - *"Its work ripples repository-wide, which is the root track's
    definition."* Rejected: it conflates coupling with ownership. Every game
    image depends on the builder too, and by that reasoning the root track
    would absorb anything with dependants. The test that survives is where
    the files live — CI is root-owned because `.github/workflows/` is a root
    directory, not because rebuilds ripple.
  - *"Three steps do not earn the machinery."* Overruled deliberately: a
    track costs two files and a table row, while its absence costs a future
    builder maintainer a decision log they cannot find. It was also free at
    this moment and would not be after the foundation is tagged, since step
    numbers freeze when a step enters `in progress` (rule 6).
  - One part of my argument **stands**: publication belongs to the root
    track, and `step-006` stayed there.
- **Approved by:** operator (who supplied the criterion and overruled the
  proportion argument)

## D-006 — The toolchain bootstrap: a venv behind `just setup`

- **Date:** 2026-08-17
- **Step:** `step-000` — The harness skeleton, local only
- **Context:** `PLAN.md`'s `step-000` requires pinned dependencies installable
  through **one documented setup command**, and leaves the bootstrap
  mechanism to a logged workflow decision. The measured machine
  (`.claude/docs/environment.md` §1) has `python3` with `venv` and
  `ensurepip`, `pip`, and `just` 1.45.0; `pre-commit` and every linter are
  absent, and so are `uv` and `pipx`.
- **Decision:** `just setup` is the one documented setup command. It creates
  `./.venv` with `python3 -m venv`, installs `requirements.txt` into it, and
  runs `pre-commit install` and `install-hooks`. Three consequences, each
  deliberate:
  - **`requirements.txt` pins `pre-commit` and nothing else.** Every linter
    is declared in `.pre-commit-config.yaml` and pinned there by revision,
    which `pre-commit` installs into its own isolated environments. Listing a
    linter in both places would give it two pinned versions that can
    disagree.
  - **The pin is a direct `==`, not a hash-locked transitive set.** The
    dependency surface is one tool used to run linters, not a runtime this
    repository ships; a lock file is machinery to maintain for a risk that
    does not exist yet. Revisit if a transitive break is ever actually
    observed (rule 11 — built at the moment of need).
  - **`just` itself is a prerequisite, not a pinned dependency.** It is the
    runner that invokes the setup command, so it cannot be installed by it.
    `README.md` names it alongside `python3` and `git`.
- **Alternatives considered:**
  - *`uv` or `pipx` for the bootstrap.* Rejected: both are absent on the
    measured machine, so either would add an install step in front of the one
    documented setup command — and `venv` plus `pip`, which are present,
    already do the job.
  - *A `scripts/setup.sh` so setup works without `just`.* Rejected: it lands
    a shell script, whose check family would have to arrive with it (rule 2,
    never ahead of need), to avoid a prerequisite the harness needs anyway —
    `just check` is unusable without `just` whatever setup does.
  - *Pinning `rust-just` into the venv so the whole toolchain is pinned.*
    Rejected: it puts a second `just` on the machine and makes which one runs
    depend on `PATH`, for a runner whose interface is stable.
  - *Installing `pre-commit` system-wide.* Rejected: unpinned, machine-global,
    and invisible to a fresh clone.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names)

## D-007 — What `just check` covers at `step-000`

- **Date:** 2026-08-17
- **Step:** `step-000` — The harness skeleton, local only
- **Context:** Rule 2's never-ahead rule governs check families keyed to an
  **artifact class**. It says nothing about guards keyed to no class at all —
  repository hygiene and secret detection — and a grep of all three plans
  found that **no step anywhere had scheduled either**. My first pass
  therefore landed three well-formedness families and rejected the hygiene
  hooks on rule 11, which applies the smallest-thing test to guards whose
  cost is not size but *timing*: several of them protect against mistakes
  that cannot be undone once committed. The operator raised this by asking
  what was planned for hygiene, security and whitespace.
- **Decision:** `just check` carries two groups at this step, **none of which
  rewrites a file**.
  1. **Well-formedness, one family per artifact class present today:**
     `check-json` (`.claude/settings.json`, which is the permission
     enforcement mechanism itself), `check-yaml` (the class arrives with
     `.pre-commit-config.yaml`), and `just --fmt --check` over the justfile
     (`just` is the only tool that parses it, and `--fmt --check` reports a
     syntax error and a formatting drift without rewriting).
  2. **Hygiene guards, admitted on blast radius rather than on class:**
     `check-added-large-files --enforce-all`, `check-executables-have-shebangs`,
     `check-shebang-scripts-are-executable`, `check-merge-conflict`,
     `check-case-conflict`, `forbid-submodules`, and
     `mixed-line-ending --fix=no`, plus a `.gitattributes` declaring
     `* text=auto eol=lf`. The test each passes is not "is it small" but
     "does the mistake it catches survive the commit that makes it": a
     multi-gigabyte blob or a secret in git history is unrecoverable without
     rewriting history, which rule 9 protects.
  **Deferred to `step-001`, deliberately:** markdown and prose lint, and
  **every repairing hook** — `trailing-whitespace` and `end-of-file-fixer`
  have no check-only mode, so adopting one lets a failing `check` mutate the
  read-only specifications. `step-001` already owes a `.claude/docs/` note
  for exactly that, so the decision belongs where its documentation lives.
- **Measured, and recorded so a later session need not re-derive it:**
  - `check-added-large-files` without `--enforce-all` inspects only files
    added to the index, so the flag is what makes it see the untracked files
    `just check` deliberately passes in.
  - `check-shebang-scripts-are-executable` reads the **git index** filemode
    (by design, so it also works on Windows) and therefore fires only on
    **tracked** files. Its sibling `check-executables-have-shebangs` reads
    the filesystem mode and does see untracked ones.
  - `mixed-line-ending` flags a file carrying **more than one** ending style;
    a uniformly-CRLF file passes it. That is why the LF rule lives in
    `.gitattributes` and the hook is its complement, not its substitute.
- **Alternatives considered:**
  - *Land a markdown structural lint here too.* Rejected: the documents it
    would lint are the read-only specifications, so the lint must bend to
    them, and "needs no tuning" is a claim only an attempted tuning can
    support. That attempt is `step-001`, which must not hold a green harness
    hostage — the split's own stated reason.
  - *Rely on `core.autocrlf` instead of `.gitattributes`.* Rejected on
    measurement: this machine does set `core.autocrlf=input` globally, but
    that is machine-local configuration that reaches neither a CI runner nor
    anyone else's clone.
  - *Keep rule 11's original reading and add nothing.* Rejected: rule 11 asks
    for the smallest thing that satisfies **the rule**, and the rule these
    guards serve is not "lint the artifact classes" but rule 5 and the
    protection of git history.
- **Approved by:** operator (who asked which hooks were planned, identified
  that the answer left gaps, and chose the scope from a proposal)

## D-008 — Rule 5 gets a mechanical guard: `detect-secrets` over the file list

- **Date:** 2026-08-17
- **Step:** `step-000` — The harness skeleton, local only
- **Context:** Rule 5 says a secret never enters the repository — not in
  files, not in examples with real values, not in commit messages — and root
  §5.4 forbids a secret in any image layer, ever. A grep of `PLAN.md`,
  `steamcmd/PLAN.md` and `project-zomboid/PLAN.md` found **no step that adds
  any secret-detection mechanism**: the `pz` plan handles credentials
  thoroughly at the level of *runtime behaviour* (redaction, fatal on a
  missing mandatory secret, an ephemeral RCON password) and not at all at the
  level of *what reaches git*. Until now rule 5 rested on implementer
  discipline plus `.gitignore`. It is also the one rule whose violation a
  later commit cannot undo.
- **Decision:** Adopt **`detect-secrets`** (Yelp, pinned by revision at
  `v1.5.0` in `.pre-commit-config.yaml`) together with `detect-private-key`
  from the already-pinned hook set. Run it **without a `.secrets.baseline`**:
  a baseline is an allowlist for known false positives, the tree currently
  produces none, and a file of hashes maintained in anticipation is exactly
  what rule 11 rejects. Introduce one at the moment a real false positive
  appears.
- **Alternatives considered:**
  - *`gitleaks`.* The more standard scanner and it needs no baseline, but its
    pre-commit hook scans the **staged git diff** rather than a file list.
    That fits the commit hook and silently skips untracked files — and
    `just check` is built specifically to see untracked files, because a
    secret sitting uncommitted in the working tree is the case that matters
    most. Rejected on design fit, not on quality; revisit if
    `detect-secrets`' false-positive rate makes the baseline burden real.
  - *`detect-private-key` alone.* Rejected as insufficient: it catches a
    pasted key block and nothing else, while the credentials this repository
    will actually handle are passwords and tokens.
  - *Generate a `.secrets.baseline` now.* Rejected: it would record the
    current tree as "reviewed" without anything having been reviewed, and a
    baseline is only meaningful once something in it was judged.
- **Approved by:** operator (who selected secret scanning from a proposal
  after the gap was reported)

## D-009 — The document lint: `pymarkdown` and `codespell`, bent to fit

- **Date:** 2026-08-17
- **Step:** `step-001` — The governance and prose lint
- **Context:** In this repository documents are load-bearing — the
  specifications are the sole source of requirements, the plans are the
  current-state record — so they are linted like code. `step-001` fixes the
  direction of fit in advance: the specifications are read-only under rule 1,
  so **the lint bends to them and never the reverse**, and every bend is a
  logged decision rather than a quiet config line. This entry is that log.
- **Decision:** Adopt **`pymarkdown` v0.9.39** for markdown structure and
  **`codespell` v2.4.3** for spelling, both pinned by revision in
  `.pre-commit-config.yaml`, both **report-only** — `pymarkdown` runs `scan`,
  not `fix`, and `codespell` runs without `-w`.
  **Three bends, and no more.** Measured over the thirteen governance and
  human-facing documents: with these three in place, **every other rule of
  both tools produces zero findings**, so nothing else was tuned, excluded
  or invented. The line-length limit stays at the default 80.
  1. **Enable the `markdown-tables` extension.** pymarkdown is a CommonMark
     linter and CommonMark has no tables, so without it every table row is
     parsed as ordinary paragraph text and bend 2 below is unreachable. This
     was measured, not assumed: `tables: false` had no effect whatsoever
     until the extension was on.
  2. **`md013.tables: false`.** A table row cannot be wrapped — the row is
     the record and a line break ends it — so a wide table is not a style
     anyone can correct. 106 of the 108 over-long lines were table rows, 17
     of them inside read-only specifications.
  3. **`codespell --ignore-words-list=unparseable`.** A standard variant
     spelling that codespell prefers to write `unparsable`, used by root
     §3.4. The specification cannot be edited to satisfy a linter, and the
     plans quoting its wording stay consistent with it.
  **Documents were changed rather than exempted wherever that was open**,
  which is everywhere except a specification's wording: three unlabelled
  code fences gained a `text` language (`DECISIONS.md`, and the `sc` and `pz`
  decision logs, whose entry-format template is the same block in each), and
  one over-long comment in `README.md`'s command listing was shortened. The
  bend-to-the-document rule is grounded in the specifications being
  **read-only**; a plan or a log is not, so a one-word fix there beats
  weakening a rule for everyone.
  **A fourth bend existed briefly and was retired.** `SPECIFICATIONS.md` line
  799 was 87 characters of ordinary prose in a document that otherwise wraps
  at ~76, and the limit was first widened to 88 to accommodate it. On the
  operator's authorisation the line was **rewrapped instead** — line breaks
  only, **not one word changed**, verified by comparing the whole document's
  word sequence before and after (7,934 words, identical). No decision entry
  governs that edit and none is owed: rule 1's amendment channel exists for
  changes to what a specification *says*, and nothing it says changed. The
  limit returned to the default 80, which is why this entry lists three bends
  and not four.
- **`.claude/docs/` note: not written, deliberately.** `step-001` owes one
  **for any repairing hook adopted**. None was: every hook in this
  repository reports and none rewrites, which is now true of the whole
  harness rather than of this step alone. The condition did not fire, so the
  note would document a hazard that does not exist.
- **Alternatives considered:**
  - *`markdownlint` / `markdownlint-cli2`.* The more widely used tool, and it
    supports the table exemption natively rather than through an extension
    still at 0.1.0. Rejected on runtime cost against a measured benefit of
    zero: `environment.md` records node as absent, so it would add a node
    toolchain — downloaded here and cached again in CI at `step-005` — for a
    result this repository's documents already achieve. Reopen if the tables
    extension misbehaves on upgrade, which is the named risk below.
  - *`vale` for prose style.* Rejected: it needs a style package chosen and
    tuned, and every mainstream one would fight 2,700 lines of deliberate,
    carefully written specification prose. That is the "high-iteration task"
    `step-001` was split off to contain, and containing it means declining
    the tool, not budgeting for the fight. `codespell` catches what is
    objectively wrong — a misspelling — and asserts nothing about style.
  - *Disable `md040` (fenced-code-language) instead of labelling three
    fences.* Rejected: it is a real rule that will matter for the human
    documentation of §9, and three one-word edits cost less than losing it.
  - *Raise `line_length` far enough to cover tables too, and drop bend 1.*
    Rejected: it would set the limit above 450 and stop catching anything.
  - *Keep the limit at 88 rather than rewrap one specification line.*
    Rejected once rewrapping became available: widening a rule for thirteen
    documents to spare one line is the trade this configuration exists to
    avoid making silently.
- **The one risk, named:** the `markdown-tables` extension is version 0.1.0 —
  the only part of this harness running on something upstream still calls
  experimental. Measured at adoption, enabling it produced **no findings of
  its own** and correctly exempted 106 rows. That is the property to
  re-measure on upgrade; `.pymarkdown.yaml` carries the instruction.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names). The one point that left that
  latitude — editing a read-only specification, even only its line breaks —
  went to the operator, who authorised it on the condition that no word
  change.

## D-010 — The permission and hook baseline

- **Date:** 2026-08-17
- **Step:** `step-002` — The permission and hook baseline
- **Context:** Rule 9 states an action boundary in prose. `step-002` exists to
  make it mechanical, and says plainly that the baseline is **outside the
  implementer's latitude**: it is proposed to the operator as one reviewable
  whole. The measurements behind every claim below are in
  `.claude/docs/permissions.md`, with the version they were taken on and a
  recipe to re-take them.
- **Decision (proposed — see the approval line):** two halves that only work
  as a pair.
  1. **The guard**, `.claude/hooks/bash_guard.py`, instantiated from the
     handoff template with **only its `REGISTRY` edited**, as the template
     requires. `git` and `docker` keep the template's rules unchanged — the
     docker set already maps onto rule 9 exactly. Two tools are added: `gh`,
     expressed as **grants** because rule 9 rules GitHub API *reads* free and
     gates every write, so the reads are the finite side to enumerate; and
     `steamcmd`, as a **vocabulary** grant, so an anonymous download or
     metadata query is silent while a credential is not. `just` and
     `pre-commit` get **no entry**: an entry with no rules, grants or handoff
     is silence, which an unregistered tool already gets, and the guard cannot
     see inside a recipe anyway. What keeps them safe is rule 2's invariant —
     no justfile recipe ever performs an act rule 9 gates — which lives
     outside the guard and must be honoured whenever a recipe changes.
  2. **The settings**, per the template's pairing: a broad allow for each
     registry tool so the guard can claw back; **no `ask` rule for anything
     the guard gates**, since a matching `ask` prompts even where a hook
     allows and would cancel every carve-out; no prefix rule restating a guard
     decision; and one deliberate duplication — an eight-entry `deny` backstop
     covering only permanent history loss, because a hook fails open and a
     broad allow plus a dead hook is a wider surface than a narrow allow list
     ever was. `permissions.defaultMode` is **`acceptEdits`**.
- **Ruled out by measurement, not preference.** `auto` is **ignored** in a
  project settings file; `dontAsk` **auto-denies** instead of prompting, which
  would remove the operator's ability to approve in-exchange — what rule 9's
  boundary and rule 6's push-at-close both rest on; `bypassPermissions`
  removes the gate; `plan` is a working mode. That leaves `default`, which
  prompts on every file edit and is how an operator ends up reaching for a
  looser mode — the failure this design exists to avoid.
- **Measured after installation, and two beliefs did not survive it:**
  - **A hook fails open — proven, not assumed.** With the guard made
    non-executable, a command it had just refused ran with no prompt at all,
    carried by the broad allow. That is the entire justification for the
    `deny` backstop, and it is now evidence rather than doctrine.
  - **Both mode-dependent behaviours flipped between `auto` and
    `acceptEdits`.** A write outside the project succeeded silently under
    `auto` and prompts under `acceptEdits`; and writing `.claude/settings.json`
    was refused under `auto` but **succeeds** under the committed mode. So the
    claim that the implementer cannot install its own baseline was true only of
    the session that made it. Under what ships, **the implementer can edit its
    own permission boundary and can disable the guard with `chmod -x`** —
    neither prompting. This baseline therefore stops mistakes, not a determined
    agent; what bounds the latter is the operator reading the diff.
    `.claude/docs/permissions.md` §7 proposes the hardening and does not apply
    it.
- **The widest entry, named rather than buried:** `Bash(python3:*)`. The guard
  does not read `python3 -c` program text, so this allow can reach anything the
  guard would otherwise gate. It is proposed because the harness, the guard and
  the checks are all Python and the development loop runs it constantly; the
  alternative is a prompt on every Python invocation. **A judgement for the
  operator.**
- **Alternatives considered:**
  - *Rules rather than grants for `gh`.* Rejected: it would mean enumerating
    every mutating subcommand and prompting on none of the ones forgotten. The
    reads are the bounded side. A write-verb rule is kept **beside** the
    grants for the one case grants cannot catch — `gh repo delete list`, where
    the read verb is the name of the thing being destroyed.
  - *A registry entry for `just` and `pre-commit`.* Rejected as literally
    inert; the invariant is the real mechanism.
  - *Restating `git push` as a `deny`.* Rejected: rule 9 requires that a push
    **asks and is never denied**, because a denied pattern cannot be approved
    in the very exchange the rule relies on.
  - *`ruff-format` alongside `ruff check`.* Rejected twice over: it rewrites,
    which nothing in this harness does, and it would reflow the vendored guard
    against its docstring's explicit request.
- **Approved by:** operator, who reviewed the proposal, applied the settings
  on 2026-08-17, observed the three-command probe, and authorised both the
  `Bash(cd:*)` addition and the fail-open probe. The hardening of
  `.claude/docs/permissions.md` §7 is **not** covered by this approval and
  remains open.

## D-011 — Adopt three reviewer agents, and defer two

- **Date:** 2026-08-17
- **Step:** `step-003` — The reviewer agents
- **Context:** Rule 3 says tooling is created when it earns its place, and
  rule 11 says to build at the moment of need. Five agent templates were
  handed over; adopting all five would anticipate needs that do not exist,
  and adopting none would leave the first milestone close to improvise its
  own review — a recovery ritual invented during the crisis it exists for.
- **Decision:** Adopt **`step-reviewer`**, **`state-reviewer`** and
  **`optimize-memory`** at `.claude/agents/`. What separates them from the
  two deferred is **the certainty of the trigger, not whether it has
  fired**: the first milestone close is this milestone's own, at `step-005`,
  so the two passes it needs must exist before it arrives. `code-reviewer`
  and `test-reviewer` stay unadopted because their triggers — implementation
  code and a test suite — genuinely do not exist yet; they remain on
  `CLAUDE.md`'s not-yet-adopted list, which is what keeps a ritual citing
  them from dangling.
- **How the templates were changed, and why each change:**
  - **The governance placeholders resolve at invocation, not literally.**
    Each agent carries a track table instead of one fixed path, and the two
    milestone passes state that the track is **named at spawn** when they run
    as part of closing a step — the close ritual has already advanced
    `CLAUDE.md`'s pointer, so resolving from it would aim both passes at the
    wrong track and a state reviewer reading the wrong plan reports nothing
    wrong.
  - **`optimize-memory`'s budget was rewritten from 220/~180 to D-002's
    280/~250.** A template's enumeration that is narrower than the rule it
    claims to execute loses to the rule; left alone, this pass would have
    compacted toward a cap this project measured as unreachable.
  - **The architecture vocabulary was seeded from the specification**, since
    nothing is built yet, and says so — it is kept current under rule 6 as
    the system materialises, and a component not listed is still in scope.
  - **`tools:` was left as the templates set it**, after checking the running
    version's tool inventory: this build has no separate search tool, so
    adding one would have been a name silently dropped.
  - **The "CLAUDE.md is in your context, probed" claim was not copied.** It
    was not probed here, and asserting it would be false. Each agent instead
    **verifies its own premise**: if it cannot see rule 9, it stops and
    reports exactly that. The first real invocation is therefore the probe,
    and a failure announces itself instead of producing a confidently
    unbounded review.
- **Both probes were then run, and are recorded in `.claude/docs/agents.md`**
  with the version, the method and a re-measure recipe. The design above is
  not a substitute for them and was not accepted as one: a self-check reports
  during a real review that an invocation lacked rule 9, while the probe
  answers now — and "now" is what the pre-committed response needs, since
  inlining the gated set into three bodies is work to do **before** the first
  milestone close depends on those agents. Results: `CLAUDE.md` **does** reach
  a subagent, delivered as project instructions before its first tool call and
  never fetched with a tool, so **the inlining branch does not fire**; and
  `tools:` **binds by omission**, an unlisted tool being absent rather than
  refused. The self-check stays regardless, because it is what makes a later
  regression announce itself.
- **The limit that measurement exposed, recorded because it is easy to
  misread:** `tools:` restricts which tools exist, not what they can do.
  `step-reviewer` holds `Bash`, and `Bash` writes — so its read-only
  discipline rests on its prose, not its tool list. Anything that must be
  mechanically unable to write needs `tools: Read` alone and another way to
  obtain a diff.
- **Pre-committed response, unchanged and now dormant:** if that report ever
  does come back, each agent body carries the gated set **inlined**, logged
  with its single-source-of-truth cost — never a citation to a rule the agent
  cannot read.
- **Alternatives considered:**
  - *Adopt all five now.* Rejected: two have no trigger, and an agent nobody
    invokes is deleted under rule 3 — adopting them would create work to undo.
  - *Adopt only `step-reviewer` and improvise the milestone passes.*
    Rejected: the close is certain and near, and a ritual written during the
    close is written by the party it is meant to check.
  - *Pin a `model:` in the two milestone passes.* Rejected on the templates'
    own reasoning, which holds: the requirement is a **relation** — not the
    model that wrote the work — and no fixed id states a relation, since a
    pinned value becomes same-model the day implementation moves to it.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — which tooling templates are adopted, rule 3)

## D-012 — Adopt the four session rituals as skills

- **Date:** 2026-08-18
- **Step:** `step-004` — The session rituals
- **Context:** Rule 3 says a ritual repeated every step is a skill, and four
  templates were handed over for exactly the four moments this workflow has:
  session start, resumption after an interruption, handover for testing, and
  the post-approval close. Until now each was performed from `CLAUDE.md` and
  `.claude/docs/workflow.md` directly — which works, and which is precisely
  what an interrupted or context-compacted session does least reliably.
- **Decision:** Adopt all four at `.claude/skills/<name>/SKILL.md` —
  `orient`, `resume-step`, `handover-step`, `approve-step`. Where D-011 had a
  selection question to answer, this one does not: all four triggers are
  certain **and already firing**. Every step this repository has closed has
  performed the handover and the close by hand, and `step-005` closes the
  milestone. A ritual not adopted here is a ritual improvised in the moment
  it is needed, which is the failure the rule names.
- **How the templates were changed, and why each change:**
  - **The governance placeholders resolve at invocation — with no track
    table copied in.** Each skill states that the plan, the log and the
    specification mean the active track's, and points at `CLAUDE.md`'s track
    map for the resolution. Unlike an agent, a skill executes **in the
    invoking session**, which has just read that map; a fourth, fifth, sixth
    and seventh copy of it would be drift surface bought for nothing
    (rule 11).
  - **`orient`'s steps 1–2 were rewritten to `CLAUDE.md`'s multi-track
    routine.** The template enumerated the single-track shape — the active
    track's files only. The rule wins over a template's narrower
    enumeration, so the instantiation carries the root plan, the root log and
    the root specification as standing reading on every track, and the
    "another track's files load only on a named cross-track dependency"
    clause with them.
  - **`approve-step` keeps its resolve-from-the-closed-step exception,
    verbatim in substance.** It is the one that fails silently: step 3
    advances the `Current state` pointer, so from there on the pointer is the
    wrong answer, and step 5 names the closed step's track explicitly when it
    spawns the milestone passes.
  - **Two places take `just verify` where the template named the check entry
    point:** `resume-step`'s working-tree forensics and `approve-step`'s
    pre-commit gate. `just test` is currently the guard's own selftest and
    costs a fraction of a second, and both moments want the strongest
    evidence available — the forensic one because it localizes where an
    interruption landed, the close because the commit it gates receives the
    step tag and becomes the known-good state every later session anchors on.
  - **`{{STATE_CHECKS}}` is filled with real commands, each marked free**:
    the toolchain's presence, this project's own containers, images and
    volumes by name, the `.local/` scratch root, the unpushed-commit-or-tag
    question, and CI runs and published packages through the GitHub API. The
    gated counterparts are named as things to request and never run.
  - **One dead branch dropped:** `approve-step`'s "where no remote exists
    yet". The remote exists, is public and is recorded as satisfied in
    `PLAN.md`'s prerequisites. A branch that can never be taken is a branch
    nobody re-checks when it stops being true.
  - **The frontmatter rationale is a two-line pointer at the foot of each
    file, not a block repeated four times at the head.** The templates each
    carried a dozen lines explaining which frontmatter keys are omitted and
    why; that reasoning is a measured fact about the tooling, so it lives
    once in `.claude/docs/agents.md` §4 "A skill's frontmatter" and each
    skill cites it. The pre-handover review then found the citation itself
    repeated four times *above* "When to use" — a note addressed to whoever
    edits the file, sitting at the top of a file loaded to execute a ritual.
    It is now two lines at the foot. **Deleting it outright was the
    reviewer's recommendation and is not taken here:** `CLAUDE.md`'s pointer
    already triggers the read, so nothing would be lost — but the pointer
    form is what the operator adopted upstream in this exchange, and
    unadopting it is theirs to decide, not mine to do quietly.
- **The check family was extended, and proven red before being trusted.**
  `agent-frontmatter` now covers `.claude/skills/*/SKILL.md` alongside
  `.claude/agents/*.md` — this step lands the first files of that class, and
  rule 2 forbids the family arriving ahead of them. For a skill the name must
  match the **directory**, since every file is `SKILL.md`. Both failure modes
  were induced deliberately (a mismatched `name`, a missing frontmatter
  block) and both took the check red; the family is otherwise unchanged, and
  still checks only what is exact.
- **Measured, and it shapes every later step's test instructions:** a skill
  created mid-session is not loaded until the session restarts — `/orient`
  answered `Unknown skill: orient` with the file on disk and passing the
  frontmatter check. Same behaviour as an agent, recorded in
  `.claude/docs/agents.md` §3 next to it.
- **Alternatives considered:**
  - *Adopt only `handover-step` and `approve-step`, the two with the nearest
    triggers.* Rejected: `orient` runs at every session start and
    `resume-step` at the first interruption, which is not a scheduled event.
    The one ritual you cannot write when you need it is the recovery one.
  - *Copy the agents' track table into each skill, for symmetry.* Rejected as
    above: symmetry with an agent is not a reason when the reason the agent
    carries a table does not apply to a skill.
  - *Keep `allowed-tools` on the frontmatter as documentation of intent.*
    Rejected: it was measured elsewhere to restrict nothing and was not
    re-measured here, so writing it would assert an enforcement this
    repository cannot back. The disciplines stay prose, and what binds stays
    `.claude/settings.json` and the guard.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — which tooling templates are adopted, rule 3)

## D-013 — Section pointers are checked by their title, not their number

- **Date:** 2026-08-18
- **Step:** `step-004` — The session rituals
- **Context:** The operator's review of `step-004` found four rituals pointing
  at `.claude/docs/agents.md` **§5** where the section is §4. The pointers
  were written from the numbering as it stood *before* a new section was
  inserted ahead of it — **in the same commit**. Nothing was malformed,
  nothing was missing, and the harness had no way to see it: a reference
  correct when written and invalidated by an edit beside it. The same shape as
  the sequencing a step lost when it moved tracks at the bootstrap
  (`.claude/docs/workflow.md` §5 "The harness contract"), where three
  consistency passes all came back clean because each asked *is this
  internally consistent?* and none asked *did something stop being true?*
- **Decision:** Adopt `scripts/check_section_references.py` as the
  `section-references` hook. It recognises exactly one shape — a backticked
  path ending in `.md`, then §N, then an optional quoted title — resolves the
  path, and asserts the section exists and that the quoted title is a prefix
  of its heading. Inside `.claude/agents/` and `.claude/skills/` the title is
  **required**; elsewhere it is optional and checked when present.
- **The measurement that chose the design, recorded because without it the
  title looks like over-engineering:** the first draft checked only that §N
  existed. Run against the defect as committed, **it passed** — §5 did exist.
  A section number is a reference with no redundancy, so any number that
  happens to exist looks right; a number and a title cannot both be wrong in
  the same direction by accident. The title is not decoration, it is the
  entire mechanism.
- **Why the title is required in one class and optional elsewhere, and what
  that actually buys.** There are 29 such pointers in the repository and 8 of
  them are in the governance class (`.claude/agents/` contributes none; the
  rituals carry them all). That class is where a pointer is followed by a
  session that will not re-read the target to check, and where the defect
  occurred. Requiring
  titles in `CLAUDE.md`, the three plans and the logs would be prose churn in
  the files this check exists to protect rather than rewrite — and `CLAUDE.md`
  has six lines of headroom against D-002's budget. Making it uniform later is
  one tuple in the script; the operator's call, not a rewrite.

  **Stated plainly, because the paragraph above could be read as claiming
  more:** the title mode — the one this entry calls "the entire mechanism" —
  covers 8 of 29 pointers. The other 21 get the number-only check that the
  measurement above found insufficient against this very defect. That check
  is not worthless there: it still catches a deleted section, a renumbering
  that removes one, and a pointer into a file that no longer exists. But it
  would not catch this bug in `CLAUDE.md` or in a plan, and the entry should
  not pretend otherwise. The pre-handover review made this finding, and it is
  recorded rather than silently narrowed.
- **Two things kept deliberately out of scope.** Prose that names a section
  any other way — "section 2", "root §3" — is not recognised: every
  `SPECIFICATIONS.md` is read-only under rule 1, so a check that could go red
  on a specification's own cross-references would be a check nobody is allowed
  to turn green. And the check scans whole documents rather than single lines,
  because these files wrap at ~76 columns: a line-based scan silently stops
  checking exactly the long titles most worth citing.
- **Proven red before being trusted**, on all four ways it can fail: the
  defect as committed (right number, wrong section), a title dropped in the
  class that requires one, a target section renamed under correct pointers,
  and a pointer into a file that does not exist. Each took the check red with
  a message naming the fix; the wrapped-title case stays green.
- **Alternatives considered:**
  - *No check — the staleness sweep plus re-reading the target section*, which
    is what the operator offered if a check was not cheap. Rejected: it came
    in at one narrow script with one exact rule, and the defect class has now
    produced two incidents in this repository's short history.
  - *Check the number only.* Rejected on the measurement above — it is the
    version that passed the bug.
  - *Requiring the title everywhere, now.* Not rejected — deferred to the
    operator with the coverage stated above, since it is prose churn across
    `CLAUDE.md`, three plans and three logs, and `CLAUDE.md` has six lines of
    headroom against D-002's budget.
  - *Fold it into the `agent-frontmatter` script.* Rejected: that check asks
    whether a definition loads, this one asks whether a reference resolves,
    and they cover different file sets. One question per check keeps a red
    run's message unambiguous.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names, rule 3). The four-pointer fix
  itself was the operator's instruction, not a choice.

## D-014 — The CI workflow's shape: two gates, one definition, no schedule

- **Date:** 2026-08-18
- **Step:** `step-005` — The same harness on the forge
- **Context:** The plan asks for a workflow that **reuses the harness entry
  points** rather than restating a single check, for check and test as
  separate jobs, for the toolchain cached, and for a proof that a fresh setup
  still works — with the explicit instruction not to invent a schedule for
  that proof, because root §8's own scheduled jobs (`step-010`, `step-011`)
  inherit the duty when they arrive.
- **Decision:** one workflow, `.github/workflows/ci.yml`, with:
  - **Triggers** `push` narrowed to `main`, `pull_request`, and
    `workflow_dispatch`. Narrowing `push` is what stops a pull request from a
    branch of this repository producing two runs of the same commit;
    `workflow_dispatch` is what lets the operator re-prove a fresh setup
    without pushing. **No `schedule:`**, and the file says so in a comment
    that names §2.8, so a later session does not read the absence as an
    oversight and add one.
  - **Two jobs from one definition**, a `strategy.matrix` over
    `[check, test]`, `fail-fast: false`. They are separate gates in the
    checks list — `just check` and `just test` — and they differ in exactly
    one step. Written as two job blocks they would carry a duplicated
    checkout, toolchain install and setup, which is precisely the material
    that drifts; `fail-fast: false` keeps a failing `check` from cancelling
    `test` and hiding half of what the run was asked to report.
  - **Only pre-commit's hook environments cached**, keyed on
    `.pre-commit-config.yaml` *and* `requirements.txt` — the two files that
    decide what those environments contain. The venv is built and
    `requirements.txt` installed from scratch on every run, so **the fresh
    setup is the run itself**, not a job of its own, and a change to either
    file gives a genuinely cold build.
  - **The `check` leg owns the cache.** Both legs restore; only `check`
    saves, and only when the restore missed. Two jobs racing to write one key
    makes a green run noisy for no gain, and the save is deliberately not
    conditioned on success: a run whose gate went red still built the
    environments, and discarding them would make the next attempt pay again.
  - **`runs-on: ubuntu-24.04`**, pinned rather than `ubuntu-latest`. §2.1
    makes this project amd64-only, and a runner image that moves under a
    floating label is the one variable a checksum cannot pin.
- **Why `just setup` runs in the `test` leg too**, where `just test` needs
  none of what it installs today: the two legs are the same harness up to
  their last step, and an exception for one of them is a thing to remember on
  the day `just test` grows a dependency. The cost is a cache restore.
- **Rehearsed locally before the one run that can prove it**, since this
  step's gate is a real push: a fresh `--no-hardlinks` clone with an empty
  `PRE_COMMIT_HOME` — the closest thing to a cold runner this machine can
  offer — ran `just setup` in **23 s** and `just verify` green. What that
  rehearsal cannot cover is the runner itself: the `just` download, the
  action versions and the workflow syntax are only exercised on the forge.
- **The cache measured, because the deliverable asks for one and the number
  argues with it:** a cold build of pre-commit's hook environments is 474 MB
  here, of which **317 MB is the Go toolchain** pre-commit fetches for
  actionlint (this machine has no `go`; a runner does, which is likely to
  make CI's copy smaller). Against a 23 s cold build, a cache of that size is
  close to break-even, and it is kept because the step's deliverables ask for
  the toolchain cached. Recorded so a later session can drop or narrow it on
  this evidence rather than on a hunch — and so the number can be compared
  against a real run's timings.
- **What a green run means here, recorded because a badge outlives its
  context:** at this step the repository contains no Dockerfile, no image and
  no workflow but this one. Green says the documents, the governance tooling
  and the Bash guard are well-formed and the guard's behaviour passes. It
  says nothing about an image, and the workflow's own header says so.
- **Alternatives considered:**
  - *Two explicit job blocks.* Rejected on the duplication above — the
    shared half is exactly what must not drift.
  - *A separate "fresh setup" job or a keep-alive schedule.* Rejected: the
    plan forbids inventing a schedule, and every run is already a clean
    checkout running the documented command in full.
  - *One cache step per leg with the same key.* Rejected: harmless but noisy,
    and a green run that logs a contention notice teaches a reader to skim.
  - *`ubuntu-latest`.* Rejected for the pin above.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names, rule 3). The deliverables
  themselves are the plan's.

## D-015 — CI gets `just` from the project's own release, checksum-verified

- **Date:** 2026-08-18
- **Step:** `step-005` — The same harness on the forge
- **Context:** `just` is the runner that invokes the setup command, so it
  cannot be installed by it (D-006). Locally the operator provides it
  (`.claude/docs/environment.md` §1). A hosted runner has nobody to, and the
  runner images do not ship it, so CI has to fetch it — the one dependency of
  this workflow that arrives from outside the pinned toolchain, in a file
  that will hold registry credentials from `step-006` onward.
- **Decision:** fetch the release archive from `casey/just` by pinned
  version and verify it against the SHA-256 that release publishes, in a
  `run:` block of six lines. Version and checksum sit together in the
  workflow's `env:` so they can only move as a pair. The version pinned,
  `1.45.0`, is the one measured on this machine — CI and the operator run the
  same `just`, which matters because `just --fmt` is an unstable feature the
  check family invokes.
- **Actions are pinned by commit SHA**, with the version tag in a trailing
  comment: `actions/checkout` and `actions/cache` only, both first-party. A
  tag is a movable pointer, and this is the workflow file that later grows
  publish rights — establishing the pin at the first workflow costs two
  comments and nothing later.
- **The rejected convenience, named because it is the obvious one:**
  `rust-just` on PyPI would have made this a one-line `pipx install` and a
  pinned dependency like any other. Its metadata was read rather than
  assumed: the homepage points at `casey/just`, but the **repository** is
  `gnpaone/rust-just` — a third party's repackaging of the binary. That is a
  supply-chain link into a workflow that will publish public images, bought
  to save five lines. Rejected on that ground alone; the packaging is
  probably fine, and "probably fine" is not the standard for a link nobody
  would notice going bad.
- **Alternatives considered:**
  - *A `setup-just` action.* Same objection one level up — a third-party
    action, pinnable by SHA but still fetching what it likes, and it replaces
    six auditable lines with a dependency.
  - *An unverified `curl | tar`.* Rejected: pinning a version without
    pinning the bytes pins nothing.
  - *Installing `just` from a distribution package.* Not available at the
    pinned version on the runner image, and it would let CI and this machine
    run different `just` versions.
- **The maintenance edge, stated rather than discovered later:** a `just`
  upgrade on this machine now has a second place to move, and the two files
  that name the version — this workflow and `.claude/docs/environment.md` —
  will disagree silently if only one is updated. Nothing checks it today; the
  staleness sweep at each step close is what is expected to catch it.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer, rule 3).

## D-016 — actionlint is the workflow-validation family, ambient integrations off

- **Date:** 2026-08-18
- **Step:** `step-005` — The same harness on the forge
- **Context:** Rule 2 requires a check family to arrive with the first file
  of its class, in the step that lands it. `.github/workflows/ci.yml` is the
  first workflow, and `check-yaml` proves only that it is YAML — every
  interesting mistake in a workflow (a mistyped runner label, an input the
  action does not define, a malformed expression, a bad `uses:` reference) is
  valid YAML and is otherwise discovered by a red run on the forge, one push
  at a time.
- **Decision:** adopt `rhysd/actionlint` v1.7.12 as the `actionlint` hook,
  pinned by revision like every other family, with
  `args: [-shellcheck=, -pyflakes=]`.
- **Why the two integrations are switched off, and why that is not a
  weakening:** actionlint shells out to whichever `shellcheck` or `pyflakes`
  is on PATH and silently skips them when absent. GitHub's runner images ship
  shellcheck; this machine does not
  (`.claude/docs/environment.md` §1). Left on, the same commit would be
  checked more strictly on CI than locally — a local green and a red run on
  the forge, which is the exact failure the workflow beside it exists to make
  impossible. Shell gets a pinned family of its own with the first shell
  script (rule 2, never ahead of need); until then the workflow's `run:`
  blocks stay short enough to read.
- **Measured against a deliberate defect, not assumed** — a throwaway
  workflow carrying three planted errors, run through `just check` and then
  deleted. Caught: `runs-on: ubuntu-latst` (with the valid label list, which
  is also how `ubuntu-24.04` was confirmed to exist), and an undefined input
  on `actions/checkout@v4`. **Not caught:** `github.event.hed_commit.message`
  — `github.event` is an untyped payload, so any field name is plausible to
  it. Recorded so the family's reach is known rather than believed: it checks
  the workflow's structure and its references, not the truth of an expression
  into the event payload.
- **Alternatives considered:**
  - *`check-yaml` alone.* Rejected — see the context; it passes every
    mistake worth catching.
  - *`actionlint-docker` or `actionlint-system`.* Rejected: the first needs a
    daemon for a linter, the second takes whatever version is installed,
    which is a family that cannot be pinned.
  - *Adding a security linter (`zizmor`) alongside.* Deferred, not rejected:
    its subject is permissions, untrusted inputs and injection in workflows
    that handle secrets, and this workflow has none. `step-006` is where that
    becomes a real question.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names, rule 3).

## D-017 — The first `detect-secrets` false positive: an inline pragma, no baseline

- **Date:** 2026-08-18
- **Step:** `step-005` — The same harness on the forge
- **Context:** D-008 adopted `detect-secrets` deliberately without a
  `.secrets.baseline`, and said a baseline would arrive "at the moment a real
  false positive appears". It appeared here: the pinned SHA-256 of the `just`
  release archive (D-015) is a 64-character hex string, and the entropy
  heuristic cannot tell a published checksum from a leaked credential.
- **Decision:** annotate the line with the tool's own
  `# pragma: allowlist secret`, and keep the repository baseline-free. The
  annotation sits beside the value with two lines saying what it is, where a
  reviewer reading the workflow will see it; a baseline is a file of hashes
  that must be regenerated whenever any scanned file changes, and it hides
  the exemption in a place nobody reads. `.pre-commit-config.yaml`'s comment
  was rewritten to record this outcome rather than keep promising a baseline.
- **When a baseline becomes right:** when inline annotations become numerous
  enough that no one can see them all — checksums for several pinned
  downloads, say. One is not that.
- **Alternatives considered:**
  - *Generate `.secrets.baseline`.* Rejected on the maintenance and
    visibility grounds above; deferred, not refused.
  - *Move the checksum out of the workflow into a file the scan excludes.*
    Rejected: an exclusion that hides a whole file is broader than the
    exemption needed, and it separates the checksum from the version it must
    move with.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer, rule 3).
