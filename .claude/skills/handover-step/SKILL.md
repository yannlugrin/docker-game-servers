---
name: handover-step
description: >-
  Pre-test handover sequence — run when the current step's implementation is
  complete and ready for operator testing, or when the operator asks for the
  handover. Checks, staleness sweep, review, then hand the step to the
  operator.
---

# Handover — the pre-test sequence

Frontmatter carries `name` and `description` only, deliberately. What a
skill's other frontmatter keys do and do not buy — and why none of them is
used here — is in `.claude/docs/agents.md` §5. Read it before adding one.

**When to use.** When the step is implemented and ready for the operator's
manual test, or when they ask for the handover. The post-approval close is
`/approve-step`, not this.

**Which documents, and which step id.** "The plan" and "the decision log"
below mean the **active track's**, resolved when this runs — from
`CLAUDE.md`'s track map and its `Current state` pointer. The step id takes
that track's prefix: `step-NNN` on the root track, `step-sc-NNN` on `sc`,
`step-pz-NNN` on `pz`.

Hand the current step over for operator testing. In order:

1. **Checks green:** run `just verify` — the check half (`just check`, the
   whole tree) and the test half (`just test`) both pass; fix until it does.
   If the step added artifacts the harness should cover, confirm it actually
   covers them — a check that never ran is not green, and a check family
   arrives with the first file of its class, in the step that lands it.
2. **Staleness sweep (the same-commit rule):** update in the same commit(s)
   as the work everything the step made stale — the plan's step status (to
   `awaiting test`) and any renumber references, `CLAUDE.md`'s current-step
   pointer and file map, `README.md`'s map, `docs/` deliverables, decision
   entries, and any `.claude/docs/` lesson worth keeping for future
   sessions.
3. **Review:** run the `step-reviewer` agent over the step's diff (last
   `step-*` tag → `HEAD`). The diff shows committed work only, so the step's
   work and the sweep must be in commits before it runs. Address or
   explicitly rebut each finding before handover.

   Two things that make this review silently not happen, both worth one
   command each: an agent or skill **created during this step** is not
   loaded until the session restarts (`.claude/docs/agents.md` §3), and a
   malformed frontmatter agent never loads at all — `just check` catches the
   second, and only a restart catches the first.
4. **Tree clean:** everything above — the step's work, the sweep, the review
   fixes — is already in small, coherent commits with the track-qualified
   step id as subject prefix (committed as the work happened, not batched
   here); `git status` shows nothing pending. No catch-all closing commit.
   **Never push:** the push belongs to `/approve-step`, after the operator
   has approved, and nowhere else.
5. **Handover message:** (a) short summary of what the step did; (b) precise
   manual test instructions — exact commands and what the operator should
   observe, including cost and cleanup if the test crosses the rule-9 action
   boundary; (c) state that you are waiting for the operator's verdict. Do
   not begin the next step.
