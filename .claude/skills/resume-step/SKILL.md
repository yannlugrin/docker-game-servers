---
name: resume-step
description: Post-interruption verification — distrust the transcript, verify
  the claimed state against the repository and the world, then report
  discrepancies and repair options. Verifies and reports only; it never
  repairs. Use it after work ended abnormally (usage limit, crash, reboot,
  killed console) or whenever the operator doubts what the last session
  claims to have done; it runs instead of /orient, whose orientation it
  embeds.
---

# resume-step

**When to use**: after work ended abnormally — a usage limit, a crash, a
reboot, a killed console — or whenever the operator doubts what the last
session claims to have done. Prefer invoking it from a fresh session, which
cannot be tempted to trust the old transcript.

**Track map** (the active track is named by CLAUDE.md's "Current state"):

| Track | Plan | Decisions | Step ids |
|---|---|---|---|
| root | `PLAN.md` | `DECISIONS.md` | `step-NNN` |
| steamcmd | `steamcmd/PLAN.md` | `steamcmd/DECISIONS.md` | `step-sc-NNN` |
| project-zomboid | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` | `step-pz-NNN` |

Work was interrupted or the last session's claims are in doubt. Your job is
to establish what is actually true, then stop.

**Doctrine: the transcript is a claim, not evidence.** What the conversation
— or its summary, or your own memory of it — says was completed is exactly
what an interruption falsifies: the narrative was written before the
interrupt, the state after. Evidence is the repository and the world; every
claim is checked against them.

In order:

1. **Anchor on approved truth.** The last annotated step tag is the last
   operator-approved state:
   `git describe --tags --abbrev=0 --match 'step-*'`
   (before the first tag, the anchor is the repository root).
   `git log` and `git diff` from there to `HEAD`, plus `git status`, are the
   complete evidence of everything since — committed and uncommitted.
2. **Cross-check the memory files.** Read `CLAUDE.md`'s pointers, the active
   track's plan entry and status, and the tail of its decision log, and
   check each claim against the git evidence. They were written by the same
   interrupted session, so a mismatch is a finding, never something to
   reconcile silently — a status of `awaiting test` over a half-delivered
   diff is precisely what you are looking for.
3. **Working-tree forensics.** Examine uncommitted changes for half-written
   work (a file edited where its counterpart was not, a reference to
   something that does not exist yet). Run `make check`: green is cheap
   evidence the tree is at least well-formed; red localizes the
   interruption.
4. **World state, inside the boundary.** The step may have touched things no
   file records — consult the current step's "How to test" and cleanup notes
   in the plan for what it may have half-applied. Free read-only checks:
   `git status`, `docker ps -a`, `docker images`, `docker volume ls`.
   Anything gated by rule 9's boundary (pushes, registry writes, GitHub
   writes, blanket prunes) you request from the operator, never run;
   anything unverifiable from here you report as unverified — an honest gap
   beats a guessed answer.
5. **Report, then stop — two shapes:**
   - **Discrepancies found:** the resume point and its evidence; each
     discrepancy as the claim plus the contradicting evidence; what could
     not be verified; and the repair options — continue the step from the
     verified state, roll back to the last `step-*` tag, or redo the partial
     work — with your recommendation. The repair is the operator's ruling;
     you execute nothing until they choose.
   - **Everything consistent:** deliver `/orient`'s report — current step and
     status, what the in-progress diff contains, what remains — plus one
     line: verification found no discrepancies, and what was checked. Then
     wait for the operator's go.
