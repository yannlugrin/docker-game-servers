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
  proposed to the operator at `step-001`.

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
