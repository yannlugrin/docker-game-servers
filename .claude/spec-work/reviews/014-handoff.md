# Review 014 — handoff lens

- **Lens:** handoff prompt (phase 7)
- **Model:** claude-fable-5 (session model, inherited)
- **Isolation:** worktree, cold context
- **Commit reviewed:** 31ee217
- **Documents given:** SPECIFICATIONS.md, project-zomboid/SPECIFICATIONS.md, .claude/spec-work/handoff/PROMPT.md, .claude/spec-work/handoff/assets/ (10 templates)

---

All references verified. Here is my report.

---

# Review report — handoff prompt (`.claude/spec-work/handoff/PROMPT.md` + assets), round at HEAD 31ee2175

**Cross-reference check:** every `§N`/`root §N`/`PZ §N` reference in the prompt resolves to an existing section of the two specification documents (bare `§2.8` and `§8` are elliptical continuations of an adjacent `root §…` and resolve correctly); the asset inventory the prompt claims (four skills, five agents, one hook) matches the files on disk exactly.

## 1. Summary-back

The prompt bootstraps an unsupervised AI implementer for a public GHCR repository of game-server Docker images (steamcmd builder + per-game runtimes, first: Project Zomboid B42), governed by two read-only specification documents and organised as two tracks (root, `pz`). In its first session the implementer would: read both specs in full; write six files — root and PZ `PLAN.md` (covering every spec section, mapping every open fact to the step that settles it, listing external prerequisites and open questions), root and PZ `DECISIONS.md`, a ~180-line `CLAUDE.md` restating the eleven ground rules with their numbering plus track map, "Current state", session routine and a temporary assets-directory block, and a descriptive `README.md` with a "For reviewers" frame; commit all six in one `meta:` commit; spawn a cold, read-only, inline-prompted subagent to audit the plans against the specs on seven criteria; triage and commit accepted findings; present the triage and stop. Implementation then proceeds one operator-gated step at a time: a four-step root-track foundation milestone (000 harness on `pre-commit`+`just`, 001 permission baseline built around the supplied `bash_guard.py`, 002 workflow tooling instantiated from the asset templates, 003 the same harness on GitHub Actions, gated by a real run), then builder, PZ image, CI automation and documentation steps, with spec amendments flowing only through a logged decision channel.

## 2. Findings

**F1 — important — Ground rule 1 (open facts) vs PZ §2 items (k) and (l).** The escalation list glosses the spec's conditions wrongly: the prompt writes "PZ item (l) resolving unfavorably (no loopback RCON bind — the must-not-ship combination)" and "PZ item (k) resolving unfavorably (a documented-degraded default healthcheck is a ship decision)". Per PZ §2, must-not-ship requires (l) *and* (c) unfavorable together (loopback unavailable *and* console unusable — l alone with a working console ships with a degraded niche profile), and the documented-degraded default healthcheck arises only from (k) *and* (l) together while the console works — (k) alone is absorbed by §6's fallback order. The operative instruction (always escalate to the operator) is safe, but rule 1 is destined for concise restatement in `CLAUDE.md` and the plans' open-fact mapping, where these compressed-wrong parentheticals become the standing text a later session acts on and presents to the operator ("we must not ship") in place of the spec's actual conditions. Direction: make the parentheticals name the combinations exactly as the spec does, or strip the rationale glosses and leave the bare escalation triggers.

**F2 — important — Ground rule 3 (governance placeholder semantics) has no named carrier past bootstrap.** The prompt calls the close-ritual track-keying exception "the one that fails silently" (resolve-at-invocation would aim the milestone state review and memory compaction at the wrong track after the pointer advances), yet: the prompt is consumed once at bootstrap; the `approve-step` template's instantiation notes never mention naming the just-closed track (its step 5 is written single-track); the first-task enumeration of what `CLAUDE.md` must carry (track map, Current state, routine, plan-entry shape, boundary rule, assets block) does not name the governance-set semantics; and the step-002 plan entry is required to carry only "the instantiation list". The whole exception thus survives only if the concise, non-verbatim `CLAUDE.md` restatement of rule 3 happens to keep it. Direction: add the resolve-at-invocation rule and its close-ritual exception to the explicit list of things `CLAUDE.md` (or the step-002 plan entry) must carry, and/or note it in `approve-step`'s instantiation header.

**F3 — minor — First-task opening contradicts the closing sequence.** "Produce six files, then stop for my review" (line 563) reads as stop-after-writing, while the section's tail orders: commit the six files, run the cold review, apply and commit accepted findings, *then* present and stop. A literal reader of the first sentence halts one commit and one review too early. Direction: reword the opening to "Produce six files, have them cold-reviewed, then stop for my review" or similar.

**F4 — minor — Rule 1's collision clause reads as an unresolved conflict.** "for amendment commits, this rule wins over rule 6's same-commit staleness sweep, and the two rules otherwise collide with no stated winner" — intended as justification (the winner is stated *because* otherwise they would collide), but a cold reader can parse "otherwise" as "in all other cases", and go hunting for a rule conflict the prompt admits but does not resolve. Direction: "…this rule wins over rule 6's same-commit staleness sweep — stated because the two rules would otherwise collide."

**F5 — minor — Track ownership of per-image documentation is ambiguous.** The two-track intro assigns "shared documentation (root §9)" to the root track, but root §9 includes the per-image READMEs — for PZ, part of "the Project Zomboid image" the `pz` track owns. The first-task deliverables list ("the per-image READMEs… as steps in their own right") does not say which plan carries them. Two reasonable implementations diverge in which track's plan, step namespace and decision log own the PZ README — observable in step ids, log placement and the cold review's coverage mapping. Direction: qualify "shared" (repository README + contributor guide root-track; per-image README follows its image's track), or state that the split is the implementer's call to log.

**F6 — minor — Step 003's fresh-setup proof rides a schedule that will not exist for many steps.** Step 003 says the proof "may ride a scheduled job the specification already requires (root §8's refresh and update detection) rather than becoming a second scheduled workflow of its own" — but at step 003 no image exists and no §8 job can; those workflows arrive far later in the plan. The interim is unstated: whether per-run fresh-runner setup already satisfies "keeps a way of proving a fresh setup still works", or a temporary schedule is expected until §8's job exists, is a guess two implementations would make differently (observable: whether a scheduled workflow exists at foundation close). Direction: one clause saying what suffices until the §8 jobs exist.

Nothing in the prompt sends the implementer into `.claude/spec-work/` beyond the prompt and `handoff/assets/`; the check families match the stack (Dockerfiles, workflows, Markdown, governance files, the Python hook — the family-with-first-file rule correctly defers workflow validation to 003); the action boundary covers every paid/destructive/shared-state act the spec implies (registry pushes and deletions, GitHub writes, unscoped Docker sweeps, git history) with the free-side exceptions the builds genuinely need; the `bash_guard.py` docstring and step 001's settings prescriptions agree point for point; and the anti-over-build guardrails (family-with-first-file, test-that-says-nothing-yet, boring-standard-tool, cold review invited to split the foundation steps) are present rather than violated. The asset templates' adoption guidance is otherwise consistent with the prompt (the F2 gap is the one exception found).

## 3. Questions for the operator

1. Confirm the intended (k)/(l) escalation semantics behind F1: is the prompt meant to escalate more broadly than the spec's k+l / l+c combinations (safe), or were the glosses meant to restate the spec exactly?
2. Which track owns the PZ per-image README and the other PZ-facing root §9 deliverables (F5)?
3. Root §4.3 requires the builder to support password-protected beta branches. Is verifying that capability part of the builder's step gate, and if so, does it need an operator-supplied beta-branch password — currently absent from the external-prerequisites list (possibly deliberately, since PZ itself needs none)?
4. Is per-run fresh-runner setup on CI meant to satisfy step 003's "proving a fresh setup still works" until root §8's scheduled jobs exist (F6)?
5. Step 000 bundles gitignore, setup command, check/test/verify in both scopes, commit-hook wiring and governance lint under one gate — intended as one step, with the cold review as the sanctioned splitting mechanism?

## 4. Verdict

0 blocking, 2 important (plus 4 minor) — not a quiet round, but nothing blocks handoff; both important findings are wording/transmission fixes inside the prompt, not structural defects.
