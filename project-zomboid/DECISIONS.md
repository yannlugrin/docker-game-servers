# Decision log — `pz` track (Project Zomboid)

Decisions governing the files of this directory: the Project Zomboid
image's Dockerfile, entrypoint, healthcheck, shipped tooling, README, and
this track's specification. Repository-wide decisions live in the root
`DECISIONS.md`.

## How to read this log

Three kinds of decision are recorded here, and a reviewer treats them
differently:

- **Choices made with the operator** — specification amendments (including
  every resolution of an open fact that changes a requirement, a variable's
  mandatory/optional tier, a documented capability or limitation, or the
  ship decision), scope calls, step reordering.
- **Choices made inside a specification "should"** — the specification
  permits deviating from a recommended default *with reason*, and the reason
  is in the entry. **A reviewer judges these on the recorded reasoning**, so
  the reasoning stays in the entry in full even when the entry is later
  compacted; a deviation from a "should" with **no** entry is a finding.
  Code contradicting a **must** is a defect, never a decision. Note that
  this specification may deviate from a root "should" with reason but
  **never weakens a root "must"** (root §6).
- **Choices left to the implementer** — mechanism where the specification
  states only the observable: the override-application mechanism, the
  recognition mechanism for a self-generated RCON password, the state-root
  path, the entrypoint's language and internal shape.

Ids are `D-NNN`, numbered in **file order** (which is chronological),
**frozen once assigned and never reused**. Ids are **per log**: this file
and the root `DECISIONS.md` each start at `D-001`, so a citation crossing
logs names the file (`DECISIONS.md D-004` for the root log).

**Where an amendment lands.** A step of this track that amends the **root**
specification logs its decision in the **root** log, in the same commit as
the amendment, with the `pz` step id in the commit subject — the log follows
the document being amended, not the step doing the work. An amendment
touching both specifications is two entries, one per log, cross-citing.

Every resolution of an open fact of §2 lands here (or in the root log, per
the rule above) **before or with** the specification amendment it justifies,
never as a rationalisation after it, and the amendment commit carries the
decision entry and the specification text and nothing else.

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

*No entries yet. The first will come from `step-pz-001`.*
