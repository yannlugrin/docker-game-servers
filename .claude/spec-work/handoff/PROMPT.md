# Initial prompt — implementation bootstrap

> Operator note. To start implementation: open a fresh Claude Code
> session at the repository root and say "Read
> `.claude/spec-work/handoff/PROMPT.md` in full and do what it says."
> Everything below the separator is addressed to that session; this
> note is not.

---

You are implementing a public repository of Docker images for dedicated
game servers: a steamcmd builder image and per-game runtime images, the
first being the Project Zomboid dedicated server (Build 42). The complete
specification is **two documents**: `SPECIFICATIONS.md` at the repository
root, and `project-zomboid/SPECIFICATIONS.md` — the per-game specification
that root §6 makes part of the specification, under the same reading
contract. (`steamcmd/SPECIFICATIONS.md` exists too, but is a pointer: the
builder's specification is root §4.) Read both documents in full before
doing anything else — they define their own reading rules (requirements as
"must", recommended defaults as "should", environment constraints stated
as facts) and every section matters. This full read happens once, in this
bootstrap session, because the plans must cover the whole specification;
afterwards, per-image specifications are read per rule 3's track rule —
the active track's specification in full, the other image tracks' not at
all — rather than all of them at every session start. The root
specification is never "another track's document": its core model and
conventions (root §3, §5) are standing reading for any image-track step.

## Ground rules — permanent; you will encode them in CLAUDE.md

1. **Every `SPECIFICATIONS.md` is read-only for you** — the root document
   and each image's. You never edit one on your
   own initiative. If you find an ambiguity, a contradiction, or something
   that cannot be implemented as written, stop and raise it with me. If we
   agree a change is needed, the decision entry is written before the
   amendment — never a rationalization after it — and both land **in one
   commit**: the entry in the governing decision log (rule 4) and the
   specification text, nothing else, the subject naming the decision
   (`step-pz-003: spec amendment — D-007, …`). A commit where the log and
   the specification disagree is a state a session can resume onto and
   misread as drift; and `git blame` on an amended line must land on a
   diff carrying the reasoning. Code stays out, so `git log` on a
   specification file remains a readable history of amendments; the code
   implementing the change follows in the step's later commits. The entry
   lands alone only when the amendment belongs to a later step — then it
   says so and names that step. Silent drift between the spec and the
   implementation is the failure mode this rule exists to prevent. The
   open facts of `project-zomboid/SPECIFICATIONS.md` §2 are the expected
   case of this channel: the spec itself orders them settled at
   implementation, so verifying one and recording its resolution in that
   document is this rule followed, not an exception to it — decision entry
   and amendment in one commit, as above. That section's own "any correction
   lands in the image documentation" is the complementary half, not a
   different routing: the specification is amended so its facts stay
   true, and the image README carries the operator-facing consequence.
   The latitude splits in two, and the split is decided now: **recording
   a verified fact is yours to do autonomously** — decision entry and
   amendment in one commit, reported in the step's summary — while **any
   resolution that changes a requirement, a tier, a documented
   limitation or the ship decision is a together-decision** that comes
   back to me before the amendment; of the open items, (d), (e), (g),
   (k) and (l) are the ones that always come back — (d) because it
   decides whether `ADMIN_PASSWORD` is offered at all, a
   documented-surface change.

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

   **You hand nothing over unverified by yourself.** Before asking me to
   test, every check that applies to what you changed passes:

   - Dockerfile lint;
   - shell script syntax and static analysis (entrypoints, tooling
     scripts);
   - YAML validation, including the GitHub Actions workflow schema and
     the compose examples;
   - markdown/prose lint over documentation.

   That list is the expected instance, not the boundary: **every
   language and artifact the repository ships gets a check family** —
   the entrypoint in whatever language it ends up written, and the
   shipped static tools: root §5.5's two clients where adopted (they
   are a recommended default — a documented replacement is a
   legitimate, logged deviation), plus any similar tool a per-game
   specification adds (the SQLite client PZ §4 contemplates, for
   instance) — each entering the repository pinned
   (version or digest recorded in it, per rule 9's fetch rule) and
   covered like any other shipped artifact.

   Two families belong on that list whatever the stack: well-formedness
   of your own instantiated tooling under `.claude/skills/` and
   `.claude/agents/`, and of `.claude/settings.json` itself —
   frontmatter and JSON parse, and every command, path and
   agent a file names resolves, because a malformed skill does not fail,
   it silently never loads, and the settings file is the enforcement
   mechanism itself, so an edit that malforms it after step `000`'s
   one-time probe fails exactly as silently — and prove once, at step
   `000`, that each
   enforcement mechanism actually binds in your version: one probe for
   the settings baseline, a separate one for skill-frontmatter
   restrictions — two mechanisms, and one passing says nothing about
   the other; an unenforced allowlist is a guard that
   exists only on paper; and prose lint over the governance documents,
   configured to them as they already are — the specification documents
   are read-only under rule 1, so the lint bends to them and never the
   reverse, and excluding a document from a rule is a logged decision,
   not a quiet config line. These checks live behind **documented
   commands in
   the repository** — two questions, kept apart because each answer must
   mean something: a *check* ("is what is committed here well-formed?" —
   syntax, lint and formatting over the whole working tree, untracked
   files included and gitignored paths excluded, with one standing
   exception this prompt decides now:
   everything under `.claude/spec-work/` is excluded from the
   harness — the exclusion keys on the path, not on tracked status —
   because rule 1 makes that directory no session's reading material) and
   a *test* ("is the implementation right?" — fixtures
   and expectations proving behavior, including the cases that must fail
   and those that must only warn: a warning nobody proves is emitted
   protects nothing), plus a *verify* entry point running both. The
   commands' names and mechanism are yours to choose from whatever is
   native to the stack — a Makefile, package-manager scripts, a task
   runner — documented, kept green, and runnable by me too. A fast form
   of *check* narrowed to what changed is legitimate mid-step; the commit
   that receives a step tag runs the full one — that commit is the
   state every later session treats as known-good. My gate exists to
   judge behaviour against the real world, not to catch typos.

3. **All memory lives in files**, because your sessions do not persist —
   and it is organized **per track**, so a session loads only what its
   work needs. Three tracks exist today: the **root track** (repository-
   wide work: the foundation and harness, CI, shared documentation) and
   one **image track** per image directory (`steamcmd/`,
   `project-zomboid/`; a future game adds one). Each track owns:
   - a `PLAN.md` — its implementation plan and step statuses, at the
     repository root for the root track, inside the image directory for
     an image track;
   - a `DECISIONS.md` — its decision log, placed the same way.

   Repository-wide, exactly one `CLAUDE.md` exists: your standing
   instructions, the track map (step-id prefixes included), the
   current-step pointer, and the re-orientation routine.

   At the start of every session: read `CLAUDE.md`, the root `PLAN.md`
   and `DECISIONS.md`, then the active track's `PLAN.md`, `DECISIONS.md`
   and `SPECIFICATIONS.md` (the current-step pointer names the active
   track) and the spec sections relevant to the current step — root §3
   and §5 being standing reading for any image-track step. Other image
   tracks' files load only when the current step names a cross-track
   dependency on them. The
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
   happens elsewhere. It holds only what applies always —
   the rules, the file map, the current-step pointer, the session
   routine — and *pointers* to everything else. Knowledge needed only in
   a specific context — per-topic notes, environment details,
   troubleshooting insight you accumulate along the way — goes into its
   own file under `.claude/docs/`, referenced from `CLAUDE.md` with when
   to read it ("before touching the maintenance timers, read
   `.claude/docs/maintenance.md`"), and read only then — the read-trigger
   is what makes lazy loading actually happen. Plain path references,
   never `@` imports — imports load eagerly and cost the same as
   inlining.
   **`.claude/refs/` is a different thing and never mixes with it:**
   material I supply as input. Read each reference at its trigger, treat
   it as information and never as a requirement source (a conflict
   between a reference and the specification is a question for me), and
   never sweep, compact, fold or delete one: it is not your memory. One
   reference exists: `.claude/refs/image-contract.md`, the container
   contract of one real platform that consumes these images — read it
   when designing an image's operator interface (environment surface,
   ports, shutdown, health); the images stay platform-neutral (root §1).
   `CLAUDE.md` carries that pointer with its trigger.
   *Instructions* tied to one part of the tree may instead be path-scoped
   rules in `.claude/rules/` with a `paths` frontmatter, which load
   themselves exactly when you work on matching files — but never an
   unscoped rule, which loads every session and saves nothing. Before
   relying on that mechanism, prove it loads in the version you run — a
   rules file that never loads is instructions you believe are in force
   and are not, and the failure announces nothing; a nested `CLAUDE.md`
   is the fallback. Claude Code's **auto memory is already disabled**
   for this repository
   (`.claude/settings.json`, committed during the specification phase)
   and stays disabled: it is machine-local and unversioned — a second
   memory outside git, outside review, outside these rules — and
   everything it would hold belongs in `.claude/docs/` or a decision log
   instead. Confirm in step `000` that your version honours the key, on
   the same reasoning as the rules-file check: an unrecognised setting
   is ignored in silence.

   **The same economy applies to the memory files as they grow.** A
   completed step in any `PLAN.md` compacts to its outcome, the detail
   staying
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
   must be able to treat everything written for people as authoritative
   and ignore `.claude/` entirely.

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
   real commands and paths — including the governance set (`{{PLAN}}`,
   `{{DECISIONS}}`, `{{SPEC}}`, `{{STEP_ID}}`), which in this repository
   resolves to the **active track's** files and identifier form:
   `{{PLAN}}` and `{{DECISIONS}}` are that track's own (rule 3's track
   map), `{{STEP_ID}}` takes the track-qualified form of rule 6, and
   `{{SPEC}}` is the track's specification with root §3 and §5 standing
   (rule 3); a decision citation crossing logs names the file (rule 4).
   A template arrives with those as placeholders on purpose: a leftover
   one is visible, while a plausible wrong filename is not. Where a
   template's own enumeration of a routine is narrower than the rule it
   claims to execute, the rule wins and the enumeration is rewritten to
   match. Each adoption logged; the ones that earn
   their place later can wait — and once none remains un-instantiated
   (each adopted or explicitly dropped, logged), delete the assets
   directory and every pointer and exception referring to it in the same
   commit: git history keeps the templates, and rule 1's carve-out must
   not outlive its purpose. Tooling files are documentation like any
   other, kept current per rule 6 — and a skill or agent nobody invokes
   anymore is deleted, not kept.

4. **Decisions get logged**, each in the log of the track whose files it
   governs: an image-local choice in that image's `DECISIONS.md`,
   anything repository-wide or spanning tracks in the root
   `DECISIONS.md`. Three kinds: choices we
   make together (spec changes, scope calls, step reordering); choices
   you make alone inside the spec's "should" latitude — the spec permits
   deviating from a recommended default *with reason*, and that reason
   goes in the log; and workflow choices this prompt leaves to you,
   where the specification says nothing to deviate from — the harness's
   shape and names, `.gitignore` contents, which tooling templates you
   adopt. The permission baseline is not in that latitude: step `000`
   always puts it to me for review. Entry format: `D-NNN` id (file order,
   frozen once assigned, never reused; ids are per-log, so cross-log
   citations name the file — `project-zomboid/DECISIONS.md D-003`), date,
   plan step, context,
   decision, alternatives considered, approved by (me, or
   you-within-latitude, naming which latitude).

5. **Secrets never enter the repository.** Not in files, not in examples
   with real values, not in commit messages. The spec (root §5.4, and
   root §4.3 for build-time Steam credentials)
   defines how secrets are sourced; follow it, and use obvious
   placeholders in anything committed.

6. **Commits are small and traceable, and documentation ships inside
   them.** One coherent change per commit, subject prefixed with the step
   identifier — or `meta: ...` for maintenance belonging to no step. Step
   identifiers are track-qualified: the root track uses plain three-digit
   numbers (`step-000`, `step-001`, …), image tracks a short prefix plus
   three digits (`step-sc-001` for steamcmd, `step-pz-001` for
   project-zomboid; a future game registers its prefix in `CLAUDE.md`'s
   track map), numbering independent per track.
   When I approve a step, its closing commit receives an annotated tag
   identical to the step identifier — the same
   identifier then names the step in its track's `PLAN.md`, prefixes
   every commit,
   and names the tag, and `git diff` between two consecutive tags is
   exactly one
   step's change. **Exactly one step is in progress repository-wide at
   any time**, whichever track it belongs to: history stays linear, and
   the last `step-*` tag is the single last-approved state rule 3's
   re-orientation relies on. Each plan orders only its own track; a step
   names its cross-track dependencies explicitly ("needs `step-sc-002`
   done"), and those named dependencies — never a global sequence — are
   what interleaves the tracks.
   The `step-*` namespace belongs to this workflow; I will
   create other tags for my own purposes, so anything that reasons about
   steps matches `step-*` explicitly and ignores every other tag. Step
   numbers are identifiers, not positions: a step's number **freezes when
   it enters `in progress`** — commits and its tag reference it from then
   on and it is never reused — while `pending` steps may be renumbered as
   the plan evolves; a renumbering commit sweeps and updates every step
   reference in the track's `PLAN.md` and in every decision log that
   cites it, and decision entries cite
   not-yet-started steps by number *plus title*, so a missed sweep stays
   decodable. Each `PLAN.md`'s order and headings — grouped under
   milestones
   when the plan is big enough that grouping helps — define the sequence,
   not the numbering. Everything a change makes stale updates in the same
   commit, on your own initiative, never because I asked: the track's
   `PLAN.md`
   status, decision entries, `CLAUDE.md`'s current-step pointer and
   file references, the root `README.md`'s file map, and any
   human-facing document
   the change touches — documentation updated later is documentation that
   drifts. Likewise, when a step teaches you something a future session
   will need — an environment quirk, a hard-won diagnosis — writing it
   into `.claude/docs/` is part of finishing the step, not a favour. You
   commit locally; pushing to any remote happens only when I ask for it.

7. **Language.** Repository files, code and comments are in English.
   Converse with me in whichever language I use.

8. **The root `README.md` is the repository's neutral entry point** — for
   humans
   and for any other AI brought in to review. It is descriptive, never
   directive toward the implementer: your standing orders live in
   `CLAUDE.md` and are for you alone. The per-image READMEs of root §9
   are consumer documentation — deliverables of image-track steps, not
   workflow documents; the root README maps the repository and links
   them rather than duplicating them. Keep the root README's file map
   accurate
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
   the repository is not local, with two deliberate carve-outs decided
   now: the **local container lifecycle end to end** is free — build,
   run, exec, logs, inspect, wait, stop, rm, volume create and rm,
   compose up and down, and **targeted** cleanup of local images and
   volumes: `rmi`, `rm` and `volume rm` by name, prune only when scoped
   by label or filter to this project's resources — including the
   base-image pulls and the anonymous Steam
   downloads a build performs: it is the core dev loop, anonymous,
   costing only bandwidth and
   time (a Project Zomboid build downloads several gigabytes), and its
   destructive tail is deliberately free too, because this project's
   images and
   test volumes are rebuildable working material — the irreplaceable
   local state is git's, which stays protected below. **Blanket prune**
   (`docker system prune`, unscoped image/volume/builder prune) is
   gated with the outward writes: it is host-global, this host runs
   other projects, and their state is not yours to free. And
   read-only remote reads are free — Steam metadata queries (buildid
   lookups), pulls of public images, `gh` and API read operations,
   authenticated or not; where a permission pattern cannot split reads
   from writes (`gh api`), the guard hook of step `000` draws the line.
   **Publishing or writing anything outward** — `git push`; `docker
   push` or any publish of any image to any registry, because release
   tags are immutable and retained forever (root §7); any GitHub write
   through `gh` or the API: workflow dispatch, pull-request or release
   creation, repository settings, GHCR package operations including
   visibility and deletion — happens only when I
   explicitly ask for or allow
   it in that exchange, never on your own initiative — a boundary the
   settings baseline of step `000` also enforces mechanically. The
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

## Your first task — this session, no implementation yet

Produce the workflow files — three plans, three decision logs,
`CLAUDE.md`, the root `README.md` — then stop for my review:

1. **The plans** — root `PLAN.md`, `steamcmd/PLAN.md`,
   `project-zomboid/PLAN.md` — derived from the specification:
   - Each track's plan orders its own steps by the dependencies between
     the spec sections it implements; cross-track sequencing comes from
     each step's named dependencies (rule 6), never a global list. Known
     hard edges: the builder image (root §4) precedes the first Project
     Zomboid image build (root §3.1's build direction) — but PZ steps
     may interleave with later steamcmd steps where building the game
     image is the best exercise the builder can get; the PZ
     fact-verification items (`project-zomboid/SPECIFICATIONS.md` §2's
     open facts) gate entrypoint and healthcheck design, so they land
     early in that track; CI (root §8) comes after images build and
     smoke-test locally. Where that order allows, put the cheap steps
     first: Dockerfiles, entrypoints, the harness, documentation, local
     builds and local smoke runs are free (a PZ build downloads several
     gigabytes from Steam — slow, but costless); anything that publishes
     is not — GHCR release tags are immutable and retained forever
     (root §7), CI workflows are only verifiable after a push, and a
     first publish needs my manual visibility flip (root §2.6).
   - **The first step is the repository foundation** (`step-000`, root
     track), before any project
     code: a `.gitignore` written with rule 5 in mind (local test state
     roots and volumes — game saves and Steam-downloaded content from
     smoke runs; `.env` and any local credential file; steamcmd and
     image-build caches;
     `.claude/reviews/`, which the reviewer templates assume is ignored —
     an untracked report otherwise blocks every clean-tree precondition
     downstream; `CLAUDE.local.md`); pinned base dependencies installable
     through one
     documented setup command; the check/test/verify harness of rule 2,
     with pre-commit hooks **and a CI workflow running the same harness**
     (the repository already lives on GitHub — the `origin` remote points
     at `github.com/yannlugrin/docker-game-servers` — so the workflow
     targets GitHub Actions, with images published to
     `ghcr.io/yannlugrin`; treat the workflow as verified only
     once I authorise the first push, since nothing local can exercise
     it; check and
     test as separate jobs once both exist; cache the toolchain, but
     keep a
     periodic uncached run proving a fresh setup still works — a
     `schedule` trigger root §2.8 disables on idle repositories like
     any other, so it sits under the same staleness guard root §8
     gives the refresh) so nothing
     diverges among the three runners — and the lint covering
     the governance documents themselves (the specifications, the plans,
     the rest), since in this repository documents are load-bearing;
     **extending the committed `.claude/settings.json`** (auto memory is
     already off — keep it off) with a permission-and-hook baseline
     enforcing rule 9's boundary, proposed for my review: allow the
     harness, the setup command, the local container lifecycle of
     rule 9, and the
     *additive and read-only* subset of local git
     (add, commit, status, diff, log, show, rev-parse, describe, tag
     listing, annotated tags); **ask**
     for everything
     rule 9 gates, `git push` included — a denied pattern cannot be
     overridden in the very exchange rule 9 relies on — and for
     state-destroying local git (`reset --hard`, deleting tags or
     branches, history rewriting — `commit --amend`, `rebase` — and
     untracked-file deletion, `git clean`; the classifier the proposal
     applies: anything that rewrites history, moves or deletes tags,
     or destroys uncommitted or untracked work asks first, and an
     allow pattern must not silently admit these — `git commit`
     admitting `--amend` is the trap): the step tags, the linear
     history and the working tree are the memory rules
     3 and 6 rest on; reserve **deny**
     for what has no authorised use at all, naming each in the proposal
     rather than leaving "destructive" to interpretation; and a guard
     hook where a permission
     pattern cannot express the rule — instructions shape your behaviour,
     but only settings and hooks enforce it; and **your workflow tooling
     instantiated from `.claude/spec-work/handoff/assets/`** per rule 3 —
     `orient`, `resume-step`, `handover-step`, `approve-step` and the
     `step-reviewer` agent almost always earn their place from the
     start (a recovery ritual created during the crisis it is needed
     for is too late); propose the
     rest only when their trigger exists — and an instantiated file must
     never name a skill or agent you did not adopt: trim the reference
     or adopt it, because a dangling name is a ritual that silently
     skips a step. One carve-out: a name that sits on `CLAUDE.md`'s
     not-yet-adopted list is not dangling — it is the documented
     fallback the milestone ritual relies on. Its test: a fresh clone, the
     setup command, the check command, one commit — all green. Step
     `000`'s breadth is deliberate — one composite foundation step,
     this prompt's stated exception to the small-step rule, because its
     parts gate nothing separately testable: the fresh-clone test is
     the gate, the enforcement probes report their results in the
     step's summary, and the CI workflow is verified at first push.
     The plan cold-review below treats that breadth as decided here,
     never as a granularity finding.
   - Steps carry track-qualified identifiers per rule 6 — `step-000`,
     the
     foundation, onward — grouped under milestones or feature headings
     when a plan is big enough that grouping helps. Steps must be small
     enough that I can test each one alone. For every step:
     **objective**, **spec sections implemented**, **deliverables**,
     **how I test it** — stating, when the test crosses rule 9's
     boundary, that it does, what it costs, and how I clean up
     afterwards — and **status** (`pending` / `in progress` /
     `awaiting test` / `done`).
   - Include the spec's non-code deliverables as steps in their own
     right: the per-image READMEs, the repository README's consumer
     content, and the contributor guide for adding a game (all root §9);
     a verification that the existing root `LICENSE` satisfies root §9
     (MIT); and the resolution of `project-zomboid/SPECIFICATIONS.md`
     §2's open facts, whose outcomes amend that document through rule 1's
     channel.
   - **The plans together account for the whole specification** — both
     documents: every section appears in at least one step of some
     track, or in a short explicit list of what
     this pass leaves out with the reason — root §10 (Future
     Considerations), root §11 (Non-Goals) and the Build 41 non-goal of
     `project-zomboid/SPECIFICATIONS.md` §1 give you most
     of that list. An orphaned section is how a requirement gets lost.
   - **Flag external prerequisites early**: things only I can prepare —
     the GHCR package visibility flip at each image's first publish
     (root §2.6, §8); my authorisation of the first push, which is also
     what makes the CI workflow verifiable; a Docker Hub credential only
     if your root §2.6 mitigation chooses authenticated base-image
     pulls (no Steam credential is needed — every install is anonymous;
     and the repository itself is already public — root §2.8's schedule
     behavior rests on that, while root §2.6's free hosting rests on
     the per-package visibility flips above); and my confirmation, at
     first push, that the repository's Actions settings are known-good:
     Actions enabled, workflow token allowed `packages: write`.
     List each with the step that first needs it, so
     waiting on me never interrupts a step mid-flight.
   - End the root plan with a section listing anything you consider
     underspecified, risky, or worth reordering — across all tracks —
     questions for me, never
     silent assumptions.
2. **The decision logs** — root `DECISIONS.md`, `steamcmd/DECISIONS.md`,
   `project-zomboid/DECISIONS.md` — each initialised with the entry
   format; the root log's first entry records the adoption of this
   workflow, the track architecture included.
3. **`CLAUDE.md`** — the ground rules above restated as your own standing
   instructions — concise, not verbatim, and keeping this numbering:
   tooling and decision entries cite the rules by number, and
   renumbering orphans every citation — plus the repository layout as
   it will emerge, the track map with step-id prefixes (rule 6), a
   section headed exactly **`Current state`** holding
   the pointer to the current step (that wording — your tooling
   templates reference the section by name; the step identifier names
   its track), and the session-start
   routine — the per-track reading rule of rule 3, and the standing
   instruction that a session resumed
   after an interruption, or told the work was interrupted, runs
   `/resume-step` before touching anything, never trusting the
   transcript — and, until step `000` has instantiated that skill,
   applies rule 3's re-orientation routine directly instead: the
   pointer to a not-yet-existing command must not strand the one
   interruption most likely to happen early. It also carries the plan-step entry shape and the
   boundary-crossing-cost rule from the plan instructions above —
   later sessions extend plans and the bootstrap cold review sources
   those conventions from `CLAUDE.md`, so they must actually be there.
   It also carries the `.claude/refs/image-contract.md`
   pointer with its read-trigger and its never-a-requirement-source
   caveat (rule 3). For as long as any tooling template remains
   un-instantiated
   it also carries the pointer to `.claude/spec-work/handoff/assets/`,
   rule 1's standing exception for that one directory, and the list of
   templates not yet adopted — a block deleted, together with the
   directory itself, once the last template is adopted or dropped
   (rule 3): after this session `CLAUDE.md`, not this prompt, is what a
   session reads, and a later milestone close that cannot find
   `optimize-memory` has no way to know it was ever offered. Kept
   deliberately small per rule 3: what applies always stays
   in, everything context-specific becomes a `.claude/docs/` file it
   points to. Write it so that a fresh session with no memory of this
   conversation behaves exactly as this one.
4. **The root `README.md`** — the neutral entry point for anyone who is
   not you: a
   human later, or another AI asked to review. Descriptive only: what the
   repository is, what each file is for, and the authority order —
   the specifications (root, then per-image), then the decision logs,
   then the plans, then code.
   Include a short **For reviewers** section framing a review: the spec's
   must/should reading rules apply; code contradicting a *must* is a
   defect; a deviation from a *should* without a decision-log entry is
   a finding, while one with an entry is a judgement to assess; anything
   missing is checked against the current step in the plans before being
   flagged; and a problem in the specification itself is a question for
   the human, never a change to propose. Note that each plan step's list
   of spec sections is the review checklist for that step.

Then, before presenting anything: **commit the files** — one
`meta:` commit; rule 3's re-orientation reads git history, and an
uncommitted deliverable is invisible to it — and **have the plans
cold-reviewed**: this
session has no harness yet, so the cold review is rule 2's gate for it,
and step `000` brings these files under the harness retroactively.
Spawn a fresh-context, read-only subagent with an inline prompt (the
agent files come later, in step 000) that reads only the specification
documents — root `SPECIFICATIONS.md`, `project-zomboid/SPECIFICATIONS.md`
and the `steamcmd/SPECIFICATIONS.md` pointer — and the files you have
just written — never this conversation, and
nothing under `.claude/spec-work/`: it holds the specification phase's
history, this prompt included, and a reviewer that reads any of it is no
longer cold. The workflow conventions its criteria cite — step shape,
boundary-crossing test costs, the one-step-in-progress rule — live in
the `CLAUDE.md` you have just written: name it in the reviewer's prompt
as the source of those conventions, and tell the reviewer that
`CLAUDE.md`'s pointer to `.claude/spec-work/handoff/assets/` is out of
bounds like the rest of that directory. It audits the plans against the
specification:

- **coverage** — every section of both specification documents mapped
  to a step or explicitly
  excluded with reason, verified section by section, not trusted;
- **ordering** — dependencies respected within and across tracks, the
  cheap steps genuinely
  first, and no step depending on a capability a later step delivers
  (the classic: something goes live before its day-two operations
  exist);
- **granularity** — each step testable by me alone, boundary-crossing
  tests naming their cost and cleanup;
- **prerequisites** — the external list complete, each with the step
  that first needs it;
- **consistency** — no dangling references between steps or tracks, and
  the one-step-in-progress rule respected by the plans' shape;
- **premises** — any factual claim in the plans the specification does
  not state is flagged for verification, never trusted: training
  knowledge goes stale.

Triage its findings — accept, reject with reason, or genuinely my
call — and present the triage together with the plans for discussion.
Step `000` begins only after I approve the plans.
