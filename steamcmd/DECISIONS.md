# Decision log — `sc` track (steamcmd builder image)

Decisions governing the files of this directory: the builder image's
Dockerfile, its README, and this track's specification pointer.
Repository-wide decisions — including everything about **publication**, which
the root track owns — live in the root `DECISIONS.md`.

## How to read this log

Three kinds of decision are recorded here, and a reviewer treats them
differently:

- **Choices made with the operator** — specification amendments, scope calls,
  step reordering.
- **Choices made inside a specification "should"** — the specification permits
  deviating from a recommended default *with reason*, and the reason is in the
  entry. **A reviewer judges these on the recorded reasoning**, so the
  reasoning stays in the entry in full even when the entry is later compacted;
  a deviation from a "should" with **no** entry is a finding. Code
  contradicting a **must** is a defect, never a decision.
- **Choices left to the implementer** — mechanism where the specification
  states only the observable: how the build-time credential channel of root
  §4.3 is implemented, how the image is laid out, what the local build recipe
  is called.

Ids are `D-NNN`, numbered in **file order** (which is chronological),
**frozen once assigned and never reused**. Ids are **per log**: this file, the
root `DECISIONS.md` and `project-zomboid/DECISIONS.md` each start at `D-001`,
so a citation crossing logs names the file — for the root log,
`DECISIONS.md D-NNN`.

**Where an amendment lands.** This track's specification is a pointer and
carries no requirements (root §6), so a change to what binds the builder is an
amendment to the **root** document and its decision entry goes in the **root**
log, in the same commit as the amendment, with the `sc` step id in the commit
subject — the log follows the document being amended, not the step doing the
work.

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

*No entries yet. The first will come from `step-sc-001`.*
