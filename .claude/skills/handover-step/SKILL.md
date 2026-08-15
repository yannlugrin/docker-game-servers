---
name: handover-step
description: Pre-test handover sequence — run when the current step's
  implementation is complete and ready for operator testing, or when the
  operator asks for the handover. Checks, staleness sweep, review, then
  hand the step to the operator.
---

# handover-step

**When to use.** When the step is implemented and ready for the
operator's manual test, or when they ask for the handover. The
post-approval close is `/approve-step`, not this.

**Resolve the active track first.** `CLAUDE.md`'s Track map and Current
state pointer name the track being handed over, and with it the plan,
the decision log and the step-identifier prefix used in commit subjects
and tag names (`step-NNN`, `step-sc-NNN`, `step-pz-NNN`).

Hand the current step over for operator testing. In order:

1. **Checks green:** run `just verify` (the whole-tree `just check`,
   then `just test`); fix until it passes. If the step added artifacts
   the harness should cover, confirm it actually covers them — a check
   that never ran is not green.
2. **Staleness sweep (the same-commit rule):** update in the same
   commit(s) as the work everything the step made stale — the track
   plan's step status (to `awaiting test`) and any renumber references,
   `CLAUDE.md`'s Current state pointer and its pointers section,
   `README.md`'s file map, `docs/` deliverables, decision-log entries,
   and any `.claude/docs/` lesson worth keeping for future sessions.
3. **Review:** run the `step-reviewer` agent over the step's diff
   (last `step-*` tag → HEAD). The diff shows committed work only, so
   the step's work and the sweep must be in commits before it runs.
   It may run on your own model — a cold context is what this review
   buys, and the model-diversity rule is the milestone passes' alone
   (D-011). Address or explicitly rebut each finding before handover.
4. **Tree clean:** everything above — the step's work, the sweep, the
   review fixes — is already in small, coherent commits whose subjects
   carry the step id (committed as the work happened, not batched
   here); `git status` shows nothing pending. No catch-all closing
   commit. Never push.
5. **Handover message:** (a) short summary of what the step did;
   (b) precise manual test instructions — exact commands and what the
   operator should observe, including cost and cleanup if the test
   crosses the action boundary; (c) state that you are waiting for
   the operator's verdict. Do not begin the next step.
