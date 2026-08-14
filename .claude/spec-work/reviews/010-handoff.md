# Review 010 — handoff lens

- **Lens:** handoff prompt (phase 7)
- **Model:** claude-fable-5 (session model)
- **Isolation:** worktree, fresh context
- **Commit reviewed:** 922eda8dd176b183b6328d9ac5d23e31d13fd4a5
- **Documents given:** SPECIFICATIONS.md, steamcmd/SPECIFICATIONS.md,
  project-zomboid/SPECIFICATIONS.md, .claude/spec-work/handoff/PROMPT.md,
  .claude/spec-work/handoff/assets/ (nine templates),
  .claude/refs/image-contract.md (context only)
- **Numbering note:** spec-phase review rounds (through challenge 009,
  see decisions.md) predate this archive directory; numbering continues
  from them.

> [Archivist note — finding 2 and operator question 1 rest on a false
> premise. Verified after the round: `git ls-tree -r 922eda8` shows
> every file the finding names — the three specification documents,
> `.claude/settings.json`, the handoff prompt and assets — tracked and
> committed at the reviewed HEAD. The reviewer derived repository state
> from a stale view despite the context block's instruction; the
> prompt's claims "committed during the specification phase" and "the
> range is simply the whole history" hold.]

---

All reading done; report follows.

---

# Review report — handoff prompt (`.claude/spec-work/handoff/PROMPT.md`)

Checkout verified at `922eda8dd176b183b6328d9ac5d23e31d13fd4a5`.

**Cross-reference check:** every `§N.M` / `root §N` citation in the prompt resolves to a real section of the specification documents, and — with the two slack instances recorded in finding 6 — each cited section says what the prompt claims. The asset inventory (four skills, five agents) matches the nine files on disk under `assets/`; the placeholder sets the prompt names exist in the templates.

## 1. Summary-back

The prompt hands a three-document specification (root + steamcmd + project-zomboid) to a cold Claude Code session that will build, gated step by step, a public repo of Docker images: a steamcmd builder and a Project Zomboid B42 runtime image, published to GHCR with CI-driven rebuilds. Work is organized as three tracks with track-qualified step ids, one step in progress repo-wide, annotated `step-*` tags marking approved states. Eleven permanent rules cover: read-only specs with a decision-logged amendment channel (open facts (a)–(o) settle autonomously on pre-committed paths, five named items always escalate); one-step-at-a-time gating with self-verification through a `just`/`pre-commit` check/test/verify harness; file-based memory (per-track PLAN/DECISIONS, one ~160-line CLAUDE.md, `.claude/docs/`, read-only `.claude/refs/`); decision logs; no secrets; small tagged commits with same-commit staleness sweeps; an action boundary (local dev loop free, registry/GitHub/outward writes gated, enforced by a step-001 settings baseline); persistence budgets; and proportionality.

**First session, as the implementer would execute it:** read the three specifications in full → write the eight governance files (3 PLANs together covering every spec section, with steps 000–002 = harness / permission baseline / workflow tooling first; 3 DECISIONS logs, root one with a workflow-adoption entry; CLAUDE.md restating the rules with the track map, "Current state" section, assets pointer and not-yet-adopted list; descriptive README with a For-reviewers section) → commit all eight in one `meta:` commit → spawn a fresh read-only inline subagent that audits the plans against only the specs plus the eight files (coverage, ordering, granularity, proportion, prerequisites, consistency, premises), told CLAUDE.md is the conventions source and `.claude/spec-work/` is out of bounds → triage findings and present triage + plans → stop; step-000 begins only on approval.

## 2. Findings

**1. Important — Rule 9 vs the spec's advertised-port facts: local container runs perform a Steam registration that rule 9's own wording gates.** Rule 9's free side includes "creating, starting … this project's containers" and its gated side includes "any other outward side effect (webhooks, mail, uploads, **registrations**)". The specification establishes that starting the PZ server on its default profile registers it publicly with the Steam server browser (root §5.2 "Steam server browser registration"; project-zomboid §3: "the game port is advertised, and a first run on generated defaults would register with Steam on the wrong number") — an outward, shared-state side effect, and with `SERVER_PASSWORD` optional-open (PZ §3) a publicly joinable server from the developer's IP. A cold implementer's first local PZ run either violates the letter of "registrations" or silently reads the boundary as blessing it; the same tension recurs in CI's smoke gate. Direction: have the operator decide explicitly — e.g., local test runs default to the non-Steam profile, or the boundary names Steam registration during local/CI test runs as an accepted free side effect.

**2. Important — the prompt asserts a committed repository state that does not hold at the reviewed commit.** Rule 3: "auto memory is already disabled for this repository (`.claude/settings.json`, **committed during the specification phase**)"; step-001: "Extend the **committed** `.claude/settings.json`". Per the repository-state snapshot for this review, `.claude/`, `SPECIFICATIONS.md`, `steamcmd/` and `project-zomboid/` are all untracked at this HEAD — nothing the bootstrap leans on (the specs rule 1 declares read-only, the settings file, this prompt) is in history. The first task's "commit the eight files" and rule 3's "before the first step tag exists, the range is simply the whole history" presuppose the specification is already committed beneath them. If the operator commits everything at handoff this dissolves; at the commit under review the claims are unsupported, and a cold-started implementer told to "extend the committed settings.json" would find an untracked file. Direction: land the handoff commit before bootstrap, or make the prompt's first task include committing the inherited spec-phase files.

**3. Important — static placeholder instantiation vs the moving "active track": two reasonable implementations diverge observably.** The prompt instructs: "fill every placeholder with this repository's real commands and paths — including the governance set (`{{PLAN}}`, `{{DECISIONS}}`, `{{SPEC}}`, `{{STEP_ID}}`), which each template resolves to the files and identifier form of the **active track**." But the active track changes across the project's life, while a skill file instantiated at step-002 is static: filled with literal paths (as "real commands and paths" and "a leftover [placeholder] is visible" suggest), `/handover-step` in a later pz-track session sweeps root `PLAN.md` instead of `project-zomboid/PLAN.md`; resolved dynamically (via CLAUDE.md's track map and current-step pointer), it behaves correctly — the operator sees different plans updated depending on the guess. Only `orient` and `optimize-memory` carry multi-track adaptation notes in their headers; `handover-step`, `approve-step`, `resume-step`, `step-reviewer` and `state-reviewer` do not, and `{{SPEC}}` is singular while rule 3 makes root §3/§5 standing reading for component-track steps. Direction: state the resolution mechanism class (look up the active track at invocation from CLAUDE.md) or mandate per-track instantiation — either removes the divergence.

**4. Minor — rule 3 contradicts itself on CLAUDE.md cardinality.** "Exactly one `CLAUDE.md` exists repository-wide" vs., later in the same rule, "a nested `CLAUDE.md` is the fallback" should `.claude/rules/` prove non-functional. The implementer whose rules-file probe fails must break one of the two statements. Direction: word the fallback as the invariant's explicit exception.

**5. Minor — rule 1's "nothing else" amendment commit vs rule 6's same-commit staleness rule.** Rule 1: a spec amendment commit contains "the decision-log entry and the specification text, **nothing else**" (code following later). Rule 6: "everything a change makes stale updates in the same commit … any human-facing documentation the change touches — documentation updated later is documentation that drifts." An amendment that immediately falsifies a README line cannot satisfy both. Direction: state that rule 1 wins for amendment commits and the documentation consequence follows in the step's later commits (rule 1 already says this for code; extend it to docs).

**6. Minor — two citation-accuracy slacks.** (a) Rule 1 describes PZ §2's items as "each naming the requirement resting on it and a pre-committed response per outcome"; the spec pre-commits responses only "where the answer could resolve unfavorably" — items (a), (b), (j), (n), (o) carry none, so the autonomous-path description overstates what the spec provides for them. (b) The opening cites "(root §6)" for both per-image documents being part of the specification; root §6 covers per-**game** specifications only — `steamcmd/SPECIFICATIONS.md` is anchored by its own text, not §6. Direction: loosen both phrasings.

**7. Minor — step-000 packages a deliverable its own gate cannot test, at the edge of one-gate breadth.** Step-000 bundles `.gitignore`, pinned setup, the check/test/verify harness, commit hooks, the governance lint, **and** a CI workflow the prompt itself says is "verified only once I authorise the first push" — many steps later. Building it in step-000 sits against rule 11's build-at-the-moment-of-need, and step-000's test ("fresh clone, setup, check, one commit") exercises none of it. The prompt mitigates by inviting the plan to split further; still, the default packaging is the thing the cold review must push against. Direction: let the plan carry the CI workflow in the step that first gets a remote, or mark it explicitly deferred-verification inside step-000.

**8. Minor — the lint-bends-to-read-only clause omits `.claude/refs/`.** Rule 2's *check* covers "the whole working tree" with one standing exception (`.claude/spec-work/`); the clause "the specification documents are read-only under rule 1, so the lint bends to them" does not extend to `.claude/refs/image-contract.md`, which is equally read-only (rule 3) and equally in the tree. The implementer must infer the same treatment; an exclusion is "a logged decision", but the rule never says refs qualifies. Direction: name refs/ beside the specifications in that clause.

**9. Minor — the external-prerequisites list reads as complete but omits a conditional operator-supplied item.** The prompt enumerates three prerequisites (repo/remote + first push, GHCR owner namespace, visibility flips). Root §2.6 requires a deliberate decision on Docker Hub anonymous-pull throttling ("mirror or authenticated pulls"); if the implementation chooses authenticated pulls, the credential is a CI secret only the operator can supply — a fourth thing "only I can prepare", needed by the first publishing workflow. Direction: either add it as conditional or reword the list as non-exhaustive.

Accuracy checks that came up clean, for the record: the image-contract description in rule 3 matches the document (a hosting platform's image contract, information-not-requirements, conflicts escalate); the check families match the stack (Dockerfiles, chooseable entrypoint language, GH Actions YAML, prose, governance frontmatter/JSON); rule 1's always-escalate items (d)/(e)/(g)/(k)/(l) map correctly to env surface / tag naming / read-only claim / degraded profile / ship-blocker; the eight-file count is right; `git describe --match 'step-*'` is coherent with track-qualified tags under the one-step-in-progress rule; no instruction sends the implementer into `.claude/spec-work/` beyond the prompt and assets; the asset-retirement choreography (prompt ↔ approve-step header ↔ optimize-memory) is mutually consistent; the bootstrap's no-harness gap is explicitly bridged by the cold review; `.claude/settings.json` on disk does contain `"autoMemoryEnabled": false`.

## 3. Questions for the operator

1. Will the specification, `.claude/refs/`, `.claude/settings.json` and this prompt be committed before the bootstrap session opens, so that "committed during the specification phase" and "the range is simply the whole history" are true when read? (Finding 2.)
2. Local PZ runs with Steam integration enabled register the server publicly — free side or gated? Should local testing default to the non-Steam profile? (Finding 1.)
3. For the governance placeholders: one instantiated tooling set that resolves the active track at invocation, or one instantiation per track? (Finding 3.)
4. Is ~160 lines realistic for a CLAUDE.md that must carry rule 9's enumeration whole, eleven restated rules, the track map, file map, session routine, plan-entry conventions and the assets block — or do you expect rule 3's "raise it as a finding" escape to fire on day one, and is that acceptable?
5. The prompt asserts specific Claude Code 2.1.231 permission/skill behaviors (`allowed-tools` inert, `Write(path)` rules never firing) while ordering a re-probe; if the probe contradicts the prompt, is the probe's result simply what binds, with no amendment owed anywhere?

## 4. Verdict

0 blocking, 3 important (findings 1–3), 6 minor — not a quiet round: the boundary contradiction, the uncommitted-state premise, and the active-track instantiation ambiguity each need an operator ruling before bootstrap.
