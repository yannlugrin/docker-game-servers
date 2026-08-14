# Root track — decision log

Decisions governing repository-wide files land here; each component
track keeps its own log, and decision ids are per log — a citation
crossing logs names the file (`project-zomboid/DECISIONS.md D-003`).

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
