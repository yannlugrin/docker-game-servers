# Handoff Prompt Review — round 016, handoff lens, session model (Fable), worktree-isolated cold spawn

[Archivist note, main session: F2 and F3's git-state premises are artifacts of the reviewer's isolation worktree, whose git metadata sat at pre-handoff commit befa945 while the file contents were current; in the real repository the handoff directory and the `.claude/docs/image-contract.md` rename have been committed since c5d648a (verified via `git ls-files`). Round 015's reviewer hit the same artifact. Report otherwise verbatim.]

Everything is read: the three specification documents, `PROMPT.md`, all nine asset templates, plus the repository facts the prompt asserts (remote, LICENSE, `.claude/settings.json`, repo visibility). Report follows.

---

# Review report — handoff prompt (`.claude/spec-work/handoff/PROMPT.md`)

**Cross-reference check:** every `§N`/`§N.M` and rule-number reference in the prompt resolves against the two specification documents and the prompt's own rules (root §1, §2.6, §2.8, §3.1, §4, §4.3, §5.4, §5.5, §6, §7, §8, §9, §10, §11; PZ §1, §2 and open items a–o; rules 1–10 cross-cited). The specifications' internal references also resolve. No dangling section reference found.

**Verified repository facts:** `origin` → `github.com/yannlugrin/docker-game-servers` (matches the prompt); the repository answers anonymous API reads (public, as the prompt asserts); `LICENSE` is MIT; `.claude/settings.json` contains `{"autoMemoryEnabled": false}`; the four skills and five agents the prompt names all exist under `assets/`. Two state discrepancies at the reviewed commit are findings 2 and 3 below.

## 1. Summary-back — the first session, step by step

The implementer is handed a public repo of game-server Docker images (steamcmd builder + per-game runtimes, first Project Zomboid B42), governed by a two-document specification it may never edit on its own initiative except to record spec-ordered fact verifications, decision-entry-first. In the bootstrap session it would:

1. Read root `SPECIFICATIONS.md` and `project-zomboid/SPECIFICATIONS.md` in full (the steamcmd stub is a pointer to root §4) — the only spec-phase inputs besides this prompt and `assets/`.
2. Write eight files: root/`steamcmd/`/`project-zomboid/` `PLAN.md` (per-track steps with objective, spec sections, deliverables, operator test with cost/cleanup, status; `step-000` = repository foundation; cheap-local-first ordering; non-code deliverables and PZ §2 open-fact resolutions as steps; external-prerequisites list; closing questions section), three initialized `DECISIONS.md`, a sub-200-line `CLAUDE.md` (rules restated keeping numbering, track map, "Current state" pointer, session routine, image-contract and assets pointers, rule 9's boundary carried whole), and a descriptive root `README.md` with a For-reviewers frame.
3. Commit all of it as one `meta:` commit.
4. Spawn one fresh-context read-only subagent (inline prompt; agent files come at step 000) that reads only the specs and the just-written files — never the conversation, never `.claude/spec-work/` — and audits the plans for coverage, ordering, granularity, prerequisites, consistency, premises.
5. Triage its findings, present triage plus plans, and stop; `step-000` begins only on the operator's approval.

## 2. Findings

**F1 — important — rule 9 (and the step-000 baseline it feeds).** The free carve-out includes "cleanup of local images and volumes (`rmi`, prune)", justified because "local images and test volumes are rebuildable working material — the irreplaceable local state is git's, which stays protected". But the prune family is host-global, not project-local: `docker volume prune` deletes every unused volume on the machine, `docker image prune -a` every unreferenced image — including other projects' state on the same host (this operator's machine visibly hosts several Docker projects). The reasoning covers only project-local resources, yet step 000 will translate this carve-out verbatim into an always-allow permission entry, so the boundary explicitly frees a destructive shared-state action beyond the project. Direction: keep targeted removals (`rm`/`rmi`/`volume rm` by name, filtered/labelled prune) free, and move blanket prune to the ask tier.

**F2 — minor — rule 3 ("git history keeps the templates").** The adoption endgame — "delete the assets directory … git history keeps the templates" — assumes the templates were ever committed. At the reviewed commit, `.claude/spec-work/handoff/` (the prompt and all nine assets) is untracked; deleting the directory after adoption would erase the templates from everywhere, silently falsifying the prompt's claim. Direction: commit the handoff directory before bootstrap, or drop the claim.

**F3 — minor — rule 3 / first-task item 3 (`.claude/docs/image-contract.md`).** The prompt's standing pointer targets `.claude/docs/image-contract.md`. The file exists in the working checkout, but the tracked path at the reviewed commit (`befa945`) is `.claude/doc/image-contract.md` — a fresh clone at bootstrap would find the pointer dangling, and `CLAUDE.md` would be born citing a file git does not carry. Dissolves if the `doc/`→`docs/` rename is committed before handoff.

**F4 — minor — bootstrap cold-review instructions vs. what CLAUDE.md is told to contain.** The bootstrap says "The workflow conventions its criteria cite — step shape, boundary-crossing test costs, the one-step-in-progress rule — live in the `CLAUDE.md` you have just written". One-step-in-progress is rule 6 and lands in CLAUDE.md; but the step-entry shape and the cost/cleanup convention exist only in first-task item 1, which is not among the ground rules item 3 tells CLAUDE.md to restate. Two reasonable implementations diverge: one encodes the step template in CLAUDE.md, one leaves it implicit in the plans — and in the second, the reviewer's named convention source lacks two of the three cited conventions. Direction: list the plan-step entry shape and the boundary-crossing-cost rule among CLAUDE.md's required contents (later sessions extending plans need them anyway).

**F5 — minor — `optimize-memory` template vs. the prompt's line budget.** The prompt makes CLAUDE.md's 200-line cap "a hard budget that yields to exactly one thing: rule 9's boundary enumeration is carried whole". The template states both "The file must stay under 200 lines" and "never compress … the action-boundary enumeration" with no yield clause — jointly unsatisfiable if the enumeration plus essentials exceed 200 — and rule 3's otherwise-detailed adaptation checklist does not name this reconciliation. Direction: add the yield clause to the adaptation list (or to the template at instantiation).

Not findings, noted as sound: the check families match the stack (Dockerfile, shell, YAML incl. GHA schema and compose, markdown/prose, `.claude` frontmatter/JSON) and the prompt explicitly makes the list "the expected instance, not the boundary"; the external-prerequisite list (visibility flip, first-push authorisation, conditional Docker Hub credential, "no Steam credential") is complete and spec-supported; the always-come-back set (e, g, k, l) matches the items whose unfavorable resolutions carry tier/ship consequences in PZ §2; all "never exist yet at bootstrap" traps I probed (step-tag lookup before any tag, missing harness at bootstrap, templates naming un-adopted agents) are each explicitly pre-handled.

## 3. Questions for the operator

1. Will the `doc/`→`docs/` rename and the `handoff/` directory be committed before the bootstrap session runs? (F2 and F3 dissolve if yes.)
2. Is `autoMemoryEnabled` the verified settings key for the Claude Code version that will run the implementation? The prompt hedges with the step-000 probe, but confirming now removes a known-unknown from the enforcement baseline.
3. Is host-global prune deliberately acceptable on the machines that will run this work (F1), or was the carve-out meant project-local?
4. PZ §2 item (d) decides whether `ADMIN_PASSWORD` is offered at all — a documented-surface change. Intended to flow through the general "changes a requirement, a tier, a documented limitation" clause rather than the named always-come-back four?
5. Rule 9 files `gh` reads under "anonymous remote reads", but `gh` runs authenticated in practice, and no permission prefix can split `gh api` reads from writes — is the read/write line intended to be enforced by the guard-hook mechanism the prompt already provides?

## 4. Verdict

0 blocking, 1 important (F1), 4 minor — not a quiet round, but nothing blocks handoff once F1 is decided and the two pre-handoff commits (F2, F3) land.
