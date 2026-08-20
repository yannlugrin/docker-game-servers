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

A **compacted** entry (below) keeps the heading, the step, a short decision
statement carrying the reason that stops it being re-litigated, and the
approval line, with detail left to git history — none of that is a shape
change, since a closed or superseded entry has no open "Context" or
"Alternatives" left to weigh.

---

## D-001 — Adopt the staged, plan-gated implementation workflow

- **Date:** 2026-08-17
- **Step:** bootstrap (precedes `step-000`)
- **Decision:** Adopt the operator's staged, plan-gated workflow and encode it
  in `CLAUDE.md` as its standing rules: read-only specifications amended only
  through a logged decision, one operator-gated step at a time, all memory in
  files (a plan and log per track, `CLAUDE.md`, `.claude/docs/`), decisions
  logged per track, secrets never committed, small track-qualified commits,
  English, `README.md` as neutral entry point, implementer-driven bug reports
  within a stated boundary, a persistence budget, and proportion. Two tracks
  at adoption — root and `pz` — the track-per-game criterion later superseded
  by D-005. Chosen because a session with no persistent memory needs a
  written record to establish state and surface drift; rejected: no plan/log
  at all, one repository-wide plan, Claude Code's auto memory (unversioned,
  outside review), and delivering the foundation in one batched step.
- **Approved by:** operator (the workflow is the operator's own; this entry
  records its adoption)
- Detail in git history, before tag `step-000`.

## D-002 — `CLAUDE.md`'s line budget, and the lazily-loaded mechanics file

- **Date:** 2026-08-17
- **Step:** bootstrap
- **Decision:** Extract mechanics and reasoning to `.claude/docs/workflow.md`,
  a lazily-loaded file with its own read triggers, leaving `CLAUDE.md` the
  rules and pointers to it; set this project's budget at **280 lines hard,
  ~250 target** rather than the prompt's 220. 200 is not reachable at
  operative-only density — rule 9's boundary enumeration alone is ~30 lines
  and is carried whole by rule, and the remaining ten rules run ~120 more; the
  only route below ~250 is moving rule text itself out of the always-loaded
  file, which defeats the point of a standing rule. Rejected: stripping
  rationale in place (still misses 220), deleting a required section,
  compressing rule 9's enumeration, and keeping 220 with the file over budget
  and no ruling.
- **Approved by:** operator
- Detail in git history, at tag `step-000` (`CLAUDE.md` fell from 301 to 254
  lines by the extraction alone).

## D-003 — Base-image pulls stay anonymous until limits bite

- **Date:** 2026-08-17
- **Step:** bootstrap (executed at `step-006` — Builder publication on CI)
- **Decision:** CI pulls the Debian base anonymously; the pre-committed
  response to Docker Hub throttling is an operator-supplied credential wired
  as a CI secret **only once throttling is actually observed** — a
  deliberate decision taken in advance per root §2.6, not a wait-and-see.
  Rejected: mirroring the base into GHCR now (machinery for an unmeasured
  risk) and authenticating from the start (spends a credential on a risk not
  yet observed).
- **Approved by:** operator
- Detail in git history, at tag `step-000`.

## D-004 — Every shipped image directory carries a specification document

- **Date:** 2026-08-17
- **Step:** bootstrap
- **Decision:** Amend root §6 so every shipped image directory — not just
  each game — carries a specification document: the per-game form, or a
  pointer form for a component the root document already specifies in full
  (today only `steamcmd/`). Retitled "Per-image specifications" so no
  existing citation breaks. Chosen because a directory with nothing of its
  own would otherwise force every reader to interpret a missing file, which
  is the drift a multi-document specification exists to prevent. Rejected:
  stating the builder's rule under §4 alone (drift), and leaving
  `steamcmd/` without a document (the gap itself).
- **Approved by:** operator (who identified the gap and ordered the
  amendment)
- **Sequel:** the track and ownership consequences are D-005.
- Detail in git history, at tag `step-000`.

## D-005 — Track ownership follows artifacts, not blast radius

- **Date:** 2026-08-17
- **Step:** bootstrap
- **Decision:** Ownership follows **where the artifacts live**, not how far
  their effects reach. The root track owns what lives at the repository root
  or in a shared directory — the harness, `docs/`, and CI in
  `.github/workflows/`, including publication of another track's image —
  and that enumeration is closed. Every shipped image directory is a track
  carrying a specification document (D-004): `sc` (`steamcmd/`) and `pz`
  (`project-zomboid/`) today, superseding D-001's per-game criterion.
  Downstream ripple is expressed by a cross-track dependency edge, never by
  moving ownership — a criterion this repository will need again at the next
  component.
- **Alternatives considered:** three grounds for keeping the builder
  root-owned, each overruled — "no specification document of its own" (D-004
  closed the gap), "its work ripples repository-wide" (conflates coupling
  with ownership), and "three steps do not earn the machinery" (a track costs
  two files and a table row; its absence costs a future maintainer a decision
  log they cannot find).
- **Approved by:** operator (who supplied the criterion and overruled the
  proportion argument)
- Detail in git history, at tag `step-000`.

## D-006 — The toolchain bootstrap: a venv behind `just setup`

- **Date:** 2026-08-17
- **Step:** `step-000` — The harness skeleton, local only
- **Decision:** `just setup` is the one documented setup command: it creates
  `./.venv`, installs `requirements.txt` (pinning only `pre-commit`), and
  runs `pre-commit install`. Every linter is declared and pinned by revision
  in `.pre-commit-config.yaml` instead, so nothing carries two disagreeing
  pins; the pin is a direct `==`, not a hash lock, since the dependency
  surface is one runner rather than a shipped runtime; `just` itself stays a
  prerequisite the setup command cannot install. Rejected: `uv`/`pipx`
  (absent on this machine, adds a step ahead of the one documented command),
  a `scripts/setup.sh` fallback (a shell script needing its own check family
  for a prerequisite the harness needs anyway), pinning `rust-just` into the
  venv (a second `just` whose selection would depend on `PATH`), and a
  system-wide `pre-commit` (unpinned, invisible to a fresh clone).
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names)
- Detail in git history, at tag `step-000`.

## D-007 — What `just check` covers at `step-000`

- **Date:** 2026-08-17
- **Step:** `step-000` — The harness skeleton, local only
- **Decision:** `just check` carries two groups, none of which rewrites a
  file: well-formedness per artifact class present (`check-json`,
  `check-yaml`, `just --fmt --check`), and hygiene guards admitted on **blast
  radius rather than artifact class** — large-file, shebang, merge-conflict,
  case-conflict, submodule and line-ending guards, plus `.gitattributes`
  forcing LF — because a multi-gigabyte blob or a secret in history is
  unrecoverable without rewriting it, which rule 9 protects. Markdown/prose
  lint and every repairing hook are deliberately deferred to `step-001`,
  since two hooks (`trailing-whitespace`, `end-of-file-fixer`) have no
  check-only mode and would let a failing check mutate a read-only
  specification.
- **Approved by:** operator (who asked which hooks were planned and
  identified the gap)
- Detail in git history, at tag `step-000`.

## D-008 — Rule 5 gets a mechanical guard: `detect-secrets` over the file list

- **Date:** 2026-08-17
- **Step:** `step-000` — The harness skeleton, local only
- **Decision:** Adopt `detect-secrets` v1.5.0 plus `detect-private-key`, run
  **without a `.secrets.baseline`** — a baseline is an allowlist for known
  false positives the tree did not yet have, and one built in anticipation is
  what rule 11 rejects. (The first real false positive, and the outcome, is
  D-017.) Rejected: `gitleaks` (its hook scans the staged diff, not the file
  list `just check` is built to see untracked files with), `detect-private-key`
  alone (catches key blocks only, not passwords or tokens), and generating a
  baseline now (would record an unreviewed tree as reviewed).
- **Approved by:** operator (who selected secret scanning from a proposal
  after the gap was reported)
- Detail in git history, at tag `step-000`.

## D-009 — The document lint: `pymarkdown` and `codespell`, bent to fit

- **Date:** 2026-08-17
- **Step:** `step-001` — The governance and prose lint
- **Decision:** Adopt `pymarkdown` v0.9.39 (structure) and `codespell` v2.4.3
  (spelling), both pinned and report-only, bent to the read-only
  specifications in exactly three measured ways — enabling the
  `markdown-tables` extension, exempting table rows from the line-length rule
  (`md013.tables: false`), and ignoring the one word codespell contests in
  root §3.4 — after which every other rule of both tools reports zero across
  the governance and human-facing documents. One read-only specification line
  was rewrapped (no word changed, verified by a whole-document word-sequence
  diff) on the operator's explicit authorisation, retiring a fourth bend.
  Rejected: `markdownlint`/`markdownlint-cli2` (would add a whole node
  toolchain for a result already achieved), `vale` (needs a style package
  tuned against 2,700 lines of deliberate prose), and disabling `md040`
  instead of labelling three fences.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names); the one specification edit
  was the operator's, on condition of no word changed.
- Detail in git history, at tag `step-001`.

## D-010 — The permission and hook baseline

- **Date:** 2026-08-17
- **Step:** `step-002` — The permission and hook baseline
- **Decision:** Make rule 9's boundary mechanical with two paired halves:
  `.claude/hooks/bash_guard.py`, instantiated from the handoff template with
  **only its `REGISTRY` edited** (`git`/`docker` unchanged, `gh` and
  `steamcmd` added as grants); and `.claude/settings.json` — a broad `allow`
  per registry tool the guard claws back from, no `ask` on anything the guard
  gates, an eight-entry `deny` backstop against permanent history loss,
  `defaultMode: acceptEdits`. Measurement, not preference, ruled out every
  other mode (`.claude/docs/permissions.md` §1) and proved **a hook fails
  open** and **the implementer can edit its own permission boundary** under
  what ships — so this baseline stops mistakes, not a determined agent; the
  operator reading the diff is what bounds the latter. The hardening this
  implies (`.claude/docs/permissions.md` §7) is proposed and **deliberately
  not applied**.
- **Approved by:** operator, who reviewed the proposal, applied the settings
  on 2026-08-17, and authorised the fail-open probe. §7's hardening remains
  open, not covered by this approval.
- Detail in git history, at tag `step-002`.

## D-011 — Adopt three reviewer agents, and defer two

- **Date:** 2026-08-17
- **Step:** `step-003` — The reviewer agents
- **Decision:** Adopt `step-reviewer`, `state-reviewer` and `optimize-memory`
  at `.claude/agents/`, since the first milestone close (`step-005`) needs
  both milestone passes already built rather than improvised at the
  boundary. `code-reviewer` and `test-reviewer` stay unadopted, their
  triggers genuinely absent, and remain on `CLAUDE.md`'s list so a citing
  ritual does not dangle. Governance placeholders resolve at invocation
  through a track table, named at spawn for the two close passes since the
  close ritual has already advanced the pointer they would otherwise read;
  `optimize-memory`'s budget follows D-002's 280/~250. **Both probes were
  run, not argued** (`.claude/docs/agents.md`): `CLAUDE.md` does reach a
  subagent, so the pre-committed inlining branch does not fire, and `tools:`
  binds by omission — though `Bash` still writes, so a reviewer's read-only
  discipline rests on its prose, not its tool list.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — which tooling templates are adopted, rule 3)
- Detail in git history, at tag `step-003`.

## D-012 — Adopt the four session rituals as skills

- **Date:** 2026-08-18
- **Step:** `step-004` — The session rituals
- **Decision:** Adopt all four templates at `.claude/skills/<name>/SKILL.md`
  — `orient`, `resume-step`, `handover-step`, `approve-step` — since all four
  triggers were already firing (every prior close had been performed by
  hand). Governance placeholders resolve at invocation with **no track table
  copied in**, since a skill executes in the invoking session, which has just
  read `CLAUDE.md`'s map; `orient`'s steps 1–2 were rewritten to the
  multi-track routine, the rule winning over the template's narrower
  single-track enumeration; the frontmatter rationale repeated per file
  became a two-line pointer to `.claude/docs/agents.md` §4. Measured: a
  skill created mid-session is not loaded until the session restarts, the
  same as an agent.
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — which tooling templates are adopted, rule 3)
- Detail in git history, at tag `step-004`.

## D-013 — Section pointers are checked by their title, not their number

- **Date:** 2026-08-18
- **Step:** `step-004` — The session rituals
- **Decision:** Adopt `scripts/check_section_references.py` as the
  `section-references` hook: it resolves a backticked `path.md` §N pointer
  and asserts both that the section exists **and**, where a quoted title is
  present, that it prefixes the heading — required in `.claude/agents/` and
  `.claude/skills/`, optional elsewhere. Chosen because a number-only check
  was measured to **pass** the defect it was built to catch (four rituals
  pointing at the wrong §5 after an insertion shifted it) — a section number
  is a reference with no redundancy, so any number that happens to exist
  looks right; the title is what makes the check able to fail. Covers 8 of
  29 pointers in title mode; requiring titles everywhere is deferred to the
  operator (prose churn across `CLAUDE.md`, three plans and three logs).
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer — the harness's shape and names, rule 3); the four-pointer fix
  itself was the operator's instruction.
- Detail in git history, at tag `step-004`.

## D-014 — The CI workflow's shape (amended ×2; evolution in git history)

- **Date:** 2026-08-18 (amended 2026-08-20 ×2)
- **Step:** `step-005` — The same harness on the forge
- **Decision:** One workflow, `.github/workflows/ci.yml`: `push` narrowed to
  `main` plus `pull_request` and `workflow_dispatch`, **no `schedule:`**
  (root §2.8's scheduled jobs arrive at `step-010`/`step-011`); `check` and
  `test` as two jobs from one matrix definition rather than duplicated
  blocks; `ubuntu-24.04` pinned rather than a floating label; one run per
  ref, `main` exempt from cancellation so a tagged close or a scheduled run
  is never left unrecorded. **No cache**, measured (474 MB of hook
  environments against a 37 s cold `just setup`) and dropped by the operator
  before the first run rather than after. **The Python interpreter, first
  left unpinned deliberately as an early-warning channel, was pinned to 3.14
  after the very first CI run died** on `ubuntu-24.04`'s 3.12.3 against the
  guard's `PurePath.full_match` (3.13+) — the floor is now stated in
  `README.md` and `.claude/docs/environment.md` §1; patching the guard
  itself was declined and reported instead, since `step-002` changed only
  its `REGISTRY`.
- **Approved by:** implementer, within latitude (the harness's shape and
  names, rule 3); the cache drop and the Python pin were both the operator's,
  taken 2026-08-20.
- Detail in git history, at tag `step-005`.

## D-015 — CI's `just`, checksum-verified (amended; evolution in git history)

- **Date:** 2026-08-18 (amended 2026-08-20)
- **Step:** `step-005` — The same harness on the forge
- **Decision:** CI fetches the `just` 1.45.0 release archive from
  `casey/just` and verifies it against the published SHA-256, version and
  checksum pinned together in `env:`, matching this machine's own version
  exactly because `just --fmt` is version-sensitive. Actions are pinned by
  commit SHA, with `.github/dependabot.yml` added (amendment, 2026-08-20) as
  the updater a SHA pin needs to keep moving rather than merely looking
  maintained. Rejected: `rust-just` on PyPI and any third-party `setup-just`
  action (both a supply-chain link into a workflow that will publish public
  images, for five lines saved), an unverified `curl | tar`, and
  `apt-get install` (Ubuntu freezes universe at release, so `ubuntu-24.04`
  cannot offer 1.45.0; `ubuntu-26.04` would, but is public preview and
  unknown to actionlint — deferred, not rejected).
- **Approved by:** implementer, within latitude (workflow choices left to the
  implementer, rule 3)
- Detail in git history, at tag `step-005`.

## D-016 — actionlint is the workflow-validation family, ambient integrations off

- **Date:** 2026-08-18
- **Step:** `step-005` — The same harness on the forge
- **Decision:** Adopt `rhysd/actionlint` v1.7.12 pinned by revision, with
  `-shellcheck=` and `-pyflakes=` switched off — both tools shell out to
  whatever is on `PATH`, GitHub's runners have `shellcheck` and this machine
  does not, and a workflow checked more strictly on CI than locally is the
  exact divergence this file exists to prevent. Measured against a
  deliberately planted three-defect workflow: caught a mistyped runner label
  and an undefined action input, did not catch a mistyped field on the
  untyped `github.event` payload — recorded so the family's reach is known,
  not assumed. Rejected: `check-yaml` alone (passes every mistake worth
  catching), `actionlint-docker`/`actionlint-system` (need a daemon or an
  unpinnable ambient version), and adding `zizmor` now (its subject —
  secrets, untrusted input — first arrives at `step-006`).
- **Approved by:** implementer, within latitude (the harness's shape and
  names, rule 3)
- Detail in git history, at tag `step-005`.

## D-017 — The first `detect-secrets` false positive: an inline pragma, no baseline

- **Date:** 2026-08-18
- **Step:** `step-005` — The same harness on the forge
- **Decision:** D-008's deferred baseline question arrived — the pinned
  `just` release checksum (D-015) is a 64-character hex string the entropy
  heuristic cannot tell from a credential — and the answer is an inline
  `# pragma: allowlist secret` beside the value, not a `.secrets.baseline`: a
  baseline is regenerated whenever any scanned file changes and hides the
  exemption where nobody reads it. Revisit toward a baseline once inline
  annotations become numerous enough that no one can see them all; one is
  not that.
- **Approved by:** implementer, within latitude (rule 3)
- Detail in git history, at tag `step-005`.
