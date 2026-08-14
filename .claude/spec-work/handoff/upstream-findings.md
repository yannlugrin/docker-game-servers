# Upstream findings — handoff phase, games-servers-2

Generic fixes applied during phase 7 that are not project-specific:
defects in the template's fixed text or gaps in slot guidance that
would be true of any project. One line each: what was wrong, the fix,
the round that found it. Raw material for the specify skill's doctrine
changelog.

- Template rule 3 offered "a nested `CLAUDE.md` is the fallback" for a
  failed rules-file probe, contradicting its own single-CLAUDE.md
  invariant; fixed to a `.claude/docs/` file with a read-trigger
  (round 010).
- Template rule 1's "nothing else" amendment commit collided with
  rule 6's same-commit staleness sweep for human-facing docs; fixed by
  stating rule 1 wins and documentation follows in later commits
  (round 010).
- The check definition "untracked files included" silently collides
  with `pre-commit run --all-files`, which enumerates tracked files
  only; fixed by stating the observable and the read-only file-list
  form — `pre-commit run --files $(git ls-files --cached --others
  --exclude-standard)` — whenever pre-commit is the hook runner
  (round 011). The initially recorded alternative,
  `git add --intent-to-add`, was rejected by the operator after the
  quiet round: a check must not write to the index as a side effect —
  `-N` flips `??` to ` A` in `git status --porcelain`, the clean-tree
  signal the step rituals read, and lets the next `git commit -a`
  sweep the file into an unrelated commit. The doctrine fix should
  name only the read-only form.
- Step 000's bundled CI workflow is untestable by its own gate and
  contradicts cheap-first ordering; both review models flagged it
  independently; fixed by splitting the CI workflow into its own step
  sequenced at first-push authorization, with the periodic uncached
  run softened to a deferrable "should" (rounds 010 and 011).
- Rule 9's free side references "the documented setup command", which
  does not exist during step 000 — the boundary had a hole at the
  exact moment work starts; fixed by ruling toolchain bootstrap free
  via each tool's canonical channel (user-level, pinned once chosen)
  with system-level installs asked of the operator, and image-build
  downloads free (round 011; operator refined the system-install
  rule).
- The enforcement probes were all pinned to step 001 though skills,
  agent `tools:` frontmatter and rules files only exist from step 002;
  fixed by attaching each probe to the step introducing its mechanism,
  and conditioning the rules-file probe on a rules file actually being
  adopted (rounds 011 and 012). Agent `tools:` frontmatter was absent
  from the probe set entirely despite the templates resting reviewer
  read-only discipline on it (round 011).
- Monorepo shape: `approve-step` advances the `Current state` pointer
  (its step 2) before firing the milestone rituals (its step 4), so
  resolve-at-invocation aims the state review and memory compaction at
  the wrong track at any cross-track milestone boundary — and the
  state reviewer fails silently there; fixed by keying close-ritual
  invocations on the track of the step just closed (round 012). The
  monorepo doctrine section should carry this exception.
- "Fill every placeholder with real commands and paths" cannot be
  satisfied for up-front-instantiated templates whose referents do not
  exist yet (state-reviewer's architecture vocabulary and inspection
  commands in an empty repository); fixed by seeding from the
  specification's own vocabulary, kept current under rule 6
  (round 012).
- The bootstrap triage instruction did not say whether accepted
  findings are applied before presentation; fixed: apply and commit,
  then present corrected plans with the triage (round 012).
- The foundation steps' dense prescriptions (permission classifier,
  probe duties, traps) had no survival path once the prompt is
  consumed at bootstrap — an interruption between plan approval and
  step 000 loses them; fixed by requiring the foundation plan entries
  to carry the prompt's per-step prescriptions in full (round 013).
- The cold-review paragraph claims "what counts as cheap" lives in
  CLAUDE.md, but the CLAUDE.md content list never ordered the cost
  taxonomy in; fixed by adding it to the list (round 013).
- The annotated-tag message shape was defined only in the
  `approve-step` template (instantiated at step 002), so the first two
  closes set the precedent the template then anchors on ("follows the
  existing tags"); fixed by stating the full shape — including the
  template's outcomes paragraph, which rule 6 initially omitted — in
  rule 6 (rounds 013 and 014).
- "Covered like anything else shipped" is undefined for third-party
  binaries no linter can read, inviting invented verification
  machinery; fixed by declaring the pin and recorded version/digest
  the whole coverage obligation (round 014).
- Process: a reviewer worktree served stale git metadata despite the
  context block's warning, producing a confident false finding that
  committed files were untracked (round 010). Mitigation that worked
  in every later round: an authoritative repository-state statement in
  the context block ("at this HEAD, these files are tracked; do not
  derive tracked-status from git"). Worth adding to the spawning
  guidance.
