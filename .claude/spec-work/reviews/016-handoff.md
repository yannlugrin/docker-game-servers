# Review 016 — handoff lens (round 3, confirmation)

- **Lens:** handoff prompt (phase 7), round 3
- **Model:** claude-fable-5 (session model, inherited)
- **Isolation:** worktree, cold context
- **Commit reviewed:** d2e7fa7 (review 015 triage applied)
- **Documents given:** SPECIFICATIONS.md, project-zomboid/SPECIFICATIONS.md, .claude/spec-work/handoff/PROMPT.md, .claude/spec-work/handoff/assets/ (10 templates), .claude/refs/image-contract.md named as operator reference

[Archivist note: the worktree again materialized at 596f91b (the previous
handoff iteration's implementation); the reviewer detached at d2e7fa7
before reading, per the context-block guard. Report is against d2e7fa7.]

---

The checkout initially sat at `596f91b` (branch `handoff-3`, carrying unrelated later content); I detached the worktree at the expected `d2e7fa7` before reading anything. All reading below is from that commit.

---

# Review report — handoff prompt (round on `d2e7fa7`)

**Cross-reference check:** every section reference in `PROMPT.md` resolves against the two specification documents — root §2.6/§2.8/§2.9, §3.1, §4, §5.4/§5.5, §6, §7, §8, §9; PZ §2's lettered items (a)–(o) all exist, and the prompt's characterizations of the must-not-ship combination (l)+(c), the (k)+(l) degraded-healthcheck ship decision, (g)'s impossible branch, and the (d)/(e)/(f)/(i) tier-changing resolutions each match the spec's text. The asset inventory the prompt names (four skills, five agents, one hook) matches the ten files on disk; `bash_guard.py` is executable; `.claude/settings.json` contains the auto-memory-off key the prompt claims; `LICENSE` is MIT; `.claude/refs/image-contract.md` exists. One loose citation is Finding 3.

## 1. Summary-back

The prompt bootstraps an unsupervised-but-gated AI implementation of a two-document specification: a public repo of GHCR-published game-server images (steamcmd builder + Project Zomboid B42 runtime), organized as two tracks (root: harness, builder, CI, repo-wide docs; `pz`: the game image and its README). Eleven permanent ground rules — read-only specs with a logged amendment channel and an escalation list for the spec's open facts, one operator-gated step at a time with self-verification behind `pre-commit`/`just` entry points, file-based memory (per-track plans and decision logs, one small `CLAUDE.md`), per-track decision logging, no secrets, small track-prefixed commits with step tags and a push-attempt-at-close exception, an enumerated action boundary (registry/GitHub writes and unscoped destruction gated; local dev loop and named Steam/GitHub reads free), a persistence budget, and a proportionality rule.

First session, as I read it: (1) read the prompt and both specifications in full; (2) write six files — root `PLAN.md` (foundation steps 000–003 carried with the prompt's prescriptions in full, then builder/CI/docs steps), `project-zomboid/PLAN.md` (every open fact (a)–(o) and prose-level "measure at implementation" items mapped step by step), both `DECISIONS.md` initialized (root D-001 = workflow adoption), `CLAUDE.md` (~180 lines, rules restated keeping the numbering, track map, `Current state`, assets block), `README.md` with the For-reviewers frame; (3) commit them in one `meta:` commit; (4) spawn a cold read-only subagent auditing the plans against the specs on seven criteria, plus a second, deliberately non-cold subagent checking foundation-step transcription fidelity against the prompt; (5) triage, apply and commit accepted findings, present the triage and corrected plans, and stop. `step-000` begins only on approval. No implementation, no push, no registry contact in this session.

## 2. Findings

**F1 — minor — Ground rule 2 / step-001 (and `bash_guard.py` docstring): permission mode named "auto" that the harness does not define.**
Evidence: "under `auto` or `bypassPermissions` nothing prompts by itself and the guard's asks are the only gate left" (rule 2's settings discussion and step-001; the guard docstring's "Mind the permission mode" repeats it). Claude Code's documented `permissions.defaultMode` values are `default`, `plan`, `acceptEdits`, `bypassPermissions` (and `dontAsk` in recent versions) — none is spelled `auto`, and the nearest colloquial reading, accept-edits ("auto-accept"), does *not* stop Bash prompts, so the sentence's behavioral claim would be wrong under that reading. Step-001 must commit a real value and "name the permission mode you expect me to work in", so the implementer is left mapping "auto" to a real mode by guess. Mitigations already present: the prompt mandates probing the mode's actual behavior and says "assume nothing here, including from this prompt", and the whole baseline is operator-reviewed. Direction: replace "auto" with the actual mode name(s) intended, or mark it explicitly as a stand-in to be resolved by the step-001 probe.

**F2 — minor — Ground rule 2 vs. rule 3: `.claude/refs/` is inside the check harness's scope but outside its resolution rules.**
Evidence: rule 2 scopes *check* to "the whole working tree … with one standing exception … everything under `.claude/spec-work/`", and its read-only carve-out names only the specifications ("the specification documents are read-only under rule 1, so the lint bends to them and never the reverse"). Rule 3 makes `.claude/refs/` equally read-only ("you never edit, extend, annotate … no sweep of yours ever touches it"), yet a Markdown-lint finding in `image-contract.md` has no stated path: the file cannot be edited, and the only escape ("excluding a document from a rule is a logged decision") is written for governance documents. Two reasonable implementations diverge observably — one bends the lint config to the ref, one logs an exclusion, one leaves check red. Direction: extend the bend-don't-edit clause (or the standing path exclusion) to `.claude/refs/`.

**F3 — minor — External prerequisites: the public-repository instruction cites two sections that do not support it.**
Evidence: "the GitHub repository (created **public**: root §2.6, §2.8 and §7 all assume it — free GHCR hosting, anonymous pulls, and the idle-schedule behavior §8 defends against)". Root §2.6 and §7 are about *package/image* visibility — §2.6 explicitly says a workflow-pushed package stays private until manually flipped, public repo or not — so of the three citations only §2.8 (idle-schedule disabling "in a public repository") actually concerns repository visibility. The instruction itself is right (the project is framed as a public product, root §1), and the prompt separately lists the per-package flip, so no wrong action follows; the citation is what's loose. Direction: rest the create-public instruction on §2.8 plus root §1's public-product framing, and leave §2.6/§7 attached to the flip and namespace items where they already correctly appear.

Nothing else rose to a finding. Specifically checked and found sound: the check-family list matches the stack (Dockerfiles, workflow validation, entrypoint-language lint left open exactly as the spec leaves the language open, Python for the vendored guard, pinned third-party clients including PZ §4's SQLite client, governance well-formedness with its explicitly sanctioned few-line custom frontmatter check) and the never-ahead rule keeps every family tied to its first artifact; the action boundary covers every paid/destructive/shared-state act the spec implies (registry pushes including dev tags, GitHub writes, registry deletion, unscoped prunes, git history/working tree), and the deliberately-freed outward write (transient Steam master-server registration of a local test server) is reasoned; the rule-1 amendment channel and the escalation list track the spec's open-fact pre-commitments exactly; rule 1's amendment-commit rule states its own winner over rule 6's staleness sweep; every bootstrap reference resolves at bootstrap (no-tag re-orientation, pre-`/resume-step` interim routine, no-remote push handling in `approve-step`, assets present and executable, auto-memory key present on disk); the templates' adoption guidance (governance placeholders resolve-at-invocation, close rituals keying on the just-closed track, model-diversity confined to the milestone passes, `.claude/reviews/` gitignore assumption) is consistent with what the prompt says about them, and the prompt pre-orders the gitignore entry the templates assume; no instruction sends any session into `.claude/spec-work/` beyond the prompt and its assets, including both bootstrap reviewers; and on proportion, the prompt polices itself — the one custom check is justified and bounded, a regretted over-built checker is named and forbidden, standard tools are mandated by name, and the one deliberately large ungated unit (the six-file first task) states its reason and is immediately operator-gated.

## 3. Questions for the operator

1. Which real `permissions.defaultMode` value does "auto" stand for in rule 2/step-001 (F1) — and is the intended working mode for this project `default`, `acceptEdits`, or something looser?
2. For F2: should `.claude/refs/` be excluded from the check harness like `.claude/spec-work/`, or linted with the config bent to it like the specifications?
3. Confirm the *git repository* (not only the GHCR packages) is meant to be created public at bootstrap — the specification states it only via root §1's framing and §2.8's public-repo behavior, and a private-repo-with-public-packages reading is otherwise not excluded.
4. Rule 9's Steam exceptions name steamcmd downloads and metadata/buildid queries; a locally started server downloading *workshop mods* (PZ §7) is a third network shape, arguably covered by "the development loop is free end to end" — is that the intended reading, so a mod-configured local test run needs no per-exchange authorization?
5. Spec-side (not a finding here): root §2.8 states scheduled-workflow disabling at "roughly 60 days without repository activity" — worth re-verifying at implementation that GitHub's current threshold and notification behavior still match, since §8's interim staleness check is calibrated to it.

## 4. Verdict

0 blocking, 0 important, 3 minor — a quiet round on substance: the prompt is internally consistent, faithful to the specification, executable cold from bootstrap, and actively guards against overbuilding; the minors are vocabulary and scope-edge polish.
EOF
git add .claude/spec-work/reviews/016-handoff.md && git commit -q -m "handoff: archive review 016 (handoff lens, round 3, quiet on substance)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" && git log --oneline -1