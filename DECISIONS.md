# Decisions — root track

Decision log for repository-wide and cross-track choices (CLAUDE.md
rule 4). Entry format: `D-NNN` id (file order, frozen once assigned,
never reused; ids are per-log — cross-log citations name the file, e.g.
`project-zomboid/DECISIONS.md D-003`), date, plan step, context,
decision, alternatives considered, approved by. Entries citing
not-yet-started steps give number *plus title*.

## D-001 — Adoption of the gated, file-memory workflow with per-track organization

- **Date**: 2026-08-13
- **Step**: bootstrap (pre-`step-000`)
- **Context**: implementation of the two-document specification begins;
  sessions do not persist, so all workflow state must live in versioned
  files, and the operator gates every step.
- **Decision**: adopt the workflow encoded in `CLAUDE.md` rules 1–10:
  read-only specifications with a decision-before-amendment channel;
  one operator-gated step in progress repository-wide; per-track memory
  — three tracks (root `step-NNN`, steamcmd `step-sc-NNN`,
  project-zomboid `step-pz-NNN`), each owning its `PLAN.md` and
  `DECISIONS.md`, cross-track order expressed only as named
  dependencies; annotated `step-*` tags marking approved states; small
  prefixed commits carrying their documentation; secrets never in the
  repository; English files; a persistence budget. Tooling templates
  from `.claude/spec-work/handoff/assets/` are adopted selectively at
  `step-000` (per-adoption entries to follow).
- **Alternatives considered**: a single global plan and log (rejected:
  every session would load every track's context, against rule 3's
  economy); per-track numbering without track prefixes (rejected:
  ambiguous tags and commit subjects); transcript-based continuity
  (rejected outright: transcripts are not versioned, reviewable memory).
- **Approved by**: operator (bootstrap prompt,
  `.claude/spec-work/handoff/PROMPT.md`).
