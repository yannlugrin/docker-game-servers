---
name: orient
description: Session-start orientation — run before touching anything.
  Establishes the current step, the last approved state and the work in
  progress, then reports and stops. Use it at the start of a normal session,
  after /clear, or when the operator asks where we are; after an interruption
  (usage limit, crash, killed console) or when the last session's claims are
  in doubt, /resume-step is the right ritual instead.
---

# orient

**When to use**: at the start of a normal session, after `/clear`, or when
the operator asks where we are. After an interruption, or when the last
session's claims are in doubt, use `/resume-step` — it embeds this
orientation and verifies on top of it.

**Track map** (the active track is named by CLAUDE.md's "Current state"):

| Track | Plan | Decisions | Step ids |
|---|---|---|---|
| root | `PLAN.md` | `DECISIONS.md` | `step-NNN` |
| steamcmd | `steamcmd/PLAN.md` | `steamcmd/DECISIONS.md` | `step-sc-NNN` |
| project-zomboid | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` | `step-pz-NNN` |

Execute the session-start routine from CLAUDE.md, in order:

1. Read `CLAUDE.md` in full, then the root `PLAN.md` and `DECISIONS.md`;
   on an image track, also that track's plan and decision log. The
   "Current state" pointer names the track and the current step.
2. Read the spec sections the current step lists: root `SPECIFICATIONS.md`
   always (§3 and §5 are standing reading for any image-track step), plus
   `project-zomboid/SPECIFICATIONS.md` on that track.
3. Locate the last approved state — match the step namespace only:
   `git describe --tags --abbrev=0 --match 'step-*'`
   Before the first step tag exists, the range is the whole history.
4. Review the work in progress: `git log` and `git diff` from that tag
   (or the repository root) to `HEAD`, plus `git status` for uncommitted
   work.
5. Anomaly check: if what you gathered does not add up — a dirty tree the
   step's status does not explain, a plan status the diff contradicts, a
   stale `CLAUDE.md` pointer — do not deliver the normal report: report the
   anomaly and recommend `/resume-step`, then stop. This skill detects; it
   does not diagnose.
6. Report to the operator: current step and status, what the in-progress
   diff contains, and what remains — then stop and wait for instructions.
   Touch nothing before reporting.
