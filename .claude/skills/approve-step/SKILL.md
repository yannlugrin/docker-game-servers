---
name: approve-step
description: Post-approval close of the current step — run only when the
  operator has declared the step approved in this exchange, after their
  manual testing. Sets status done, compacts the entry, and puts the
  annotated step tag on the close commit.
---

# approve-step

**When to use.** Only after the operator has declared the step approved
in this exchange, following their own manual test. The pre-test handover
is `/handover-step`, not this.

Close the approved step. The precondition is the operator's explicit
approval in this exchange; if their message leaves any doubt, ask —
never treat this skill's invocation context as the approval itself.

**Resolve the track of the step being closed**, from `CLAUDE.md`'s Track
map and Current state pointer: its plan, its decision log and its
step-identifier prefix (`step-NNN`, `step-sc-NNN`, `step-pz-NNN`). Name
that track explicitly in step 4 — the pointer will already have moved on
to the next step, and the milestone rituals key on the track of the step
just **closed**, never on the advanced pointer.

In order:

1. **Confirm scope:** the step being closed is the one in `awaiting
   test`; its number has been frozen since it entered `in progress`.
2. **Close commit:** in one commit — the plan's step status to `done`
   and the step entry compacted to its outcome (a few lines: what was
   approved, date, tag name; detail stays in git history);
   `CLAUDE.md`'s Current state pointed at the next step; anything else
   the approval made stale. Run `just check` before committing — the
   whole-tree form, never `just check changed`: this commit receives
   the step tag and is the state every later session treats as
   known-good. Subject: `<step-id>: close — approved, status done,
   entry compacted`.
3. **Annotated tag** named for the step id, on that commit. Message
   shape follows the existing tags (`git tag -n99 -l 'step-*'`): a
   title line `<step-id> — <step title>`, then `Approved YYYY-MM-DD.`
   and a short paragraph of the step's notable outcomes.
4. **Milestone boundary:** if this was the milestone's last step, do
   not start the next one — suggest the whole-state review
   (`state-reviewer`) and then the memory-compaction pass
   (`optimize-memory`), both invoked for the track of the step just
   closed and in that order, so the compaction runs after the review
   has read the uncompacted memory. **Spawn both on a model other than
   the one you are running**, passing the override explicitly at
   invocation: they judge work your model produced, and neither agent
   pins a model — omitting the override does not mean "no opinion", it
   means they inherit yours, which is the one outcome to avoid
   (D-011). If no second model is available, say so when reporting the
   passes rather than presenting them as independent.
5. **Never push.** The next step starts only on the operator's go.
