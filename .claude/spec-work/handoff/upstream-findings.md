# Upstream findings — handoff phase, games-servers (handoff-3 iteration)

Generic defects found and fixed during this phase — nothing here is
project-specific; each is a candidate fix for the specify skill's
handoff template, its guidance (`handoff.md`), or the asset templates.
One line each: what was wrong → the fix applied here → the round that
found it (reviews 014–016).

## Template fixed text (the prompt)

- "Produce four files, then stop for my review" contradicts the
  section's own closing sequence (commit → cold review → triage →
  present) → opening reworded to "produce … and have them
  cold-reviewed …; only then stop" → round 1 (F3).
- Rule 1's "the two rules otherwise collide with no stated winner"
  parses as an admitted unresolved conflict → reworded to "— stated
  because the two rules would otherwise collide with no winner" →
  round 1 (F4).
- The open-facts latitude split lets "pre-committed path is
  autonomous" collide with the always-escalate list when a
  pre-committed response itself changes a tier, limitation or
  capability → state that the escalation list wins wherever both
  clauses apply → round 2 (F1).
- The `CLAUDE.md`-reaches-subagents probe has no pre-committed
  unfavorable branch (unlike the `.claude/rules/` probe beside it) →
  added: probe fails → agents inline the gated set, logged with the
  single-source cost → round 2 (F3).
- "the first agent you spawn" literally denotes the bootstrap cold
  reviewer, whose context must stay cold → scoped to "the first agent
  you spawn in step 002" → round 2 (F12).
- Nothing verifies the foundation plan entries actually carry the
  prompt's per-step prescriptions, and the cold reviewer is
  structurally barred from reading the prompt → added a second,
  deliberately non-cold transcription-fidelity subagent to the first
  task → round 2 (F5).
- The first task is one large ungated unit while the prompt argues
  elsewhere that no step is exempt from splitting → exemption stated
  explicitly (text output, correction is cheap, the cold review is
  rule 2's self-verification, not a step gate) → round 2 (F6,
  rejected as a change but the silent self-exemption was real).
- The governance frontmatter parse check mandates a bespoke tool
  while rule 11 forbids unexamined bespoke tools → sanctioned
  explicitly as a few-line custom check with its reason (no standard
  tool exists; the guarded files fail silently) → round 2 (F8).
- Step 000's "the check/test/verify harness … built on the tools
  named there" reads against rule 2's never-ahead rule (families for
  Dockerfiles/workflows that do not exist yet) → step 000 scoped to
  the harness skeleton plus families whose artifacts exist at 000 →
  round 2 (F9).
- The static-checks guidance misses that `bash_guard.py` is Python
  whatever the entrypoint language, and its 88-column width exemption
  is a config item → Python named as a standing family with the
  exemption → round 2 (F11).
- The prompt asserts permission-mode names and behavior normatively —
  and *both* attempts at fixing the vocabulary were wrong: round 3's
  reviewer claimed `auto` does not exist, the triage accepted it, and
  a live probe of the installed 2.1.233 then showed `auto` *does*
  exist (with classifier behavior that can deny outright — a third
  case the "fixed" wording erased) while `default` is absent from the
  CLI's choices. The durable fix, applied on operator review: the
  template names **no** modes and asserts **no** mode behavior — the
  mode set and each mode's unmatched-command behavior are step-001
  probe-and-record duties, exactly as the prompt already rules for
  every other measured value → round 3 (F1) + operator review.
- `.claude/refs/` sits inside the check harness's whole-tree scope
  but is read-only with no stated lint-resolution path (the
  bend-don't-edit clause names only the specifications) → refs joins
  the standing path exclusion, with its reason → round 3 (F2).

- Rule 6's multi-track adaptation claimed "`git diff` between two of
  a track's tags is exactly one step's change" — false under
  interleaved tracks on one linear history (a root-track tag pair can
  have a `pz` step between them); the invariant is *the immediately
  preceding `step-*` tag of any track*, which is what rule 3's
  `git describe --match 'step-*'` already computes. Fixed in rule 6,
  the plan-compaction block, and `approve-step.md`'s header →
  operator review.
- The `{{IGNORE_ITEMS}}`-fed `.gitignore` list in step 000 omitted
  `.claude/worktrees/` — the one line the skill's own workspace rule
  mandates (a commit made while a reviewer worktree exists swallows
  its checkout), and an implementer writing `.gitignore` fresh from
  the list would drop it. The fixed text should carry it the way it
  carries `.claude/reviews/` and `CLAUDE.local.md` → operator review.

## Guidance (`handoff.md`)

- Multi-track: the close-ritual track-keying exception ("key on the
  just-closed step's track, not the advanced pointer") has no named
  carrier past bootstrap — the first-task `CLAUDE.md` carry-list and
  the step-002 plan-entry content never mention it → added to both →
  round 1 (F2), extended round 2 (F4).
- `{{HOUSE_TOOLING}}` / `{{BOUNDARY}}` guidance is silent on the
  task-runner gate bypass: a PreToolUse Bash guard sees `just
  release`, never the gated act inside the recipe, so naming a task
  runner needs the companion invariant (no gated act behind a recipe
  name) → invariant added to the prompt → round 2 (F2).

## Asset templates

- `step-reviewer.md` / `state-reviewer.md` assert "a probe confirmed
  `CLAUDE.md` reaches every subagent's context" as settled fact,
  biasing instantiation toward citation → attributed to the earlier
  project, re-probe ordered, inline fallback named → round 2 (F3).
- `approve-step.md` advances the Current-state pointer (step 3)
  before spawning the milestone passes (step 5) with no multi-track
  note — while `optimize-memory.md` carries one; the asset set was
  inconsistent on exactly the hazard the prompt names → close-track
  keying added to header and step 5 → round 2 (F4).
- `optimize-memory.md` is the only writing agent (broadest `tools:`)
  without the action-boundary paragraph the three reviewers carry →
  paragraph added → round 2 (F10).
- `bash_guard.py`'s module docstring asserts mode names and behavior
  in three places → de-normativized to "probe the installed version,
  never take modes from this docstring" (same lesson as the prompt's
  F1 above; the intermediate name-swap fix was itself wrong);
  `--selftest` still green → round 3 (F1) + operator review.

## Process observations

- Worktree isolation twice materialized the reviewer's checkout on a
  different branch (a previous handoff iteration's implementation) —
  both times the context block's stale-checkout guard caught it and
  the reviewer self-corrected. The guard instruction is load-bearing;
  consider also naming the expected *branch* (not only the commit) in
  the context block for repositories with multiple lines.
- A cold reviewer asserted a harness fact from training knowledge
  (the permission-mode list), and the triage accepted and applied it
  without probing the installed version — the "facts are researched,
  not assumed" rule needs to bind triage of *reviewer-asserted
  environment claims* as explicitly as it binds spec drafting: a
  finding that asserts what the harness defines is verified against
  the harness before it is applied.
