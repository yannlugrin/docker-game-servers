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

```
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
    Rejected: `Plan conventions` became `workflow.md` §1 with a read trigger
    rather than disappearing, which keeps it reachable for the closes that
    precede `/approve-step`.
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
