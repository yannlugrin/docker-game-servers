---
name: orient
description: >-
  Session-start orientation — run before touching anything, at the start of
  a normal session, after /clear, or when the operator asks where we are.
  Establishes the current step, the last approved state and the work in
  progress, then reports and stops.
---

# Orientation — the session-start ritual

Frontmatter carries `name` and `description` only, deliberately. What a
skill's other frontmatter keys do and do not buy — and why none of them is
used here — is in `.claude/docs/agents.md` §4 "A skill's frontmatter".
Read it before adding one.

**When to use.** At the start of a normal session, after `/clear`, or when
the operator asks where we are. After an interruption (a usage limit, a
crash, a killed console), or when the last session's claims are in doubt,
`/resume-step` is the right ritual, not this.

**Read-only.** This ritual reads and reports; it edits nothing, commits
nothing, and runs no command that changes the repository or the world.

**Which documents.** "The plan", "the decision log" and "the specification"
below mean the **active track's**, resolved when this runs — never one fixed
path. Take the track from `CLAUDE.md`'s track map and its `Current state`
pointer. On a component track the **root specification always applies too**:
a per-image document adds to the root conventions and never replaces them.

Execute the session-start routine from `CLAUDE.md`, in order. It is a
multi-track routine, and this enumeration matches it — reading less than the
routine is skipping reading:

1. Read `CLAUDE.md` in full, the **root** `PLAN.md` and the **root**
   `DECISIONS.md`. These three are standing reading on every track.
2. Read the active track's plan, log and specification, plus the
   specification sections the current step names. The **root specification
   is never "another track's document"**: root §3 and §5 above all are
   standing reading on any track. Another track's plan, log or specification
   loads only when the current step names a cross-track dependency.
3. Locate the last approved state — match the step namespace only, never the
   latest tag of any kind:
   `git describe --tags --abbrev=0 --match 'step-*'`
   Before the first step tag exists, the range is the whole history.
4. Review the work in progress: `git log` and `git diff` from that tag (or
   the repository root) to `HEAD`, plus `git status` for uncommitted work.
   That range is exactly the work in progress, and nothing else is.
5. Anomaly check: if what you gathered does not add up — a dirty tree the
   step's status does not explain, a plan status the diff contradicts, a
   stale `CLAUDE.md` pointer — do not deliver the normal report: report the
   anomaly and recommend `/resume-step`, then stop. This skill detects; it
   does not diagnose.
6. Report to the operator: current step and status, what the in-progress
   diff contains, and what remains — then stop and wait for instructions.
   Touch nothing before reporting.
