---
name: handover-step
description: Pre-test handover sequence — checks green, staleness sweep,
  reviewer pass, then hand the step to the operator for testing. Use it when
  the current step's implementation is complete and ready for operator
  testing, or when the operator asks for the handover; the post-approval
  close is /approve-step, not this.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  # Subagent invocation — without it, step 3's review silently never runs.
  # Named `Agent` in this harness; `Task` in others, so both are listed.
  - Agent
  - Task
  - Bash(make verify:*)
  - Bash(make check:*)
  - Bash(make test:*)
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git describe:*)
  - Bash(git add:*)
  - Bash(git commit:*)
---

# handover-step

**When to use**: the current step's implementation is complete and ready for
the operator's manual test, or the operator asks for the handover. After
their approval, the closing ritual is `/approve-step`.

**Track map** (the active track is named by CLAUDE.md's "Current state"):

| Track | Plan | Decisions | Step ids |
|---|---|---|---|
| root | `PLAN.md` | `DECISIONS.md` | `step-NNN` |
| steamcmd | `steamcmd/PLAN.md` | `steamcmd/DECISIONS.md` | `step-sc-NNN` |
| project-zomboid | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` | `step-pz-NNN` |

Hand the current step over for operator testing. In order:

1. **Checks green:** run `make verify` (the check and the test halves both
   pass); fix until it does. If the step added artifacts the harness should
   cover, confirm it actually covers them — a check that never ran is not
   green, and a new language or artifact type needs its own hook in
   `.pre-commit-config.yaml`.
2. **Staleness sweep (the same-commit rule):** update in the same commit(s)
   as the work everything the step made stale — the plan's step status (to
   `awaiting test`) and any renumber references, `CLAUDE.md`'s current-step
   pointer, the root `README.md` file map, `docs/` deliverables, decision
   entries, and any `.claude/docs/` insight worth keeping for future
   sessions.
3. **Review:** run the `step-reviewer` agent over the step's diff (last
   `step-*` tag → HEAD; before the first tag, the whole history). The diff
   shows committed work only, so the step's work and the sweep must be in
   commits before it runs. Address or explicitly rebut each finding before
   handover.
4. **Tree clean:** everything above — the step's work, the sweep, the review
   fixes — is already in small, coherent commits whose subjects carry the
   step id (`step-NNN`, `step-sc-NNN` or `step-pz-NNN`), committed as the
   work happened rather than batched here; `git status` shows nothing
   pending. No catch-all closing commit. Never push.
5. **Handover message:** (a) short summary of what the step did; (b) precise
   manual test instructions — exact commands and what the operator should
   observe, including cost and cleanup if the test crosses rule 9's
   boundary; (c) state that you are waiting for the operator's verdict. Do
   not begin the next step.
