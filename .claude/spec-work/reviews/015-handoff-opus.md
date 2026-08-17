# Review 015 — handoff lens (Opus round)

- **Lens:** handoff prompt (phase 7), round 2 — divergent-model round
- **Model:** claude-opus (user-approved divergence from session model)
- **Isolation:** worktree, cold context
- **Commit reviewed:** b26fc7f (review 014 triage applied)
- **Documents given:** SPECIFICATIONS.md, project-zomboid/SPECIFICATIONS.md, .claude/spec-work/handoff/PROMPT.md, .claude/spec-work/handoff/assets/ (10 templates), .claude/refs/image-contract.md named as operator reference

[Archivist note: the reviewer's worktree materialized at 596f91b — the tip
of `main`, which holds a *previous handoff iteration's* implementation
(branches handoff-0/1/2 predate the current handoff-3 line). The stale-
checkout guard in the context block caught it; the reviewer extracted
b26fc7f and reviewed that. The report below is against b26fc7f as claimed.]

---

I read the full specification (both documents), the handoff prompt, all ten asset templates, `bash_guard.py`, `.claude/settings.json` and `.claude/refs/image-contract.md`.

**Checkout note.** The worktree was at `596f91b`, not the expected `b26fc7f`, and its tree contained implementation artifacts (`CLAUDE.md`, `PLAN.md`, `justfile`, …) — a divergent line, not an ancestor. I did not review it. I extracted `b26fc7f` (whose tree matches the authoritative file list exactly) to scratchpad and reviewed that. Everything below refers to `b26fc7f`.

**Cross-reference check.** All 35 `§N.M` references in `PROMPT.md` resolve (root §2.6, §2.8, §2.9, §3, §3.1, §4, §4.3, §5, §5.1, §5.4, §5.5, §6, §7, §8, §9, §10, §11; PZ §1, §2, §4), and each says what the prompt claims it says — I checked the substance of every one, including the three PZ open-item escalations, root §2.9's measurement items, and the prerequisite citations. The asset templates contain no `§` references. No finding.

---

## 1. Summary-back — the implementer's first session, step by step

A fresh session at the repository root is told to read `PROMPT.md` in full and obey it. It reads both specification documents cover to cover. It absorbs eleven permanent ground rules: specs are read-only and amendable only through a decision-entry-first channel; work is one operator-gated step at a time; all memory lives in files (`CLAUDE.md` plus a per-track `PLAN.md`/`DECISIONS.md`, with two tracks — root and `pz`); decisions are logged per track; no secrets; small track-prefixed commits with annotated `step-*` tags on approval; English; a descriptive `README.md`; a hard action boundary (local and read-only free, plus named exceptions for Steam downloads, pinned-image pulls and GitHub API reads; every registry push, GitHub write and unscoped destructive sweep gated); a persistence budget; and a proportionality rule that outranks the thoroughness of the others.

It then produces six files — two plans, two decision logs, `CLAUDE.md` (~180 lines, restating the rules with rule 9's boundary carried whole), and `README.md` with a "For reviewers" frame. The plans must derive their order from the spec's own dependencies, account for every section of both documents and every open fact item by item, list external prerequisites with the step that needs them, and open with four gated foundation steps on the root track: `000` harness (gitignore, pinned deps, one `check` entry point taking a scope, `test`, `verify`, commit hooks, governance-document lint), `001` permission and hook baseline (instantiate `bash_guard.py`, edit only its `REGISTRY` and `CASES`, pair it with broad allows plus a short deny backstop, then probe what actually enforces and write the measurements into `.claude/docs/`), `002` workflow tooling (instantiate four skills and three agents from the assets directory), `003` the same harness on GitHub Actions, gated by a real green run. It commits the six files as one `meta:` commit, spawns a fresh read-only subagent with an inline prompt to cold-review the plans against the specs on seven criteria, triages the findings, applies and commits the accepted ones, and presents the triage plus corrected plans. Step `000` begins only on the operator's approval.

---

## 2. Findings

### Finding 1 — important — Rule 1, "Open facts": the autonomous/escalate split contradicts itself on several PZ items

Rule 1 says "**verifying a fact that lands on its favorable or pre-committed path is autonomous**", then says "**These always come back to me before any amendment or ship decision**: … and any resolution that would change a variable's mandatory/optional tier, a requirement, a documented limitation, or drop a documented capability."

Several of PZ §2's pre-committed unfavorable branches do exactly the second thing:
- item **(i)** unfavorable → "the player count is documented as unavailable in that configuration … a stated limitation" — drops a documented capability *and* is pre-committed;
- item **(d)** unfavorable → "this image does not document the variable" (`ADMIN_PASSWORD`) — drops a documented capability *and* is pre-committed;
- item **(f)** unfavorable → "a documented image-behavior variable selects the probe mode" — adds a variable to the §5.3 environment surface *and* is pre-committed;
- item **(e)** unfavorable → buildid-derived tags, an operator-facing change to root §7's naming.

Two reasonable implementers diverge observably: one resolves (i) and (d) alone and reports in a step summary, the other stops and asks. Since the whole point of the clause is to fix where the operator's hand is required, the ambiguity lands on the most consequential decisions in the project.

*Direction:* state which clause wins — e.g. the escalation list overrides the pre-committed-path latitude wherever both apply — or enumerate the pre-committed branches that are nonetheless autonomous, rather than leaving the two rules to collide.

### Finding 2 — important — Rule 2 / step-001 registry inventory: `just` is an opaque gate-bypass for exactly the acts rule 9 protects

The prompt names `just` as the task runner and tells step `001` to "Inventory what this project actually runs — the harness, `docker` and its relatives, `steamcmd` invocations, `just`, `pre-commit`, `gh`, anything the `justfile` shells out to."

But the guard is a `PreToolUse` hook on the **Bash tool**, judging the command string it is given. It sees `just release`; the `docker push` that recipe executes is spawned by `just`, never by the Bash tool, so no hook fires and no `deny` prefix rule in `settings.json` matches either. Registering `docker` in the registry buys nothing here, and `just` is not a shell wrapper the guard can walk through (recipes are names, not command lines — unlike `sudo` or `docker run`). The clause "anything the `justfile` shells out to" acknowledges the problem and then prescribes the one remedy that does not work.

The two reasonable resolutions produce opposite observable behavior: `Bash(just:*)` broadly allowed means any publishing recipe runs ungated (root §7 explicitly contemplates dev-namespace publishes, which rule 9 gates); `ask Bash(just:*)` means a prompt on every `just check` in the development loop, which is what the whole broad-allow-plus-narrow-hook design exists to avoid.

*Direction:* decide the invariant here rather than leaving it to step `001` — e.g. the justfile contains no gated act at all (publishing belongs to CI per root §8), stated as a rule the guard's `CASES` or the governance family can assert; or `just` gets an explicit registry treatment. Either way the prompt should say which, since the implementer cannot discover the hole from the guard's own docstring.

### Finding 3 — important — Rule 2 probes: the "does `CLAUDE.md` reach a subagent" probe has no pre-committed unfavorable branch, and every reviewer agent's boundary rests on it

Rule 2: "whether `CLAUDE.md` reaches a subagent's context at all, at step `002` … **every reviewer agent's boundary rests on it**." Three agent templates (`step-reviewer`, `state-reviewer`, `code-reviewer` by omission) instruct: "The gated set is **not** a placeholder: cite rule 9 rather than restating it … a probe confirmed `CLAUDE.md` reaches every subagent's context" — asserting the earlier project's result as settled, which biases instantiation toward the citation form.

If the re-probe fails, nothing says what to do, and the failure is silent by construction: the agents' bodies would cite a rule 9 that is not in their context, and a subagent with `Bash` and no boundary text is precisely the shape the templates exist to prevent. Contrast the `.claude/rules/` probe two paragraphs later, which *does* carry its fallback ("If it does not load, the fallback is a `.claude/docs/` file with its read-trigger in `CLAUDE.md`").

*Direction:* give this probe a pre-committed response the same way — e.g. an unfavorable result means each agent carries an inlined boundary block with a stated single-source-of-truth cost, logged as a decision — and soften the templates' "a probe confirmed" to "a probe in an earlier project confirmed; re-probe here".

### Finding 4 — important — `approve-step.md`: the template realizes the close-ritual track hazard the prompt names, and carries no marker for the fix

Rule 3 calls this out explicitly as "the one exception, and it is the one that fails silently": close rituals must key on the track of the **step just closed**, "named explicitly by the close ritual, never on the pointer: the close ritual advances that pointer before it fires them, so at a cross-track milestone boundary resolve-at-invocation would aim both passes at the wrong track, and a state reviewer reading the wrong track's plan reports nothing wrong."

`approve-step.md` does exactly that ordering — step 3 writes "`CLAUDE.md`'s 'Current state' pointed at the next step", then step 5 spawns `state-reviewer` and `optimize-memory` — and says nothing anywhere about which track those two receive. Its header section enumerates its placeholders (`{{PLAN}}`, `{{STEP_ID}}`, `{{CHECK_COMMAND}}`) and its `state-reviewer`/`optimize-memory` fallback wiring in detail, but not this. The implementer is left to apply a general clause ("Where a template's own enumeration of a routine is narrower than the rule it claims to execute, the rule wins") to a subtlety the template gives no hook for. `optimize-memory`'s own header, by contrast, does carry the track note ("in a multi-track repository this agent is invoked for one track and edits that track's files") — so the asset set is inconsistent on precisely this point.

*Direction:* add the instruction to `approve-step.md`'s header (or its step 5) — the closing track is named explicitly at spawn — so the artifact that ships carries the rule, not just the prompt that is consumed once.

### Finding 5 — important — Lines 761–769: nothing verifies that the foundation steps carry the prompt's prescriptions, and the cold reviewer is structurally barred from checking

The prompt requires: "the four foundation entries carry this prompt's per-step prescriptions **in full** — the permission classifier and its traps, the probe duties, the CI reuse rule and its prerequisites, the instantiation list with rule 3's governance-placeholder semantics … this prompt is consumed once at bootstrap, and a session resuming onto the plan must find that detail in the plan, not remember it."

This is the single highest-stakes transcription in the bootstrap — everything the prompt says about steps `001`–`003` survives only if it lands in `PLAN.md`. Yet the cold reviewer's seven criteria (coverage, ordering, granularity, proportion, prerequisites, consistency, premises) contain nothing about it, and the reviewer *cannot* check it: it is forbidden from reading anything under `.claude/spec-work/`, which is where the prompt lives. The only check left is the operator reading four plan entries against a 974-line prompt by hand — and a dropped clause is invisible, not wrong.

*Direction:* add a second, deliberately non-cold pass whose only job is transcription fidelity (it may read `PROMPT.md`; it judges nothing else), or make the four foundation entries' required content an explicit checklist in the prompt that the implementer must tick off in its handover message.

### Finding 6 — important — "Your first task" is one ungated unit, against the prompt's own reasoning for splitting the foundation

The first task is: read two specifications (~1,240 lines), write six files including two plans that must map every section of both documents and every open fact individually, write a `CLAUDE.md` restating eleven dense rules with rule 9's enumeration carried whole inside a ~180-line budget, commit, spawn and brief a cold reviewer, triage its findings, apply and commit the accepted ones, and only then present.

The prompt justifies splitting the foundation into four steps with: "a foundation delivered whole arrives with everything already written, and my first correction then costs the lot." That argument applies with more force here — this is the largest single unit in the document, it precedes any harness, and a structural correction (wrong track split, wrong granularity, wrong milestone grouping) invalidates the plans, the review and the triage together. The prompt also instructs its own reviewer that "'this step is too big to judge in one gate' is one of the most valuable findings this review can return" and that "No step is exempt" — while exempting the step that produces the reviewer.

*Direction:* consider a gate between the six files and the cold review (the operator rules on plan *structure* before a reviewer spends a round on plan *content*), or state explicitly why this unit is exempt from the argument the foundation split rests on.

### Finding 7 — minor — Rule 9: a locally-run PZ server performs an outward write the boundary does not classify

Rule 9 rules the development loop "free end to end, local writes included: building images locally; starting, stopping, exec-ing into, reading the logs of … *this project's own* containers", and separately rules free "anonymous steamcmd downloads and Steam metadata/buildid queries" — all Steam **reads**.

But PZ §2 states both UDP ports are "**advertised** in the root §5.2 sense (Steam server browser registration)", and root §8's smoke test starts the image "on the image's **default configuration profile**". Running that locally registers the operator's server with Valve's master server — an outward write to shared state (a public listing), not a read, and not on either side of the enumeration. It is low-blast-radius (delisted on stop) but it is exactly the class the boundary exists to enumerate, and the implementer will do it dozens of times.

*Direction:* classify it explicitly — free with a note, or run the default local smoke profile with Steam integration disabled (PZ §6 makes that a supported profile) — rather than leaving it unexamined.

### Finding 8 — minor — Rule 2: the governance well-formedness family mandates a bespoke check, which rule 11 and rule 2's own wording elsewhere argue against

Rule 2 declares two families that "belong on that list whatever the stack", the first being "**Governance well-formedness:** your instantiated tooling under `.claude/skills/` and `.claude/agents/`, and `.claude/settings.json` — their frontmatter and JSON must parse."

`.claude/settings.json` is covered by a standard pre-commit hook (`check-json`). YAML frontmatter inside `.md` files is not: there is no standard ecosystem tool for it, so this clause mandates a small custom script — and the prompt's own test for this is stated one paragraph later ("once mandated by a rule it cannot be deleted without amending the rule") and again in rule 11 ("Before writing a runner, an installer, a discovery library or a test driver, ask whether the ecosystem already ships one"). The clause is self-aware about scope ("Those two parse checks are cheap and exact, and they are the whole of what this rule requires") but not about the tool question.

*Direction:* either name a standard mechanism, or say plainly that this one family is a sanctioned few-line custom check and why, so it does not read as an accidental exception to rule 11.

### Finding 9 — minor — `step-000` deliverables vs rule 2's "never ahead of it"

Rule 2 is emphatic: "a family arrives **with the first file of its class, in the step that lands it**, never ahead of it: a check family (and its fixtures) for an artifact the repository does not yet contain is scaffolding, not coverage." But `step-000` is described as delivering "pinned base dependencies installable through one documented setup command" and "the check/test/verify harness of rule 2, built on the tools named there" — where "the tools named there" include Dockerfile lint and GitHub Actions workflow validation, for artifacts that do not exist until much later steps.

Two reasonable implementations diverge observably: one pins and configures hadolint/actionlint at `000`, one adds each with its first artifact. The operator's `step-000` test ("a fresh clone, the setup command, the check command, one commit — all green") looks different in each.

*Direction:* make `step-000`'s scope explicit — the harness *skeleton* plus only the families whose artifacts exist at `000` (markdown/prose, JSON) — so the "never ahead of it" rule and the step's deliverable list cannot be read against each other.

### Finding 10 — minor — `optimize-memory.md` is the only writing agent with no action-boundary paragraph

`step-reviewer`, `state-reviewer` and `code-reviewer` each carry the same block: "**everything rule 9 merely *gates* is, for you, forbidden outright.** The gate is the operator's authorisation in an exchange, and a subagent has no exchange to be gated in." `optimize-memory` — which has `tools: Read, Bash, Edit, Write`, the broadest tool set of the five agents — carries no equivalent. Its only constraint is "you never commit". The prompt says nothing about the asymmetry.

*Direction:* carry the same paragraph in `optimize-memory.md`, or state in the prompt why an editing agent needs it less than a read-only one.

### Finding 11 — minor — Rule 2's language-lint clause does not reach `bash_guard.py`

"Lint for the language the entrypoints and tooling are implemented in, **whichever you choose** — the specification deliberately does not choose one." But `bash_guard.py` is Python regardless of what the implementer chooses for entrypoints, and it is 2,000 lines of the repository's most load-bearing tooling. If the entrypoints are shell, a reasonable implementer reads this clause as "shell lint" and covers the guard only by the catch-all ("Every artifact class the repository ships gets a family"). The guard's own docstring also imposes a config obligation this clause does not anticipate: "This file is written at 88 columns … A project whose lint is narrower exempts the width rule for this path alone … (With pre-commit, the exemption also needs `force-exclude`.)"

*Direction:* name Python explicitly as a family the repository ships whatever the entrypoint language, and carry the guard's width exemption forward as a known config item of step `001`.

### Finding 12 — minor — "the first agent you spawn" is ambiguous at bootstrap

Rule 2 pins the subagent-context probe to step `002`: "that one costs one exchange with the first agent you spawn ('quote rule 9's opening line')". Literally, the first agent the implementer spawns is the bootstrap cold reviewer, in this very session — which is explicitly told to read only the specs and the six files, and whose context the probe would contaminate.

*Direction:* say "the first agent you spawn *in step 002*".

---

## 3. Questions for the operator

1. **Rule 1's escalation list vs the spec's pre-committed branches** (Finding 1): when PZ item (i) or (d) resolves unfavorably along the path the specification itself pre-committed, do you want to be asked, or is the pre-commitment your consent?
2. **Runner capacity for the smoke test.** Root §8 gates every game-image publish on building and starting a multi-gigabyte PZ image. GitHub-hosted `ubuntu-latest` runners ship roughly 14 GB of free disk. Neither the specification nor the prompt names this; if it forces a self-hosted runner or a disk-reclaim step, that is an external prerequisite the prompt's list is missing. Is this something you have already sized?
3. **Repository visibility at creation.** The prompt lists "the GitHub repository, its remote, and my authorisation of the first push" but never says the repository must be created **public** — which root §1, §2.6, §2.8 and §7 all depend on (free GHCR, anonymous pulls, and the 60-day idle-schedule disabling that §8's staleness check exists to survive). Deliberate omission or oversight?
4. **`just` and the guard** (Finding 2): do you intend the justfile to contain any recipe that publishes, pushes, or writes to GitHub? If no, saying so in the prompt closes the hole for free.
5. **The `.claude/spec-work/handoff/assets/` deletion.** Once the last template is adopted or dropped, the prompt orders the directory deleted along with every pointer to it. That leaves `PROMPT.md`, `decisions.md`, `external-review-prompt.md` and `reviews/` in the tree, permanently unreadable by any session and permanently excluded from the harness. Is keeping them tracked intended, or should the whole `spec-work` tree eventually leave the working repository?
6. **`CLAUDE.md`'s 180-line target.** By my count the mandated contents — eleven rules, layout, track map, `Current state` with its closed item list, the session routine and its pre-`002` fallback, the plan-entry shapes, the boundary-crossing-cost rule, the governance-placeholder semantics with the close-ritual exception, the assets block, and rule 9's ~30-line enumeration carried whole — sit close to or above the cap on arrival. The prompt anticipates this and offers a project-specific budget as a logged deviation. Do you expect that deviation at bootstrap, or should something on the list move to `.claude/docs/` from the start?

---

## 4. Verdict

6 important, 6 minor, 0 blocking. Not a quiet round: the handoff is unusually well-constructed and self-aware — its rule collisions are mostly named and ordered, its cold-start references are guarded, and its asset templates carry their own doctrine — but Findings 1 through 6 are each a place where the prompt states a stake and then leaves the response, the check, or the resolution unwritten.
