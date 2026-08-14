# Review 012 — handoff lens

- **Lens:** handoff prompt (phase 7), round 3
- **Model:** claude-fable-5 (session model)
- **Isolation:** worktree, fresh context
- **Commit reviewed:** 152393fe99286be4592b921bd8729c19ecc594e0
- **Documents given:** SPECIFICATIONS.md, steamcmd/SPECIFICATIONS.md,
  project-zomboid/SPECIFICATIONS.md, .claude/spec-work/handoff/PROMPT.md,
  .claude/spec-work/handoff/assets/ (nine templates),
  .claude/refs/image-contract.md (context only), .claude/settings.json.
  Context block carried the authoritative repository-state statement and
  noted two prior triaged rounds.

---

The checkout was verified at the expected HEAD (`152393fe99286be4592b921bd8729c19ecc594e0`) before reading. All files were read in full: the three specification documents, `PROMPT.md`, the nine asset templates, `.claude/settings.json`, and `.claude/refs/image-contract.md`.

---

# Handoff Prompt Review — Round 3

**Cross-reference check:** every `root §N`/`§N` citation in the prompt and every rule-number citation in the asset templates was resolved against the specification documents and the prompt's own numbering. All resolve; the "eight files" count in the first task is arithmetically correct (3 plans + 3 logs + `CLAUDE.md` + `README.md`); the asset directory contains exactly the four skills and five agents rule 3 names.

## 1. Summary-back — the implementer's first session, as I read it

A fresh Claude Code session is pointed at `PROMPT.md`. It reads the three specifications in full, then, without writing any implementation code: (1) derives three track plans — root, steamcmd, project-zomboid — with the root track opening on three pre-named foundation steps (`step-000` harness on pre-commit + just, `step-001` permission baseline extending the committed `settings.json`, `step-002` workflow tooling instantiated from the assets), cheap-first ordering, milestone grouping, external prerequisites (GitHub repo/remote/first-push authorization, GHCR namespace, per-package visibility flips, conditional Docker Hub credential) each tied to the step that first needs it, and a closing open-questions section; (2) initialises the three decision logs, the root one recording workflow adoption; (3) writes one `CLAUDE.md` (~160 lines, rules restated keeping the prompt's numbering, rule 9's boundary enumeration carried whole, track map, `Current state` section, session routine with the pre-`/resume-step` fallback, and the assets-directory block); (4) writes a descriptive `README.md` with a "For reviewers" frame. It commits all eight files as one `meta:` commit, spawns a cold, inline-prompted, read-only subagent that reads only the specifications plus the eight files (told that `CLAUDE.md`'s assets pointer is out of bounds), triages its findings, and presents triage plus plans. Implementation begins only on plan approval. This matches the intended bootstrap as far as I can reconstruct it; I found no step a cold session could not execute.

## 2. Findings

**F1 — important — PROMPT.md rule 3 (monorepo instantiation instruction) vs `assets/approve-step.md` steps 2 and 4.** The prompt directs that the governance placeholders be filled "with the instruction to resolve the active track at invocation — from `CLAUDE.md`'s track map and its `Current state` pointer." But `approve-step` advances `Current state` to the *next* step in its close commit (step 2) before its step 4 fires the milestone rituals — the state review and the memory compaction, the two passes the prompt works hardest to guarantee are never improvised. At a cross-track milestone boundary (close the steamcmd milestone, next step is `step-pz-…` — the expected shape of this plan), a template instantiated per the letter of that instruction resolves the *wrong track*: `optimize-memory`'s precondition then fails loudly (its `{{PLAN}}` shows no done last step), but `state-reviewer` has no such guard and would quietly review the wrong track's (empty) done set — a ritual that runs, reports, and proves nothing about the milestone just closed. Direction: have the prompt key milestone-close invocations to the track of the step just closed (or have `approve-step` pass the track explicitly), rather than the already-advanced pointer.

**F2 — minor — PROMPT.md rule 2 and step-002 vs rule 3 and rule 11.** Step-002's text mandates the `.claude/rules/` loading probe as one of "the mechanisms this step introduces" — but step-002 introduces skills and agents, not necessarily any rules file, and rule 3 conditions that probe on "*before relying on* that mechanism." As written, an implementer adopting no path-scoped rules must still build and run a probe for a mechanism with no consumer — exactly the build-ahead-of-need shape rule 11 forbids. Direction: condition the step-002 rules probe on a rules file actually being adopted, or state explicitly that the probe is deliberately anticipatory.

**F3 — minor — PROMPT.md rule 1, open-facts come-back classifier.** The classifier ("changes … the documented operator surface, a documented limitation or the decision to ship") is followed by an illustrative list — (d), (e), (f), (g), (k), (l). But the pre-committed paths of items (i) ("player count documented as unavailable … a stated limitation") and arguably (m) and (h) also produce documented limitations, and they are absent from the list. Two reasonable implementers diverge: one treats the list as exhaustive and resolves (i)/(m) autonomously; the other applies the classifier and brings them back. The word "illustratively" saves the text from contradiction but not the implementer from the guess. Direction: either extend the list to every item whose pre-committed path documents a limitation, or state that the classifier alone governs and the list is deliberately partial.

**F4 — minor — PROMPT.md, closing triage instruction.** "Triage its findings — accept, reject with reason, or genuinely my call — and present the triage together with the plans" does not say whether *accepted* findings are applied (and committed) before presentation or presented as pending amendments. The operator observably receives either corrected plans plus a triage log, or uncorrected plans plus proposals — a divergence at the very gate that decides whether step-000 starts. One sentence settles it.

**F5 — minor — PROMPT.md rule 3 ("fill every placeholder with this repository's real commands and paths") vs `assets/state-reviewer.md`.** State-reviewer is on the instantiate-up-front list (milestone-close certainty), but at step-002 its `{{ARCHITECTURE_VOCABULARY}}` — which the template itself scopes "once it exists" — and `{{INSPECTION_COMMANDS}}` have no real referents yet: no images, no containers, no components built. "Fill every placeholder" and "instantiate at step-002" cannot both be satisfied literally. Direction: tell the implementer how to seed those two (e.g., from the specification's own component vocabulary, updated under rule 6 as the system materialises) or exempt them from the fill-every rule with a visible marker.

Checks that found nothing: the check families match the stack (Dockerfile, entrypoint language, Actions YAML, prose, JSON/frontmatter — nothing for artifacts the repository lacks, each conditioned on existence); the rule 9 action boundary covers every paid, destructive or shared-state action the specification implies, including the easily-missed transient Steam-browser registration of a default-profile start, GHCR API writes (dev-tag pruning included), and package-visibility flips; the external prerequisites list is complete and invents nothing; the spec-work quarantine is watertight (the sole standing exceptions — this prompt at bootstrap, the assets until adoption completes — are consistently carved out everywhere, including in the cold reviewer's instructions); the operator's standard tools (pre-commit, just) are mandated rather than left to a "mechanism of your choice"; the bootstrap contains no reference to a file, tag or convention that will not exist when needed (the pre-tag `git describe` case and the pre-`/resume-step` interruption window are both explicitly handled); rule 1's amendment-commit rule and rule 6's staleness sweep resolve their own collision explicitly; and the prompt's description of `.claude/refs/image-contract.md` matches the document on disk (it is a platform image contract, treated as information, not requirements — and nothing in it conflicts with the specification in a way that would trap the implementer).

## 3. Questions for the operator

1. Is a full governance track — separate `PLAN.md`, `DECISIONS.md`, `step-sc-NNN` prefix, milestone expectation — intended for steamcmd, whose specification defers wholly to root §4? The prompt mandates the three-track shape, so the bootstrap cold reviewer's proportion criterion cannot propose folding it into the root track even if that would be leaner.
2. The Claude Code behavior claims (2.1.231: inert `allowed-tools`, the `Edit(path)`/`Write(path)` asymmetry, the `autoMemoryEnabled` key) date from a prior probe, and re-probing is only mandated at steps 001/002. Nothing in the bootstrap session appears to *rely* on them — is that your reading too, i.e., is a stale claim harmless until the probes run?
3. Should the cold plan-reviewer also receive `.claude/refs/image-contract.md`? The plans may cite it (rule 3 orders it read before designing the operator interface), and a reviewer that cannot see it must flag every such citation as an unverifiable premise.
4. For F3: which of items (h), (i), (m) do you actually want brought back before amendment?

## 4. Verdict

0 blocking, 1 important (F1), 4 minor — not a quiet round, but close: the single important finding is a wiring defect at the milestone boundary, not a flaw in the prompt's substance.
