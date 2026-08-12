# Handoff Prompt Review — round 015, handoff lens, Opus, worktree-isolated cold spawn

[Archivist note, main session: F6's factual premise and questions 2–3 were verified false after receipt — `.claude/spec-work/handoff/` is fully tracked and `.claude/docs/image-contract.md` is the committed path (rename in c5d648a); the reviewer misread git state in its worktree. Report otherwise verbatim.]

All three specification documents, the handoff prompt and the nine asset templates read in full.

**Cross-reference check.** Every `§N` / `§N.M` reference in `PROMPT.md` resolves to a real section that says what the prompt claims (root §1, §2.6, §3.1, §4, §4.3, §5.4, §6, §7, §8, §9, §10, §11; `project-zomboid/SPECIFICATIONS.md` §1, §2). Verified mechanically for the specifications too: no unresolved reference in either document. Repository claims check out: `origin` is `git@github.com:yannlugrin/docker-game-servers.git`, `.claude/settings.json` is committed with `autoMemoryEnabled: false`, `LICENSE` is MIT, `steamcmd/` and `project-zomboid/` both exist, `.claude/docs/image-contract.md` is on disk, and neither specification references anything under `.claude/spec-work/`.

---

## 1. Summary-back — the implementer's first session

A fresh session at the repository root is told to read `.claude/spec-work/handoff/PROMPT.md` in full and do what it says. It would:

1. Read `SPECIFICATIONS.md` and `project-zomboid/SPECIFICATIONS.md` end to end (and note `steamcmd/SPECIFICATIONS.md` is a pointer to root §4). This is the only session that reads everything.
2. Absorb ten permanent ground rules: specifications are read-only and amended only through a decision-log channel; work is one operator-gated step at a time, self-verified by a check/test/verify harness before handover; all memory lives in files organised per track (root, `steamcmd/`, `project-zomboid/`), each with `PLAN.md` and `DECISIONS.md`, plus one small `CLAUDE.md`; decisions get logged with `D-NNN` ids per log; no secrets in the repository; small commits prefixed with track-qualified step ids and annotated `step-*` tags on approval; English; a descriptive root `README.md`; a free/gated action boundary (local read-only, `docker build`/`run`, anonymous remote reads free — every push, publish and GitHub write gated); and a persistence budget that makes asking part of the workflow.
3. Write, without implementing anything: three `PLAN.md` files derived from the specification (steps with objective, spec sections, deliverables, how-the-operator-tests, status; `step-000` being the repository foundation — `.gitignore`, pinned deps behind one setup command, the check/test/verify harness with pre-commit hooks and a CI workflow, a permission-and-hook baseline extending `.claude/settings.json`, and workflow tooling instantiated from `handoff/assets/`), three `DECISIONS.md` files, `CLAUDE.md`, and the root `README.md` with a "For reviewers" section.
4. Commit all of it as one `meta:` commit, then spawn a cold read-only subagent that sees only the specifications and the new files (never the conversation, never `.claude/spec-work/`) to audit the plans on coverage, ordering, granularity, prerequisites, consistency and unverified premises.
5. Triage the findings and present them with the plans. Step `000` starts only after the operator approves.

---

## 2. Findings

### F1 — important — PROMPT rules 1 and 4, `project-zomboid/SPECIFICATIONS.md` §2
**Whether resolving a PZ open fact needs the operator's approval before the spec is amended is genuinely ambiguous.** Rule 1 opens with "you never edit one on your own initiative … stop and raise it with me. If we agree a change is needed …". It then says the fifteen open facts of PZ §2 "are the expected case of this channel … verifying one and recording its resolution in that document is this rule followed, not an exception to it — decision entry first, then the amendment commit." Rule 4 classes "spec changes" under "choices we make together". An open fact is not an ambiguity to raise — it is a research task the spec ordered — so "this rule followed" can be read as *autonomous once verified*, or as *fifteen more approval round-trips*. The divergence is observable and large. It matters most because several open items carry consequences that are unambiguously the operator's: item (l) unfavourable means "the image **must not ship** on that combination"; item (k) unfavourable means shipping a documented degraded healthcheck; item (g) can force a narrowed read-only claim as a reasoned root §5.1 deviation; item (e) unfavourable switches the entire tag scheme to buildid-derived names.
*Direction:* separate the two halves explicitly — recording a verified fact is within latitude (logged, then amended), while any resolution that changes a requirement, a tier, a documented limitation or the ship decision is a together-decision. Naming (e), (g), (k), (l) as the ones that always come back is cheap and removes the guess.

### F2 — important — PROMPT rule 9 and the step-`000` permission baseline
**The action boundary and the proposed allowlist omit the commands the work actually needs.** Free is defined as "anything local and read-only … with two deliberate carve-outs …: local `docker build` and `docker run`". But root §8's smoke gate — which the implementer must run locally long before CI — requires starting the image, waiting for healthy, sending the stop signal and reading the exit code, i.e. `docker stop`, `docker wait`/`inspect`, `docker logs`, `docker ps`, `docker rm`; root §5.5 requires demonstrating a `docker exec` save/announce path; the smoke test's read-only-rootfs run needs mounts and volumes (`docker volume create`/`rm`); and a multi-gigabyte PZ image makes `docker rmi`/prune part of the loop. None of these is read-only and none is a named carve-out, so by the boundary's own construction they are gated. The step-`000` allow list repeats the gap ("local docker builds and runs"), and its git enumeration — "add, commit, status, diff, log, describe, annotated tags" — omits `git show`, which the `step-reviewer` template it also instantiates explicitly relies on. Two reasonable implementations diverge visibly: one asks the operator on every container stop, the other decides for itself that the whole local Docker surface is free.
*Direction:* state the free side as the local container lifecycle end to end (build, run, exec, logs, inspect, stop, rm, volumes, compose up/down) and say explicitly whether any local Docker destruction is gated; add read-only git (`show`, `rev-parse`, `tag -l`) to the allow enumeration.

### F3 — important — PROMPT rule 3 vs. `assets/optimize-memory.md`
**The prompt files an operator-supplied reference in the directory the mandatory compaction pass is told to delete from.** Rule 3 places `.claude/docs/image-contract.md` — "the container contract of one real platform that consumes these images" — inside `.claude/docs/`, defined in the same rule as "your working memory". `optimize-memory`'s staleness sweep asks of *every* file under `.claude/docs/`: "**Is it consumed?** If the step or question it exists for is now `done`/resolved, fold anything still operative into its proper home …, then delete the file and its pointer." Once the image tracks are done, `image-contract.md` matches that test exactly — and it is not the implementer's memory to fold and discard. The prompt's instantiation guidance enumerates what the templates predate (per-track memory, one `D-NNN` namespace, narrower session routines) and never marks this file non-deletable. The pass is required at every milestone close, and the agent's edits are reviewed by a main session that has no standing instruction to protect the file.
*Direction:* either add an explicit exemption to the instantiation guidance (operator-supplied references are never swept), or give operator-supplied inputs a directory distinct from the implementer's own notes.

### F4 — important — PROMPT rule 3 vs. `assets/handover-step.md`, `assets/approve-step.md`
**The templates hardcode a step-id namespace that rule 6 replaces, and the prompt's adaptation list does not include it.** `handover-step` step 4 requires commits "with `step-NNN:` subjects"; `approve-step` prescribes the close subject "`step-NNN: close — approved, status done, entry compacted`", "Annotated tag `step-NNN`", and a tag title line "`step NNN — <step title>`". Rule 6 makes identifiers track-qualified — `step-000` for the root track, `step-sc-001`, `step-pz-001` for image tracks. The prompt tells the implementer exactly what is stale in the templates: "they assume a single plan, a single decision log, a single specification document and one `D-NNN` namespace". A closed enumeration that omits the step-id namespace invites an instantiation that faithfully preserves `step-NNN`, producing wrong commit subjects and wrong tag names in the one ritual that creates the `step-*` anchors rule 3's re-orientation depends on.
*Direction:* add the step-id namespace to that enumeration (`step-NNN` → the active track's qualified form).

### F5 — minor — PROMPT rule 2
**The check families presume a stack the specification deliberately leaves open, and one shipped artifact class has no coverage at all.** Rule 2 lists Dockerfile lint, "shell script syntax and static analysis (**entrypoints**, tooling scripts)", YAML, markdown/prose — then adds two families "whatever the stack". Naming entrypoints as shell scripts decides an implementation choice the specification refuses to make (its reading contract: "never prescribes implementation"). Separately, root §5.5 makes two shipped static clients (Steam query, RCON) a **must**, with a size expectation to be measured (root §2.9); whether they are vendored binaries or compiled in the builder stage, they need pinning, provenance and a check family, and the prompt mentions them nowhere — including in rule 9, where fetching anything "not pinned in the repository" is gated.
*Direction:* phrase the list as "every language and artifact you ship gets syntax and static analysis in the harness", with the current list as the expected instance, and add one line on how the §5.5 clients are obtained, pinned and covered.

### F6 — minor — PROMPT rule 2, repository state
**The harness exclusion is keyed to tracked status, but the handoff directory is untracked.** Rule 2 defines *check* as running over "the whole working tree, untracked files included and gitignored paths excluded, with one standing exception … the **tracked** files under `.claude/spec-work/` are excluded". `PROMPT.md` and `assets/` are currently untracked in the working tree (git tracks only `decisions.md`, `external-review-prompt.md` and `reviews/`), so as written the harness would lint the handoff prompt and the un-instantiated templates — files rule 1 makes no session's reading material and that are scheduled for deletion. The same fact undercuts rule 3's justification for that deletion: "git history keeps the templates" is true only if they are committed first.
*Direction:* key the exclusion to the path rather than to tracked status, and have the operator commit the handoff directory before the bootstrap session.

### F7 — minor — PROMPT, first task, cold-review subagent
**The reviewer is asked to judge conventions defined only in the document it must not read.** Its criteria include "each step testable by me alone, boundary-crossing tests naming their cost and cleanup" (rule 9), "the one-step-in-progress rule respected by the plans' shape" (rule 6), and "the cheap steps genuinely first" — none of which is in either specification. They are recoverable from the freshly written `CLAUDE.md`, which falls under "the files you have just written", but the prompt never says so; and that `CLAUDE.md` will itself carry a pointer to `.claude/spec-work/handoff/assets/` plus rule 1's exception, which the reviewer is forbidden to follow.
*Direction:* have the inline reviewer prompt name `CLAUDE.md` as the source of the workflow conventions, and tell it to treat the assets pointer as out of bounds.

### F8 — minor — PROMPT rule 3, reading rule vs. root §5/§6
**"The other tracks' [specifications] not at all" can be read as excluding the root specification from image-track sessions.** The bootstrap paragraph says per-image specifications are read "the active track's specification in full, the other tracks' not at all"; the routine then lists "the active track's `PLAN.md`, `DECISIONS.md` and `SPECIFICATIONS.md` … and the spec sections relevant to the current step". For the `steamcmd` track the active specification is a seven-line pointer whose entire substance is root §4; for `project-zomboid` it is a document that root §6 binds to root §5 "in full". Whether the conventions layer is actually loaded then rests entirely on each step's section list being complete — the one thing a plan is most likely to under-enumerate.
*Direction:* state that the root specification is never "another track's document" — root §3 and §5 are standing reading for any image-track step.

### F9 — minor — PROMPT step `000` vs. root §2.8
**The periodic uncached CI run inherits the deactivation trap without inheriting the countermeasure.** Step `000` asks for "a periodic uncached run proving a fresh setup still works". Root §2.8 states that `schedule`-triggered workflows in a public repository are disabled after roughly 60 days without activity, and root §8 imposes deactivation-resistance only on the refresh flow. A freshness job that quietly stops running is the same silent failure the specification builds a whole clause around.
*Direction:* note that §2.8 applies to this job too, or fold the uncached run into the §8 refresh flow so one staleness check covers both.

### F10 — minor — PROMPT rule 9 vs. `assets/step-reviewer.md`, `assets/state-reviewer.md`
**`{{NEVER_RUN}}` does not map cleanly onto rule 9's boundary.** Both templates source it "from the rule-9 boundary", while step `000` is told to "reserve **deny** for what has no authorised use at all" — a set rule 9 arguably leaves empty, since everything gated is merely "only when I explicitly ask". A subagent cannot obtain that authorisation mid-run, so for a reviewer agent the whole *gated* set is effectively never-run, not just the deny set.
*Direction:* say which set the placeholder takes (the gated set, for agents that cannot ask).

### F11 — minor — PROMPT, first task, external prerequisites
**Repository visibility is not on the prerequisite list.** The prompt lists the GHCR package visibility flip, the first-push authorisation, and a conditional Docker Hub credential. It does not list the repository itself being public, which root §1 and §7 assume, which root §2.6's free hosting rests on, and which root §2.8's 60-day rule is explicitly scoped to ("In a public repository"). On a private repository the Actions minutes are also billed — a cost the action boundary otherwise takes care to enumerate.
*Direction:* add repository visibility to the external list with the step that first depends on it, or state that it is already public.

---

## 3. Questions for the operator

1. On F1: when the implementer verifies a PZ §2 open fact, does it amend `project-zomboid/SPECIFICATIONS.md` on its own after logging the decision, or does every amendment come back to you first? If it is split, where is the line?
2. Do you intend to commit `.claude/spec-work/handoff/` (prompt and assets) before the bootstrap session? Several instructions — the harness exclusion, "git history keeps the templates" — behave differently depending on the answer.
3. `.claude/docs/image-contract.md` exists on disk, but git tracks the same file at `.claude/doc/image-contract.md`; the rename appears uncommitted. Is that intentional, and will the path the prompt cites be the committed one?
4. Is `github.com/yannlugrin/docker-game-servers` already public, and is the GHCR namespace `ghcr.io/yannlugrin` already in use for anything that could collide with `steamcmd` or `project-zomboid`?
5. Is `.claude/rules/` with `paths` frontmatter a mechanism you have seen work in the version the implementer will run? The prompt tells it to prove this before relying on it; I want to know whether you expect the proof to succeed or the nested-`CLAUDE.md` fallback to be the real path.
6. Do you want the implementer's local Docker cleanup (`docker rmi`, `volume rm`, prune of multi-gigabyte build artifacts) to be free, or to come back to you each time?

---

## 4. Verdict

0 blocking, 4 important (F1–F4), 7 minor. Not a quiet round — F1's approval ambiguity and F2's action-boundary gap would both bite in the first working week, and F3 and F4 are conflicts between the prompt's own rules and the templates it ships.
