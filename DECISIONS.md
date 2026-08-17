# Decision log — root track

Decisions governing repository-wide files: the harness, the builder image,
CI, the repository-wide documentation of root §9, and the workflow itself.
Decisions governing a game image's files live in that track's log
(`project-zomboid/DECISIONS.md`).

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
**frozen once assigned and never reused**. Ids are **per log**: this file
and `project-zomboid/DECISIONS.md` each start at `D-001`, so a citation
crossing logs names the file (`project-zomboid/DECISIONS.md D-003`).

A `pz`-track step that amends the **root** specification logs its decision
**here**, in the same commit as the amendment, with the `pz` step id in the
commit subject — the log follows the document being amended, not the step
doing the work. An amendment touching both specifications is two entries,
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
- **Step:** bootstrap (executed at `step-008` — Builder publication on CI)
- **Context:** Root §2.6 records that Docker Hub rate-limits anonymous pulls,
  which makes every CI pull of the Debian base from shared-IP hosted runners
  an intermittent-throttling risk, and asks the implementation to decide about
  it **deliberately rather than after the first failed build**.
- **Decision:** CI pulls the base anonymously. The pre-committed response to
  throttling is **authenticated pulls with a Docker Hub credential the
  operator supplies**, wired as a CI secret at the moment limits are actually
  observed. `step-008` therefore builds no mirror and adds no credential now,
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
