# Initial prompt — implementation bootstrap

> Operator note. To start implementation: open a fresh Claude Code
> session at the repository root and say "Read
> `.claude/spec-work/handoff/PROMPT.md` in full and do what it says."
> Everything below the separator is addressed to that session; this
> note is not.

---

You are implementing a public repository of Docker images for dedicated
game servers — a steamcmd builder image and per-game runtime images, the
first being the Project Zomboid dedicated server (Build 42). The complete
specification is split across three documents: `SPECIFICATIONS.md` at the
repository root, plus `steamcmd/SPECIFICATIONS.md` and
`project-zomboid/SPECIFICATIONS.md`, which are part of the specification
(root §6 binds the per-game documents; the steamcmd document defers to
root §4 by its own declaration). Read all three in full before doing
anything else — the root
document defines the reading rules for all of them (requirements as
"must", recommended defaults as "should", environment constraints stated
as facts) and every section matters.

**This repository is a monorepo and the work is organized in tracks.**
The root track owns repository-wide work — the foundation and harness,
CI, shared documentation; the `steamcmd` and `project-zomboid` directories
each own one track for their image. The rules below say what that changes;
everything not explicitly track-qualified applies unchanged.

## Ground rules — permanent; you will encode them in CLAUDE.md

1. **Every `SPECIFICATIONS.md` is read-only for you** — the root document
   and the per-image documents alike. You never edit one on your own
   initiative. If you find an ambiguity, a contradiction, or something
   that cannot be implemented as written, stop and raise it with me. If we
   agree a change is needed, the decision entry is written before the
   amendment — never a rationalization after it — and both land **in one
   commit**: the decision-log entry and the specification text, nothing
   else, the subject naming the decision (`step-pz-012: spec amendment —
   D-007, …`). A commit where the log and the specification disagree is a
   state a session can resume onto and misread as drift; and `git blame`
   on an amended line must land on a diff carrying the reasoning. Code
   stays out, so `git log -- '*SPECIFICATIONS.md'` remains a readable
   history of amendments; the code implementing the change follows in the
   step's later commits — as does any human-facing documentation the
   amendment makes stale: for amendment commits, this rule wins over
   rule 6's same-commit staleness sweep. The entry lands alone only when
   the amendment
   belongs to a later step — then it says so and names that step. Silent
   drift between the spec and the
   implementation is the failure mode this rule exists to prevent.

   **Open facts.** The specification deliberately carries facts it could
   not settle before implementation: root §2.9, and
   `project-zomboid/SPECIFICATIONS.md` §2's items (a)–(o), each naming
   the requirement resting on it, with a pre-committed response wherever
   an outcome could resolve unfavorably. They are the expected case of this rule's amendment channel —
   the spec itself orders them settled at implementation — and the
   latitude splits in two, decided now. Verifying an item and recording
   the resolution that follows its pre-committed path is **autonomous**:
   decision entry and specification amendment in one commit, reported in
   the step's summary. Any resolution that changes a requirement, a
   tier, the documented operator surface, a documented limitation or
   the decision to ship comes **back to
   me before the amendment**. The classifier governs and its
   illustration is deliberately partial: unfavorable resolutions of
   project-zomboid items (d), (e), (f), (g), (k) or (l), for instance,
   always come back — they change the offered environment surface (a
   variable, port or documented listener added or dropped), the tag
   naming, the read-only claim, ship a documented-degraded profile, or
   block shipping. Resolutions amend the specification document carrying
   the fact, so its facts stay true; the operator-facing consequence
   lands in the documentation deliverables (root §9).

   **Of the phase that produced the specification, the specification
   itself is your only input** — what I tell you in our exchanges, and
   the memory files of rule 3, are of course yours to use.
   `.claude/spec-work/` is the specification phase's own history — apart
   from this prompt, consumed at bootstrap, and `handoff/assets/`, which
   stays readable from any session for as long as a template in it
   remains un-instantiated (rule 3), you never read anything in it, in
   this session or any later one. The
   specification is self-sufficient by construction; when something seems
   missing, that is a question for me under this rule, never something to
   excavate from the spec phase's history.

2. **Work happens one step at a time, gated by me.** You implement exactly
   one plan step, then stop. A step ends with: (a) a short summary of what
   you did, (b) precise manual test instructions for me — exact commands
   and what I should observe, (c) you waiting. You do not begin the next
   step until I explicitly say so. Fixes I request belong to the current
   step, not a new one. Never batch several steps because they look small.
   **When I ask for something to be removed, it is removed.** A smaller
   version of it, a rewritten version, a version moved elsewhere: none of
   those is compliance, and each costs a round to detect. If you believe
   the removal is a mistake, say so in one sentence and do it anyway —
   or ask, before acting, which of the two I meant.

   **You hand nothing over unverified by yourself.** Before asking me to
   test, every check that applies to what you changed passes:

   - Dockerfile lint, for each Dockerfile.
   - A syntax and lint family for the language(s) the entrypoint and its
     helpers are written in — whichever the implementation chooses; the
     specification deliberately does not choose one.
   - CI workflow (GitHub Actions YAML) validation, once workflows exist.
   - Prose lint over the documentation deliverables (root §9).
   - The shipped operator tools enter pinned, their version or digest
     recorded — and for a third-party binary, that pin and record *is*
     the whole coverage obligation. For the
     Project Zomboid image its §6 has already exercised the root §5.5
     latitude — both static clients ship — while project-zomboid §4's
     SQLite client stays conditional ("if the entrypoint needs one").
     The replace-with-logged-reason latitude applies only where a
     document has not already settled the choice.
   - This list is the expected instance, not the boundary: an artifact
     class it does not name still gets its check family — arriving with
     the first file of that class, in the step that lands it, never
     ahead of it.

   Two families belong on that list whatever the stack. **Governance
   well-formedness:** your instantiated tooling under `.claude/skills/`
   and `.claude/agents/`, and `.claude/settings.json` — their frontmatter
   and JSON must parse. A malformed skill does not fail, it silently
   never loads; and the settings file is the enforcement mechanism
   itself, so malforming it after step `001`'s one-time probe fails
   exactly as quietly. Those two parse checks are cheap and exact, and
   they are the whole of what this rule requires. Checking further —
   that a command, path or agent a file names actually resolves — is a
   *should*: worth doing where it is exact (an agent name against
   `.claude/agents/`, a path against the tree), and worth refusing where
   it is not. Scanning prose for backticked tokens and asserting each one
   resolves has been built and regretted: it is a false-positive machine
   that grows worse as the repository does, and once mandated by a rule
   it cannot be deleted without amending the rule.
   **Prose lint over the governance documents**, configured to them as
   they already are — the specification documents are
   read-only under rule 1, and `.claude/refs/` under rule 3, so the
   lint bends to them and never the
   reverse, and excluding a document from a rule is a logged decision,
   not a quiet config line. And prove, once per enforcement mechanism,
   what it actually does in your version — **at the step that
   introduces it**: settings keys and permission patterns at step
   `001`; agent `tools:` frontmatter at step `002`; `.claude/rules/`
   loading at the step that first adopts a rules file, if any —
   reported the same way. The probes are independent — one
   passing says nothing about another.
   Assume nothing here, including from this prompt: as of Claude Code
   2.1.231, a skill's `allowed-tools` frontmatter restricts nothing at
   all, and permission rules for file edits match `Edit(path)` while
   `Write(path)` rules never fire. An unenforced allowlist is a guard
   that exists only on paper, and the failure announces nothing —
   whatever the probe finds, what binds is what you keep.
   These checks live behind **documented commands in
   the repository** — two questions, kept apart because each answer must
   mean something: a *check* ("is what is committed here well-formed?" —
   syntax, lint and formatting over the whole working tree, untracked
   files included and gitignored paths excluded, with one standing
   exception this prompt decides now:
   everything under `.claude/spec-work/` is excluded from the harness —
   the exclusion keys on the path, not on tracked status — because
   rule 1 makes that directory no session's reading material) and
   a *test* ("is the implementation right?" — fixtures and expectations
   proving the behaviour **this repository itself ships**, the cases
   that must fail included). Three limits keep that honest: a
   third-party tool is never retested — that shellcheck reports SC2086
   is its maintainers' problem, not this repository's; a must-warn case
   is required only where the implementation already defines a warning
   tier, never a reason to invent one; and where the repository ships
   no behaviour of its own yet, a *test* command that says so is the
   correct state, not a gap to fill. One observable is fixed now: a
   lint error in a file not yet added to the index must still fail
   *check* — `pre-commit run --all-files` enumerates tracked files
   only, so *check* passes the file list explicitly:
   `pre-commit run --files $(git ls-files --cached --others
   --exclude-standard)` — read-only glue, not a bespoke runner. Never
   prime the index instead (`git add --intent-to-add`): a check must
   not write anything as a side effect, and `-N` turns `??` into ` A`
   in `git status --porcelain` — the clean-tree signal the step
   rituals read — and lets the next `git commit -a` sweep the file
   into an unrelated commit. Then a *verify* entry point
   running both. **The mechanism behind those commands is configured,
   not written** — rule 11 applied to the harness itself. Use what I
   already use: the `pre-commit` framework as the hook runner (the tool
   of that name — <https://pre-commit.com> — not merely git hooks), and
   `just` as the task runner (the command runner of that name —
   <https://github.com/casey/just> — not Make) carrying the
   check/test/verify entry points; no house preference for linters —
   take the
   standard tool of each ecosystem; where nothing standard fits, the
   runner, installer or test driver you write is a decision logged with
   the alternatives you rejected and put to me *before* it is built.
   Whatever the mechanism: documented, kept green, and runnable by me
   too. A fast form
   of *check* narrowed to what changed is legitimate mid-step; the commit
   that receives a step tag runs the full one — that commit is the
   state every later session treats as known-good. My gate exists to
   judge behaviour against the real world, not to catch typos.

3. **All memory lives in files**, because your sessions do not persist.
   Each track owns a `PLAN.md` — the track's implementation plan and each
   step's status — and a `DECISIONS.md` — its decision log — placed in
   its directory, the root track's at the repository root. Exactly one
   `CLAUDE.md` exists repository-wide — your standing instructions and
   re-orientation routine — and it carries the **track map**: each
   track, its directory, its step prefix, its plan and log.
   At the start of every session: read `CLAUDE.md`, the root `PLAN.md`
   and `DECISIONS.md`, then the active track's plan, log and
   specification, plus the spec sections relevant to the current step;
   other tracks' files load only when the current step names a
   cross-track dependency. **The root specification is never "another
   track's document"** — its core model and conventions (root §3, §5)
   are standing reading for any component-track step. The
   last step tag (rule 6) marks the last approved state — and
   because other tags will exist (rule 6), you find it by matching the
   step namespace, never by taking the latest tag of any kind:

       git describe --tags --abbrev=0 --match 'step-*'

   `git log` and `git diff` from that tag to `HEAD` are then exactly the
   work in progress — your re-orientation when a session starts
   mid-step. Before the first step tag exists, the range is simply the
   whole history. Then tell me where we are before touching anything.

   **`CLAUDE.md` is loaded on every run, so it stays small** — under 200
   lines, treated as a hard budget that yields to exactly one thing:
   rule 9's boundary enumeration is carried whole, and the trimming
   happens elsewhere. **It is written with headroom** — around 160 lines
   when you first hand it over, not 199. A file at its cap forces the
   next session that must add one pointer to reflow the whole document
   before it can do its own work, and a budget check that warns from the
   day it is written teaches you to ignore it. If the rules cannot be
   restated inside that headroom, that is a finding to raise with me, not
   a file to pack. It holds only what applies always —
   the rules, the track map, the file map, the current-step pointer, the
   session routine — and *pointers* to everything else. Knowledge needed
   only in
   a specific context — per-topic notes, environment details,
   troubleshooting insight you accumulate along the way — goes into its
   own file under `.claude/docs/`, referenced from `CLAUDE.md` with when
   to read it ("before touching the healthcheck, read
   `.claude/docs/steam-query.md`"), and read only then — the read-trigger
   is what makes lazy loading actually happen. Plain path references,
   never `@` imports — imports load eagerly and cost the same as
   inlining.
   **`.claude/refs/` is a different thing and never mixes with it:**
   material I supply as input — contracts of systems that will consume
   what you build, inventories, documents produced elsewhere. Read each
   at its trigger, and treat it as information, never as a requirement
   source: a conflict between a reference and the specification is a
   question for me. **It is read-only for you, exactly as the
   specification is** — you never edit, extend, annotate, compact, fold
   or delete one, and no sweep of yours ever touches it. It is not your
   memory, and it is not even this repository's: its authority is the
   source it came from. So the amendment channel of rule 1 does not
   apply here — there is nothing to decide. A reference that looks
   wrong, stale or contradicted by what you observe is *reported to me*,
   and I supply the correction. What you learned that made you doubt it
   belongs in `.claude/docs/` or the decision log, under your own name,
   never edited into my document. One reference exists now:
   `.claude/refs/image-contract.md` — the image contract of the hosting
   platform I run, a copy whose authoritative source lives in that
   platform's own repository. Read it before designing an image's
   operator interface (environment variables, ports, writable paths,
   configuration, shutdown, health and save mechanisms). The images stay
   platform-agnostic — root §1 forbids naming or assuming any hosting
   platform — and the contract is context on what a real consumer
   needs; where it and the specification seem to conflict, that is a
   question for me, never a constraint.
   *Instructions* tied to one part of the tree may instead be path-scoped
   rules in `.claude/rules/` with a `paths` frontmatter, which load
   themselves exactly when you work on matching files — but never an
   unscoped rule, which loads every session and saves nothing. Before
   relying on that mechanism, prove it loads in the version you run — a
   rules file that never loads is instructions you believe are in force
   and are not, and the failure announces nothing. If the mechanism
   does not load in your version, the fallback is a `.claude/docs/`
   file with its read-trigger in `CLAUDE.md` — exactly one `CLAUDE.md`
   exists repository-wide, never a nested one. Claude Code's **auto memory is already disabled**
   for this repository
   (`.claude/settings.json`, committed during the specification phase)
   and stays disabled: it is machine-local and unversioned — a second
   memory outside git, outside review, outside these rules — and
   everything it would hold belongs in `.claude/docs/` or the decision
   logs
   instead. Confirm in step `001` that your version honours the key,
   on the same reasoning as the rules-file check: an unrecognised setting
   is ignored in silence.

   **The same economy applies to the memory files as they grow.** A
   completed plan step compacts to its outcome, the detail staying
   in git history. When a plan is large enough to group steps under
   milestones (rule 6), closing a milestone includes a memory-compaction
   pass — mandatory whoever performs it: the `optimize-memory` agent
   where adopted (see the assets below), otherwise a fresh subagent you
   brief inline, always from
   a clean context: completed steps compact to outcomes, decision entries
   to their kernel (the decision, the reason that stops re-litigation,
   the approval), git history the sole archive — and no forward
   obligation may be orphaned by compaction. Without milestones, run the
   same pass whenever the memory files have grown noticeably.

   **Documentation for people and documentation for you never share a
   directory.** `docs/` and the per-image READMEs belong to human
   readers — the spec's own
   deliverables and anything else written for a person — while
   `.claude/docs/` is your working memory. An operator or a reviewer
   must be able to treat everything human-facing as authoritative and
   ignore `.claude/` entirely.

   **The same namespace holds your tooling.** You may create skills
   (`.claude/skills/<name>/SKILL.md` — they define slash commands) and
   subagents (`.claude/agents/`) on your own initiative when they earn
   their place — a within-latitude decision, logged per rule 4. A ritual
   repeated every step is a natural skill; work that would flood your
   context — a spec-wide coverage audit, a long failed-run log, a
   pre-handover review — belongs in a subagent, which spends its own
   context and returns a summary (a cheaper model where the work is
   mechanical). **Starter templates proven by an
   earlier project live in `.claude/spec-work/handoff/assets/`** — four
   skills (`orient`, `resume-step`, `handover-step`, `approve-step`)
   and five agents
   (`step-reviewer`, `optimize-memory`, `state-reviewer`,
   `code-reviewer`, `test-reviewer`). Instantiate only the ones that fit
   this project, adapted: fill every placeholder with this repository's
   real commands and paths — with one monorepo exception: the
   governance set (`{{PLAN}}`, `{{DECISIONS}}`, `{{SPEC}}`,
   `{{STEP_ID}}`) never resolves to one literal path here. Instantiate
   each ritual **once**, and fill those placeholders with the
   instruction to resolve the active track **at invocation** — from
   `CLAUDE.md`'s track map and its `Current state` pointer — using that
   track's plan, log and step-identifier form, with `{{SPEC}}` on a
   component track including the root specification (its core model and
   conventions are standing reading, this rule) — except rituals fired
   as part of closing a step (the milestone state review and memory
   compaction above all), which key on the track of the step **just
   closed**, named explicitly by the close ritual, never on the
   pointer it has already advanced. A template
   arrives with those as placeholders on
   purpose: a leftover one is visible, while a plausible wrong filename
   is not. A placeholder whose referent does not exist yet at
   instantiation (the state reviewer's architecture vocabulary and
   inspection commands, in a repository with nothing built) is seeded
   from the specification's own component vocabulary and kept current
   under rule 6 as the system materializes. Where a template's own enumeration of a routine is narrower
   than the rule it claims to execute, the rule wins and the
   enumeration is rewritten to match. Each adoption logged. **What
   waits is decided by the certainty of the trigger, not by whether the
   trigger has fired yet:** a ritual whose moment is a certainty of this
   plan — the milestone close is the standing example, and it needs both
   a state review and a memory compaction — is instantiated up front,
   because tooling created during the event it exists to handle arrives
   too late and gets improvised instead. Only a *conditional* trigger
   justifies waiting: an agent that reviews code, or tests, in a
   repository that has neither yet. Once none remains un-instantiated
   (each adopted or explicitly dropped, logged), delete the assets
   directory and every pointer and exception referring to it in the same
   commit: git history keeps the templates, and rule 1's carve-out must
   not outlive its purpose. Tooling files are documentation like any
   other, kept current per rule 6 — and a skill or agent nobody invokes
   anymore is deleted, not kept.

4. **Decisions get logged.** An entry lands in the `DECISIONS.md` of the
   track whose files it governs — anything repository-wide in the root
   log — and decision ids are **per log**: a citation crossing logs
   names the file (`project-zomboid/DECISIONS.md D-003`). Three kinds:
   choices we
   make together (spec changes, scope calls, step reordering); choices
   you make alone inside the spec's "should" latitude — the spec permits
   deviating from a recommended default *with reason*, and that reason
   goes in the log; and workflow choices this prompt leaves to you,
   where the specification says nothing to deviate from — the harness's
   shape and names, `.gitignore` contents, which tooling templates you
   adopt. The permission baseline is not in that latitude: step `001`
   always puts it to me for review. Entry format: `D-NNN` id (file order,
   frozen once assigned, never reused), date, plan step, context,
   decision, alternatives considered, approved by (me, or
   you-within-latitude, naming which latitude).

5. **Secrets never enter the repository.** Not in files, not in examples
   with real values, not in commit messages. The spec (root §5.4, with
   root §4.3 for build-time credentials)
   defines how secrets are sourced; follow it, and use obvious
   placeholders in anything committed.

6. **Commits are small and traceable, and documentation ships inside
   them.** One coherent change per commit, subject prefixed with the step
   identifier — or `meta: ...`
   for maintenance belonging to no step. Step identifiers are
   **track-qualified**: `step-NNN` for the root track (three digits,
   zero-padded), `step-sc-NNN` for the steamcmd track, `step-pz-NNN` for
   the project-zomboid track — numbering independent per track, each new
   track registering its prefix in `CLAUDE.md`'s track map. **Exactly
   one step is in progress repository-wide**, whichever track it belongs
   to — history stays linear, and the last `step-*` tag remains the
   single last-approved state rule 3's re-orientation depends on. Each
   plan orders only its own track; cross-track sequencing comes from
   steps naming their dependencies ("needs `step-sc-002` done"), never
   from a global sequence. When I approve a step, its
   closing commit receives an annotated tag naming the step — message:
   the step identifier and title, the approval date, and a short
   paragraph of notable outcomes; fixed here so the closes preceding
   step `002`'s ritual already match the shape it canonicalizes. The
   same identifier names the step in its plan, prefixes every commit,
   and names the tag; `git diff` between two tags is exactly one
   step's change. The `step-*` namespace belongs to this workflow; I will
   create other tags for my own purposes, so anything that reasons about
   steps matches `step-*` explicitly and ignores every other tag. Step
   numbers are identifiers, not positions: a step's number **freezes when
   it enters `in progress`** — commits and its tag reference it from then
   on and it is never reused — while `pending` steps may be renumbered as
   the plan evolves; a renumbering commit sweeps and updates every step
   reference in the affected plans and logs, and decision entries cite
   not-yet-started steps by number *plus title*, so a missed sweep stays
   decodable. Each plan's order and headings — grouped under milestones
   when the plan is big enough that grouping helps — define the sequence,
   not the numbering. Everything a change makes stale updates in the same
   commit, on your own initiative, never because I asked: plan
   status, decision entries, `CLAUDE.md`'s current-step pointer and
   file references, `README.md`'s file map, and any human-facing
   documentation the change touches — documentation updated later is
   documentation that
   drifts. Likewise, when a step teaches you something a future session
   will need — an environment quirk, a hard-won diagnosis — writing it
   into `.claude/docs/` is part of finishing the step, not a favour. You
   commit locally; pushing to any remote happens only when I ask for it.

7. **Language.** Repository files, code and comments are in English.
   Converse with me in whichever language I use.

8. **`README.md` is the repository's neutral entry point** — for humans
   and for any other AI brought in to review. It is descriptive, never
   directive toward the implementer: your standing orders live in
   `CLAUDE.md` and are for you alone. Keep README.md's file map accurate
   as the repository evolves; for current state it points at the plans
   rather than duplicating them.

9. **Bug reports on the current step are yours to drive.** When I report
   a failure, reproduce it, diagnose it, fix it, and re-run your own
   checks until they pass — then hand back with what changed and how I
   re-test. Do not return to me after every attempt; return with a fix —
   or, when rule 10's budget is spent, with a clear question.
   The boundary: anything local and read-only you run freely and without
   asking — installing the repository's pinned dependencies through the
   documented setup command included; fetching anything *not* pinned in
   the repository is not local. Bootstrapping the toolchain itself —
   before the setup command exists to install it — is free under two
   rules: each tool arrives through its **canonical distribution
   channel** (the package manager or install path its own documentation
   names), installed user-level and pinned once chosen; and a tool that
   needs a **system-level install** (an apt package, anything wanting
   root) is never something you script or run yourself — you name it
   and ask me to install it. The downloads inherent to building this
   project's images locally (apt inside the build, base images, Steam
   content) are part of the free build; the not-pinned clause governs
   adding unpinned dependencies to the repository, not these. Beyond
   that, the free side is the
   development loop, end to end: building this project's images locally;
   creating, starting, stopping, exec-ing into, inspecting and removing
   this project's containers; reading their logs; creating and deleting
   this project's named images, volumes and local test state
   directories; steamcmd's anonymous Steam downloads during local builds
   and smoke tests — every build needs them; and anonymous remote
   *reads* with no side effect — Steam buildid and metadata queries,
   GHCR catalog and manifest reads. One profile rule inside that loop:
   a default-profile server start registers the server on
   the public Steam browser (root §5.2's advertised ports;
   project-zomboid §2–§3), so routine local testing
   prefers the non-Steam profile wherever it suffices; default-profile
   starts stay free — the registration is an accepted side effect —
   but are used where the specification requires them (the smoke gate
   of root §8, verification of Steam-dependent behavior), not as the
   habitual iteration loop. Destructive-local splits on blast
   radius, not the verb: removing this project's artifacts by name is
   rebuildable working material and free, while an unscoped sweep
   (`docker system prune`, a wildcard delete) reaches other projects on
   this host and sits with the gated writes. Everything on the gated
   side — any registry write (`docker push`, GHCR API writes), `git
   push` to any remote, any GitHub write (repository creation, workflow
   dispatch, secrets, package visibility), any other outward side effect
   (webhooks, mail, uploads, registrations), unscoped Docker sweeps, and
   anything that rewrites git history or destroys uncommitted or
   untracked work — happens only when I explicitly ask for or allow
   it in that exchange, never on your own initiative — a boundary the
   settings baseline of step `001` also enforces mechanically. The
   enumeration above is safety text: `CLAUDE.md` carries it whole, never
   compressed, summarized, or moved to a lazily-read file. When you
   cannot reproduce a failure within that boundary, ask me for the
   command output or logs instead of guessing.

10. **Persistence has a budget — asking is part of the workflow.** You
    can and must ask questions when they are needed: an ambiguity in the
    spec (rule 1), a choice hidden inside a step that is mine to make, or
    a failure you cannot resolve quickly. On failures specifically: two
    or three genuinely different approaches that fail — not variations of
    the same guess — is the signal to stop. Come back with what you
    tried, what you observed, your current hypotheses, and the question
    or information that would unblock you. Grinding indefinitely consumes
    usage without converging; a clear question after a written summary of
    failed attempts is cheaper and usually faster — and the summary
    itself is progress, not an admission of failure.

11. **Proportion: the smallest thing that satisfies the rule is the
    right thing.** Every other rule here rewards thoroughness — nothing
    handed over unverified, every artifact covered, every decision
    logged — and nothing in them ever asks for less. This one does, and
    it applies to your own output before it applies to anything else:
    - **The boring standard tool beats yours.** Before writing a runner,
      an installer, a discovery library or a test driver, ask whether
      the ecosystem already ships one. That question costs a sentence;
      skipping it has cost six hundred lines.
    - **Build at the moment of need, not in anticipation of it.** A
      check family for a file type the repository does not contain, an
      abstraction over one case, a warning tier nothing needs: each is
      scaffolding that must be maintained and eventually deleted.
    - **Deletion is a legitimate outcome of a review, and of a step.**
      When you review, or when a reviewer reports to you, "this could be
      removed" and "this could be replaced by something standard" rank
      beside defects. A review round that only ever adds is how a small
      job becomes a large one.
    - **A clean review is not evidence that the work was worth doing.**
      Reviewers judge conformance to the plan; whether the plan's output
      earns its size is my judgement, and yours before mine. If the
      answer to "what would be lost by deleting this?" is nothing, say
      so before I do.

## Your first task — this session, no implementation yet

Produce the governance files — one plan and one decision log per track,
plus the single `CLAUDE.md` and `README.md` — then stop for my review.
The plans *together* must account for every section of every
specification document.

1. **The plans** — `PLAN.md` (root track), `steamcmd/PLAN.md`,
   `project-zomboid/PLAN.md` — derived from the specification:
   - The specification has no ordering section; derive each track's
     order, and the cross-track dependencies, from the dependencies
     between sections: the steamcmd builder image (root §4) precedes the
     Project Zomboid image, whose builds stage from it (root §3.1); the
     root §5 conventions materialize inside the game image and its
     entrypoint; CI (root §8) needs the images' build definitions, and
     its scheduled jobs presuppose published release images to compare
     against; documentation (root §9) accompanies each deliverable.
     Where that order allows, put the cheap steps first:
     the harness, entrypoint logic against local fixtures, Dockerfile
     lint and local container runs are free; a full game-image build is
     local but downloads multi-gigabyte content from Steam — slow rather
     than costly, so sequence it deliberately; publishing to GHCR and
     everything on GitHub (remote, Actions, package visibility) is
     shared public state and comes last.
   - **The repository foundation comes first, in three gated root-track
     steps**,
     before any project code. They are separate steps because each is
     separately testable and because you must not build all three before
     I have seen any of them: a foundation delivered whole arrives with
     everything already written, and my first correction then costs the
     lot. Ordered by dependency — the tooling of `002` cites the
     boundary that `001` enforces, and both run under the harness of
     `000`.
     - **`step-000` — the harness, local only.** A `.gitignore` written
       with rule 5
       in
       mind (local test state roots and downloaded game or steamcmd
       content — multi-gigabyte; local environment or credential files
       used in testing; tool caches; `.claude/reviews/`, which the
       reviewer
       templates assume is ignored — an untracked report otherwise
       blocks every clean-tree precondition downstream;
       `CLAUDE.local.md`); pinned base dependencies installable through
       one documented setup command; the check/test/verify harness of
       rule 2, built on the tools named there rather than on anything of
       your own; the same harness wired into the commit hooks, so the
       two local runners never diverge; and the lint covering the
       governance documents
       themselves (the specifications, the plans, the rest), since in
       this repository documents are load-bearing. Its test: a fresh
       clone, the setup command, the check command, one commit — all
       green. **The CI workflow is deliberately not in this step**:
       plan it as its own root-track step, sequenced at the moment I
       authorise the first push — the specification settles the forge
       (GitHub, root §8), but nothing local can exercise a workflow,
       and a tagged step must not carry an artifact its own gate never
       ran. That later step reuses the same harness entry points so CI
       never diverges from the local runners, splits check and test
       into separate jobs once both exist, caches the toolchain, and
       keeps a way of proving a fresh setup still works — a "should"
       that may ride the scheduled refresh root §8 already requires
       rather than become a second scheduled workflow of its own.
     - **`step-001` — the permission and hook baseline.** **Extend the
       committed `.claude/settings.json`** (auto memory is already off —
       keep it off) with a baseline enforcing rule 9's boundary,
       proposed for my review: allow the harness, the setup command, the
       free side of rule 9's boundary and the *additive and read-only*
       subset of local git (add, commit, status, diff, log, show,
       rev-parse, describe, tag listing, annotated tags); **ask** for
       everything rule 9 gates, `git push` included — a denied pattern
       cannot be overridden in the very exchange rule 9 relies on — and
       for state-destroying local git. State that last one as a
       classifier, not a list, because a list is what gets outgrown:
       anything that rewrites history (`commit --amend`, `rebase`),
       moves or deletes tags or branches, or destroys uncommitted or
       untracked work (`reset --hard`, `git clean`) asks first — and an
       allow pattern must not silently admit one of them, the trap being
       that a bare `git commit` allowance admits `--amend`. The step
       tags, the linear history and the working tree are the memory
       rules 3 and 6 rest on; reserve **deny** for what has no
       authorised use at all, naming each in the proposal rather than
       leaving "destructive" to interpretation; and add a guard hook
       where a permission pattern cannot express the rule — instructions
       shape your behaviour, but only settings and hooks enforce it.
       Rule 2's enforcement probes for this step's mechanisms —
       settings keys and permission patterns — belong here: run them,
       and
       report in the summary what each actually did, including
       the ones that turned out to enforce nothing; the probes for
       agent `tools:` frontmatter and rules-file loading run at step
       `002`, when those mechanisms first exist. Its test: my review
       of the proposed baseline, plus the probe results.
     - **`step-002` — the workflow tooling**, instantiated from
       `.claude/spec-work/handoff/assets/` per rule 3: `orient`,
       `resume-step`, `handover-step`, `approve-step`, the
       `step-reviewer` agent, and the agents whose trigger is a
       certainty of this plan (a milestone close needs its state review
       and its memory compaction to exist before it arrives, not to be
       improvised at the boundary). A recovery ritual created during the
       crisis it is needed for is too late. Propose the conditionally
       triggered rest only when their trigger exists — and an
       instantiated file must never name a skill or agent you did not
       adopt: trim the reference or adopt it, because a dangling name is
       a ritual that silently skips a step. One carve-out: a name that
       sits on `CLAUDE.md`'s not-yet-adopted list is not dangling — it
       is the documented fallback the milestone ritual relies on.
       Rule 2's probe for the mechanism this step introduces — agent
       `tools:` frontmatter — runs here, reported like step `001`'s
       (the `.claude/rules/` probe waits for the step that first
       adopts a rules file, if any). Its
       test: I invoke each ritual and see it do what it claims —
       note that a new skill or agent may only be picked up at session
       start, so say whether a restart is part of the test.
     Nothing here is exempt from the small-step rule. If one of the
     three is still too big for a single test — or cut in the wrong
     place for this project — say so, and split it further in the plan
     you present; the cold review below is invited to find exactly that.
     And the three foundation entries carry this prompt's per-step
     prescriptions **in full** — the permission classifier and its
     traps, the probe duties, the CI-deferral reasoning, the
     instantiation list — as their deliverables and test content: this
     prompt is consumed at bootstrap, and a session resuming onto the
     plan must find that detail there, not remember it.
   - Steps carry track-qualified identifiers per rule 6 — `step-000` to
     `step-002`,
     the foundation, onward — grouped under milestones, which these
     plans are expected to be big enough for: the milestone close is
     what triggers rule 3's compaction and state review, so a plan you
     judge too small to group is a question for the open-questions
     section, never a silent omission. Steps must be small
     enough that I can test each one alone. For every step:
     **objective**, **spec sections implemented**, **deliverables**,
     **how I test it** — stating, when the test crosses rule 9's
     boundary, that it does, what it costs, and how I clean up
     afterwards — and **status** (`pending` / `in progress` /
     `awaiting test` / `done`).
   - Include the spec's non-code deliverables as steps in their own
     right: the per-image READMEs (also the GHCR pages), the repository
     README, the contributor guide for adding a game, and the MIT
     `LICENSE` file — all specified in root §9.
   - **The plans account for the whole specification**: every section
     of every document appears in at least one step, or in a short
     explicit list of what
     this pass leaves out with the reason — root §10 (Future
     Considerations), root §11 (Non-Goals) and project-zomboid §1's
     Build 41 non-goal give you most
     of that list. An orphaned section is how a requirement gets lost.
   - **Flag external prerequisites early**: things only I can prepare —
     the GitHub repository — existing, public, with Actions enabled —
     and its remote, plus my authorization of the first
     push (the CI-workflow step is only verifiable then); the GHCR
     owner namespace (`ghcr.io/<owner>`, root §7 — it names every
     published image); and, at each image's first publish, the one-time
     flip of its GHCR package to public visibility (root §2.6, §8),
     which only I can do; and, conditionally, a Docker Hub pull
     credential as a CI secret, if the implementation resolves
     root §2.6's anonymous-pull throttling risk with authenticated
     pulls — flag it the moment that choice is made. List each with the
     step that first needs it,
     so
     waiting on me never interrupts a step mid-flight.
   - End the root plan with a section listing anything you consider
     underspecified, risky, or worth reordering — across all tracks —
     questions for me, never
     silent assumptions.
2. **The decision logs** — root `DECISIONS.md`, `steamcmd/DECISIONS.md`,
   `project-zomboid/DECISIONS.md` — each initialised with the entry
   format, the root log with a first
   entry recording the adoption of this workflow.
3. **`CLAUDE.md`** — the ground rules above restated as your own standing
   instructions — concise, not verbatim, and keeping this numbering:
   tooling and decision entries cite the rules by number, and
   renumbering orphans every citation — plus the **track map** (each
   track, its directory, its step prefix, its plan and log), the
   repository layout as
   it will emerge, a section headed exactly **`Current state`** holding
   the pointer to the current step (that wording — your tooling
   templates reference the section by name), and the session-start
   routine — including the standing instruction that a session resumed
   after an interruption, or told the work was interrupted, runs
   `/resume-step` before touching anything, never trusting the
   transcript, and — until step `002` has instantiated that skill —
   applies rule 3's re-orientation routine directly instead: the
   pointer to a not-yet-existing command must not strand the
   interruptions most likely to happen early, the ones during the
   foundation steps themselves. It also carries the plan-step entry
   shape, the
   boundary-crossing-cost rule, and the cost taxonomy that orders the
   plans (free local work; slow multi-gigabyte local builds; shared
   public state) from the plan instructions above: later
   sessions extend the plans, and the bootstrap cold review sources
   those conventions from `CLAUDE.md`, so they must actually be there.
   For as long as any tooling template remains un-instantiated
   it also carries the pointer to `.claude/spec-work/handoff/assets/`,
   rule 1's standing exception for that one directory, and the list of
   templates not yet adopted — a block deleted, together with the
   directory itself, once the last template is adopted or dropped
   (rule 3): after this session `CLAUDE.md`, not this prompt, is what a
   session reads, and a later milestone close that cannot find
   `optimize-memory` has no way to know it was ever offered. Kept
   deliberately small per rule 3: what applies always stays
   in, everything context-specific becomes a `.claude/docs/` file it
   points to — and it lands **with headroom, around 160 lines, not at
   the 200-line cap**, so the next session that must add a pointer adds
   it instead of reflowing the file first. Write it so that a fresh
   session with no memory of this conversation behaves exactly as this
   one.
4. **`README.md`** — the neutral entry point for anyone who is not you: a
   human later, or another AI asked to review. Descriptive only: what the
   repository is, what each file is for, and the authority order —
   the specifications, then the decision logs, then the plans, then
   code.
   Include a short **For reviewers** section framing a review: the spec's
   must/should reading rules apply; code contradicting a *must* is a
   defect; a deviation from a *should* without a decision entry is
   a finding, while one with an entry is a judgement to assess; anything
   missing is checked against the active plan's current step before
   being
   flagged; and a problem in the specification itself is a question for
   the human, never a change to propose. Note that each plan step's list
   of spec sections is the review checklist for that step.

Then, before presenting anything: **commit the eight files** — one
`meta:` commit; rule 3's re-orientation reads git history, and an
uncommitted deliverable is invisible to it — and **have the plans
cold-reviewed**: this
session has no harness yet, so the cold review is rule 2's gate for it,
and step `000` brings these files under the harness retroactively.
Spawn a fresh-context, read-only subagent with an inline prompt (the
agent files come later, in step `002`) that reads only the three
specification documents,
the files you have just written, and `.claude/refs/` — given to it
with rule 3's framing, information and never a requirement source, so
a plan line citing the reference is checkable rather than an
unverifiable premise — never this conversation, and
nothing under `.claude/spec-work/`: it holds the specification phase's
history, this prompt included, and a reviewer that reads any of it is no
longer cold. The workflow conventions its criteria cite — the step
entry shape, boundary-crossing test costs, what counts as cheap — live
in the `CLAUDE.md` you have just written, not in the specification:
name it in the reviewer's prompt as the source of those conventions,
and tell the reviewer that `CLAUDE.md`'s pointer to
`.claude/spec-work/handoff/assets/` is out of bounds like the rest of
that directory. It audits the plans against the specification:

- **coverage** — every section of every specification document mapped
  to a step or explicitly
  excluded with reason, verified section by section, not trusted;
- **ordering** — dependencies respected within and across tracks, the
  cheap steps genuinely
  first, and no step depending on a capability a later step delivers
  (the classic: something goes live before its day-two operations
  exist);
- **granularity** — each step testable by me alone, boundary-crossing
  tests naming their cost and cleanup. **No step is exempt**, the
  foundation steps included: "this step is too big to judge in one
  gate" is one of the most valuable findings this review can return,
  and a plan that declares any step's breadth beyond question has
  disarmed its own reviewer;
- **proportion** — deliverables that exceed what their step's objective
  requires, anything the plan proposes to build that a standard tool of
  the ecosystem already provides, anything scheduled ahead of the need
  for it. "Delete this" and "use the boring existing tool" are findings
  of the same rank as a coverage gap;
- **prerequisites** — the external list complete, each with the step
  that first needs it;
- **consistency** — no dangling references between steps, within or
  across tracks;
- **premises** — any factual claim in the plans the specification does
  not state is flagged for verification, never trusted: training
  knowledge goes stale.

Triage its findings — accept, reject with reason, or genuinely my
call — apply and commit the accepted ones, and present the triage
together with the corrected plans for discussion, rejected findings
with their reasons included.
Step `000` begins only after I approve the plans.
