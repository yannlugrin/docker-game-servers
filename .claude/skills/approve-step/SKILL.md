---
name: approve-step
description: Post-approval close of the current step — status done, plan
  entry compacted, annotated step tag on the close commit. Use it only when
  the operator has declared the step approved in this exchange, after their
  manual testing and never on inference; the pre-test handover is
  /handover-step, not this.
---

# approve-step

**When to use**: only when the operator has declared the step approved in
this exchange, after their manual testing — never on inference. The pre-test
handover is `/handover-step`.

**Track map** (the active track is named by CLAUDE.md's "Current state"):

| Track | Plan | Decisions | Step ids |
|---|---|---|---|
| root | `PLAN.md` | `DECISIONS.md` | `step-NNN` |
| steamcmd | `steamcmd/PLAN.md` | `steamcmd/DECISIONS.md` | `step-sc-NNN` |
| project-zomboid | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` | `step-pz-NNN` |

Close the approved step. The precondition is the operator's explicit
approval in this exchange; if their message leaves any doubt, ask — never
treat this skill's invocation context as the approval itself.

In order:

1. **Confirm scope:** the step being closed is the one in `awaiting test`;
   its number has been frozen since it entered `in progress`.
2. **Close commit:** in one commit — the plan's step status to `done` and
   the step entry compacted to its outcome (a few lines: what was approved,
   date, tag name; detail stays in git history); `CLAUDE.md`'s "Current
   state" pointed at the next step; anything else the approval made stale.
   Run `make check` in its full form — never a narrowed pass — before
   committing: this commit receives the step tag and is the state every
   later session treats as known-good. Subject: `<step-id>: close —
   approved, status done, entry compacted`.
3. **Annotated tag** named for the step (`step-NNN`, `step-sc-NNN` or
   `step-pz-NNN`) on that commit. Message shape follows the existing tags
   (`git tag -n99 -l 'step-*'`): a title line `<step-id> — <step title>`,
   then `Approved YYYY-MM-DD.` and a short paragraph of the step's notable
   outcomes.
4. **Milestone boundary:** if this was the milestone's last step, do not
   start the next one — suggest the whole-state review (`state-reviewer`)
   and then, once its findings are settled, the memory-compaction pass
   (`optimize-memory`, invoked per track, from a clean context). Both
   passes are required at a milestone boundary, and this step is their
   in-ritual trigger.
5. **Never push.** The next step starts only on the operator's go.
