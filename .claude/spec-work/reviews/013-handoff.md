# Review 013 — handoff lens

- **Lens:** handoff prompt (phase 7), round 4
- **Model:** claude-fable-5 (session model)
- **Isolation:** worktree, fresh context
- **Commit reviewed:** 1a9e0292c5565f855324ebc610d407f6b5e78ba1
- **Documents given:** SPECIFICATIONS.md, steamcmd/SPECIFICATIONS.md,
  project-zomboid/SPECIFICATIONS.md, .claude/spec-work/handoff/PROMPT.md,
  .claude/spec-work/handoff/assets/ (nine templates),
  .claude/refs/image-contract.md (context only), .claude/settings.json.
  Context block carried the authoritative repository-state statement and
  noted three prior triaged rounds.

---

Checkout verified at `1a9e0292c5565f855324ebc610d407f6b5e78ba1` before reading. I read the prompt, all nine asset templates, the three specification documents, `.claude/settings.json`, and the head of `.claude/refs/image-contract.md`.

**Cross-reference check:** every section reference the prompt makes (root §1, §2.6, §2.9, §3.1, §4.3, §5.2, §5.4, §5.5, §6–§11; project-zomboid §1, §2 items (a)–(o), §4, §6) resolves to a section that exists; the asset inventory the prompt names (four skills, five agents) matches the directory exactly; `.claude/settings.json` contains the `autoMemoryEnabled: false` key the prompt claims. One citation is imprecise rather than unresolved — finding 3.

---

## 1. Summary-back

The project is a public monorepo of Docker images for Steam dedicated game servers: a date-tagged steamcmd builder image, and per-game runtime images with the game baked in at build time — the first being Project Zomboid Build 42 — published to GHCR under immutable `-rN` tags with CI-driven rebuild-on-buildid-change, all governed by a conventions section (uid-agnostic, loud-fail configuration, mediated SIGTERM shutdown, protocol-level healthcheck).

The prompt hands this to an implementing agent working in three tracks (root, steamcmd, project-zomboid), one gated step at a time, with file-based memory (per-track PLAN/DECISIONS, one CLAUDE.md), track-qualified step tags, a pre-commit/just harness, and a permission baseline enforcing a free-local / gated-outward action boundary.

In its first session the implementer would: read the prompt in full, then the three specifications in full; write the three plans (foundation steps 000–002 first, milestones, per-step objective/spec-sections/deliverables/test/status, external-prerequisites list, open-questions section), three initialized decision logs, a ~160-line CLAUDE.md restating the eleven rules with the track map and Current state pointer, and a descriptive README with a For-reviewers section; commit all eight files in one `meta:` commit; spawn a fresh read-only subagent (inline prompt; inputs: the three specs, the eight files, `.claude/refs/`; `CLAUDE.md` named as convention source; all of `.claude/spec-work/` out of bounds) to audit the plans on coverage, ordering, granularity, proportion, prerequisites, consistency, and premises; triage and commit accepted findings; present the triage and corrected plans; stop. Step-000 starts only on operator approval.

## 2. Findings

**1. Important — First-task §§ "step-000"–"step-002" vs rule 1 and task 3: the foundation steps' prescriptive detail has no ordered survival path once the prompt becomes unreadable.**
Evidence: rule 1 makes the prompt "consumed at bootstrap", and task 3 states "after this session `CLAUDE.md`, not this prompt, is what a session reads". The prompt knows this failure class and explicitly orders two conventions into CLAUDE.md precisely because "the bootstrap cold review sources those conventions from `CLAUDE.md`, so they must actually be there." But the dense prescriptive content of the three foundation steps — step-001's allow/ask/deny classifier, the "a bare `git commit` allowance admits `--amend`" trap, the ask-not-deny reasoning, the probe-and-report duties; step-000's gitignore inventory and the CI-workflow deferral reasoning; step-002's instantiation list and the not-yet-adopted carve-out — is ordered nowhere but into the implementer's plan-writing judgment. A session interrupted between plan approval and executing steps 000–002 re-orients from PLAN.md entries that may carry only summaries, and the cold reviewer cannot detect the loss because it is forbidden to read the prompt. Direction: one sentence in task 1 requiring the foundation-step plan entries to carry the prompt's per-step prescriptions as their deliverables/test content (the same "so they must actually be there" move task 3 already makes).

**2. Minor — Cold-review instructions vs task 3: "what counts as cheap" is declared to live in CLAUDE.md but is never ordered into it.**
Evidence: the cold-review paragraph tells the implementer the reviewer's cited conventions — "the step entry shape, boundary-crossing test costs, what counts as cheap — live in the CLAUDE.md you have just written". Task 3 orders only the first two in ("the plan-step entry shape and the boundary-crossing-cost rule"). The cheap/slow-multi-gigabyte/shared-public-state cost taxonomy lives only in the plan-ordering guidance; rule 9's boundary enumeration (carried whole) classifies free vs gated, not cheap vs slow. Two reasonable implementations diverge in whether the reviewer can actually check its "cheap steps genuinely first" criterion against a source. Direction: add the cost taxonomy to task 3's CLAUDE.md content list, or drop it from the reviewer-sourcing sentence.

**3. Minor — Rule 9: the Steam-browser-registration claim is cited to root §5.2, which does not state it.**
Evidence: "a default-profile server start transiently registers the server on the public Steam browser (root §5.2)". Root §5.2 only defines what "advertised" means; the fact that a default-profile PZ start registers with Steam lives in project-zomboid §2 (ports "advertised… Steam server browser registration") and §3 ("would register with Steam on the wrong number"). The claim is spec-supported, but the citation sends a verifier to a section that cannot confirm it, and "transiently" is stated nowhere. Direction: cite project-zomboid §2/§3 (alone or alongside root §5.2).

**4. Minor — Rule 6 / approve-step template: the first two step closes predate the ritual that defines the tag-message shape, and the template then anchors on those tags.**
Evidence: `/approve-step` is instantiated at step-002, so steps 000 and 001 are closed from rule 6 alone, which requires only "an annotated tag naming the step". The template's step 3 defines the richer canonical shape ("`{{STEP_ID}} — <step title>`, then `Approved YYYY-MM-DD.`…") but instructs "Message shape follows the existing tags" — so the canonical shape risks being set by two tags created without it. The prompt built an explicit pre-002 fallback for `/resume-step` but not for the close ritual. Cosmetic divergence, self-healing if noticed. Direction: one clause in rule 6 or task 3 giving the tag-message shape (or pointing the pre-002 closes at the template, which rule 3's carve-out already makes readable).

Nothing found in the categories: unsupported check families (Dockerfile lint, entrypoint-language lint, Actions YAML validation, prose lint, governance parse checks all match the stack); missing or invented external prerequisites (repo+Actions+remote, first-push authorization, GHCR namespace, per-package visibility flip, conditional Docker Hub credential — complete against the spec, none invented); action-boundary gaps (registry writes, GitHub writes, dev-tag pruning, unscoped sweeps, history rewrites all gated; Steam-registration side effect of default-profile starts explicitly handled); instructions into `.claude/spec-work/` beyond the prompt and assets (the cold-review prompt even fences off CLAUDE.md's assets pointer); template/prompt conflicts (placeholders, `.claude/reviews/` gitignore assumption, milestone-close track-keying exception, not-yet-adopted carve-out — all mutually consistent); over-building (the prompt is aggressively anti-bespoke: pre-commit/just named as the operator's standard, the backtick-scanner regret, "a *test* command that says so is the correct state", check families arriving with their first file).

## 3. Questions for the operator

1. Rule 1's classifier pulls back any resolution changing "a documented limitation" — which captures even spec-pre-committed responses like item (i)'s "player count documented as unavailable" and item (m)'s "unknown — assume irreversible", despite those following the pre-committed path exactly. Is that round-trip deliberate, or should spec-pre-committed documentation consequences be autonomous?
2. Is the assumption that the same bootstrap session (or one reading only PLAN.md) executes steps 000–002 — i.e., do you accept finding 1's risk, or was the plan always intended as the full carrier of the foundation-step detail?
3. The Claude Code facts frozen into the prompt and templates (2.1.231: `allowed-tools` inert, `Write(path)` rules never firing, `disallowed-tools` turn-wide) — are they still the versions the implementer will run, or is the step-001/002 probe expected to overturn them? (The prompt is safe either way; the question is whether the prose should still assert them.)
4. Specification question, not a prompt finding: root §8's smoke gate and root §5.5's healthcheck both hinge on PZ open item (k)/(l) fallbacks; if (l) resolves unfavorably the image "must not ship" — is the operator prepared for that outcome to surface as a blocked track rather than a degraded release, as the prompt's rule-1 list correctly relays?

## 4. Verdict

0 blocking, 1 important, 3 minor — not a quiet round, but nothing blocks the handoff; finding 1 is the one worth fixing before the prompt is used.
