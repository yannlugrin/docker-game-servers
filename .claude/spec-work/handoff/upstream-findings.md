# Upstream findings — handoff phase (reviews 014–018)

Generic findings from this repository's handoff review rounds: defects or
gaps in the specify skill's templates and fixed prompt text, nothing
project-specific. **All were ported upstream on 2026-08-13** (skill
revision reviewed against this repository's handoff); they are recorded
here so a later session does not report them a second time. Format: round
and finding — what was wrong — where the upstream fix landed.

- 014-F1 — `approve-step`'s milestone step named agents that could end up
  neither adopted nor listed, with no terminal fallback — ported: fallback
  rewiring in the template header and step 4. **[ported]**
- 014-F2 — the adaptation instruction understated what the templates
  assume (single plan/log/spec, one id namespace) — ported: the governance
  placeholder set (`{{PLAN}}`, `{{DECISIONS}}`, `{{SPEC}}`, `{{STEP_ID}}`)
  and its glossary in `handoff.md`. **[ported]**
- 014-F3 — `.claude/settings.json` sat outside every standing check
  family while being the enforcement mechanism itself — ported: rule 2's
  governance-well-formedness fixed text. **[ported]**
- 015-F1 — open-fact resolution latitude was ambiguous (autonomous vs
  approval round-trips) — ported: the `{{OPEN_FACTS}}` slot with the
  mandatory latitude split. **[ported]**
- 015-F2 — the boundary's free side was under-enumerated (a dev loop is
  local and full of writes) — ported: `{{BOUNDARY}}`'s "enumerate the free
  side too" rule. **[ported]**
- 015-F3 — operator-supplied references lived in the directory the memory
  sweep owns — ported: `.claude/refs/` and the `{{REFERENCES}}` slot.
  **[ported]**
- 015-F5 / 017-F4 — check families hardened stack choices and spec
  "should"s into facts, and shipped third-party tools lacked a family —
  ported: `{{STATIC_CHECKS}}`'s three rules. **[ported]**
- 015-F7 — the bootstrap plan reviewer judged conventions defined only in
  documents it must not read — ported: the closing block names `CLAUDE.md`
  as the conventions source and fences the assets pointer. **[ported]**
- 015-F10 — `{{NEVER_RUN}}` did not say which set it takes — ported:
  reviewer templates take rule 9's entire gated set, with the
  cannot-ask-mid-run reasoning. **[ported]**
- 016-F1 — blanket prune was freed by a reasoning that only covered
  project-local resources — ported: `{{BOUNDARY}}`'s blast-radius rule
  (destructive-local splits on blast radius, not the verb). **[ported]**
- 016-F4 — the plan-step entry shape and boundary-cost rule existed only
  in the first-task text the later sessions never reread — ported:
  first-task item 3 requires `CLAUDE.md` to carry them. **[ported]**
- 016-F5 — `optimize-memory` stated the 200-line cap and the
  never-compress-the-boundary rule as jointly unsatisfiable — ported: the
  yield clause in the template. **[ported]**
- 017-F1 — `CLAUDE.md`'s `/resume-step` instruction pointed at a command
  that does not exist until step 000 — ported: the pre-instantiation
  fallback in first-task item 3. **[ported]**
- 017-F2 — step 000's breadth contradicted the small-step rule the prompt
  itself states — ported: the breadth is blessed as a deliberate composite
  with its gate named. **[ported]**
- 017-F5 — the state-destroying-git ask tier was a list that omitted
  history rewriting and `git clean` — ported: stated as a classifier, with
  the bare-`git commit`-admits-`--amend` trap named. **[ported]**
- (architecture) — the per-track memory shape this repository needed
  (root + per-component plans, logs, qualified step ids, one step in
  progress repo-wide, root spec as standing reading) — ported: the
  "Monorepo and multi-track projects" section of `handoff.md`. **[ported]**
- 018-F1 — the parameterized templates cited "the glossary in
  `handoff.md`", a file that ships with the skill and never with the
  repository, so the pointer dangled for every implementer — ported:
  each template header now states its placeholders' meaning inline,
  named to the subset that file uses (seven files, `resume-step.md`
  included). **[ported 2026-08-13]**

Reviews 014–017 are archived under `.claude/spec-work/reviews/`; the two
false git-state findings (015-F6-premise, 016-F2/F3) that motivated the
worktree-state spawning guidance are noted in their archive headers.
