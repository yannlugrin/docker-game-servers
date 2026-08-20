---
name: approve-step
description: >-
  Post-approval close of the current step — run only when the operator has
  declared the step approved in this exchange, after their manual testing.
  Sets status `done`, compacts the entry to its outcome, puts the annotated
  step tag on the close commit, and attempts the push so the permission gate
  puts the publish decision to the operator.
---

# Approve — the post-approval close

**When to use.** Only after the operator has declared the step approved in
this exchange, following their own manual test. The pre-test handover is
`/handover-step`, not this.

**Which documents, and which step id — and here the usual resolution is
wrong.** "The plan" means the plan of the **track of the step being
closed**, and the step id takes that track's prefix (`step-NNN`,
`step-sc-NNN`, `step-pz-NNN`). Step 3 advances `CLAUDE.md`'s `Current state`
pointer, possibly onto another track, so from step 3 onward the pointer is
no longer the answer: step 5 **names the closed step's track explicitly**
when it spawns its passes. This is the exception that fails silently — a
state reviewer reading the wrong track's plan reports nothing wrong.

Close the approved step. The precondition is the operator's explicit
approval in this exchange; if their message leaves any doubt, ask — never
treat this skill's invocation context as the approval itself.

In order:

1. **Confirm scope:** the step being closed is the one in `awaiting test`;
   its number has been frozen since it entered `in progress`.
2. **Compact the step entry — replace it, do not annotate it.** The shape is
   `.claude/docs/workflow.md` §1 "Plan-step entry shape": the heading marked
   `done`, one outcome bullet, and the tag range where the detail lives.
   Read it and follow it there — it is the only statement of the shape, it is
   what the plans are written against (`PLAN.md` says so in its own header),
   and a copy in this file would be the copy that goes stale. `CLAUDE.md`
   carries no plan conventions and is not the tie-breaker: that section was
   deleted from it at `step-002` and became §1 (D-002).

   What this ritual adds to the shape, because it only matters while
   performing a close: write the outcome bullet as the tag message's opening
   paragraph condensed — step 4 writes that message in the same
   commit-and-tag pass, so the two cannot disagree. And deleting the plan
   text is the point, not a side effect: an approved step's deliverable list
   keeps asserting intentions the step itself changed, in the file every
   session reads at start.

3. **Close commit:** in one commit — that compacted entry with its status
   `done`; `CLAUDE.md`'s `Current state` pointed at the next step **and the
   closed step's paragraph deleted, not demoted**: its outcome is in the
   entry and the tag this same commit writes, a durable fact belongs in
   `.claude/docs/`, an obligation in the plan, an invariant in the decision
   log. A third copy in `CLAUDE.md` is how that section becomes a changelog
   — measured once at 131 lines, a paragraph at a time, each defensible on
   its own. Anything else the approval made stale.

   Run `just verify` before committing — the full scope, never a narrowed
   fast pass: the close commit receives the step tag and is the state every
   later session treats as known-good.

   Subject: `<step id>: close — approved, status done, entry compacted`.
4. **Annotated tag** named by the step id, on that commit. The message shape
   is `.claude/docs/workflow.md` §5 "The harness contract", and
   `git tag -n99 -l 'step-*'` shows the tags already written to it.

5. **Milestone boundary:** if this was the milestone's last step, do not
   start the next one — run the two passes of `.claude/docs/workflow.md` §3
   "Closing a milestone", review first and compaction second, so the
   compaction reads memory the review has already seen uncompacted. §3
   carries the requirements on them; what this ritual adds is the three
   things §3 cannot know:

   - **Which track.** Both passes target the track of the step **just
     closed** — name it explicitly at spawn. The `Current state` pointer has
     already moved at step 3 and may point at another track, and a state
     reviewer reading the wrong track's plan reports nothing wrong.
   - **Who performs them.** `state-reviewer` and `optimize-memory`. Were
     either dropped, `CLAUDE.md`'s not-yet-adopted list is the fallback name;
     were that list gone too, brief a fresh subagent inline from a clean
     context. The passes are required whoever performs them, and this step is
     their in-ritual trigger.
   - **The model override is passed explicitly.** Neither agent pins one, so
     omitting it does not mean "no opinion" — it means they inherit yours,
     which is the one outcome to avoid. If no second model is available, say
     so when reporting rather than presenting the passes as independent. This
     applies to these two passes only: `/handover-step`'s review buys a cold
     context, which any model gives, and may run on yours.

6. **Report, then attempt the push.** Show the step summary and what the
   close commit and tag contain — with `CLAUDE.md`'s line count and its
   change since the last close, so growth is visible at the moment it
   happens and in front of the operator. The budget is D-018's. Over it,
   present **both** remedies and let them rule: what could move out, and
   raising the budget. Never resolve it by compressing something that
   cannot be compressed without loss — the number is a signal, and a gate
   here would make deletion the cheapest way to go green.

   Then run `git push --follow-tags` — `--follow-tags` carries the annotated
   tag with the commit, where a bare `git push` leaves the step tag behind,
   and a tag that exists only locally is invisible to everything reading the
   remote.

   **This is a named exception to rule 9's "never on your own initiative",
   and it does not generalise.** It holds here because the operator has just
   approved the step, the only open question is whether this closed state
   should be published now, and the permission gate answers exactly that
   question at exactly that moment — better than an offer they have to
   remember to answer. It does *not* license attempting any other gated act
   on the grounds that something downstream will catch it: everywhere else
   the guard is a backstop, never a substitute for asking. It rests on the
   push being gated here — a property recorded with this repository's other
   measured permission behaviour in `.claude/docs/permissions.md`,
   established once and re-measured when the harness changes, never
   re-established at each close. If a close ever pushes with no prompt, stop
   and report it: the exception has lost its footing and the ritual goes
   back to asking in prose.

   **A refusal is final.** If the push is declined or denied, say so, leave
   the commit and its tag local, and stop — no retry, no narrower spelling,
   no pushing the branch without the tag. Either way the next step starts
   only on the operator's go.

---

*Editing this file: frontmatter is `name` and `description` only — why is
in `.claude/docs/agents.md` §4 "A skill's frontmatter".*
