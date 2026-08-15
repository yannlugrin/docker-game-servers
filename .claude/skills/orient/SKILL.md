---
name: orient
description: Session-start orientation — run before touching anything, at
  the start of a normal session, after /clear, or when the operator asks
  where we are. Establishes the current step, the last approved state and
  the work in progress, then reports and stops.
---

# orient

**When to use.** At the start of a normal session, after `/clear`, or
when the operator asks where we are. After an interruption (a usage
limit, a crash, a killed console), or when the last session's claims are
in doubt, `/resume-step` is the right ritual, not this.

**Read-only.** This ritual reads and reports; it edits nothing, commits
nothing, and runs no command that changes the repository or the world.

**Resolve the active track first.** This is a monorepo: `CLAUDE.md`'s
Track map and its Current state pointer name the active track, and with
it the plan, the decision log, the step-identifier prefix and the
specification set. Read them now, from the files — never from memory of
an earlier session.

Execute the session-start routine from `CLAUDE.md`, in order:

1. Read `CLAUDE.md` in full, then root `PLAN.md` and `DECISIONS.md`,
   then the active track's plan, decision log and `SPECIFICATIONS.md`.
   On a component track the root specification is not another track's
   document: its §3 and §5 are standing reading. Other tracks' files
   load only where the current step names a cross-track dependency.
2. Read the spec sections the current step names.
3. Locate the last approved state — match the step namespace only,
   because other tags exist and are not step tags:
   `git describe --tags --abbrev=0 --match 'step-*'`
   Before the first step tag exists, the range is the whole history.
4. Review the work in progress: `git log` and `git diff` from that tag
   (or from the root commit) to `HEAD`, plus `git status` for
   uncommitted work.
5. Anomaly check: if what you gathered does not add up — a dirty tree
   the step's status does not explain, a plan status the diff
   contradicts, a stale `CLAUDE.md` pointer — do not deliver the
   normal report: report the anomaly and recommend `/resume-step`,
   then stop. This skill detects; it does not diagnose.
6. Report to the operator: current step and status, what the
   in-progress diff contains, and what remains — then stop and wait
   for instructions. Touch nothing before reporting.
