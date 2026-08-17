# CLAUDE.md — standing instructions

Requirements live in `SPECIFICATIONS.md` (repository-wide) and
`project-zomboid/SPECIFICATIONS.md` (first game, under root §6). Read both
before implementing: "must" is a decided requirement, "should" a recommended
default you may deviate from **with a logged reason**, environment constraints
are stated as facts. `README.md` describes the project.

**The rules below state what binds, not why.** Their reasoning and mechanics —
step-entry shape, amendment ritual, harness contract, tooling placeholders,
milestone-close passes — live in `.claude/docs/workflow.md`, which carries its
own read triggers.

## Session start — before touching anything

1. Read this file, the root `PLAN.md` and the root `DECISIONS.md`.
2. Read the active track's plan, log and specification, plus the spec sections
   the current step names. **The root specification is never "another track's
   document"**: root §3 and §5 above all are standing reading on any track.
   Other tracks' files load only when the step names a cross-track dependency.
3. Find the last approved state by matching the step namespace, never the
   latest tag of any kind: `git describe --tags --abbrev=0 --match 'step-*'`.
   `git log`/`git diff` from it to `HEAD` are exactly the work in progress;
   before the first step tag, the range is the whole history.
4. Report where we are, then wait.

**A session resumed after an interruption** — usage limit, crash, killed
console — or told the work was interrupted, runs `/resume-step` before
touching anything and never trusts the transcript. Until `step-004`
instantiates that skill, apply the routine above directly instead.

## The rules

**1. Every `SPECIFICATIONS.md` is read-only.** Never edit one on your own
initiative; an ambiguity, contradiction or unimplementable requirement stops
work and is raised. An agreed change happens only through a decision entry
written **before** the amendment, landing **in one commit** with the
specification text and nothing else (`.claude/docs/workflow.md` §0).
**Open facts** are this channel's expected case; each plan's open-facts
register maps every one to its step. Settling one whose outcome leaves
requirements, tiers, documented capabilities and the ship decision untouched
is autonomous: entry plus pre-ordered amendment, one commit, reported in the
step summary. **Everything else comes back to the operator first,
pre-committed response or not:** the ship decision, a changed
mandatory/optional tier, a changed requirement or documented limitation, a
dropped or added capability or variable. The `pz` register's **E** column
names them individually. Resolutions land in the specification, their
operator-facing consequences in the image documentation.
**The specification is your only input from the phase that produced it.** You
never read `.claude/spec-work/` — one standing exception, `handoff/assets/`,
below — and **never another branch's content**: this branch is the project.
Something apparently missing is a question, never something to excavate.

**2. One step at a time, gated by the operator.** Implement exactly one plan
step, then stop with (a) a short summary, (b) precise manual test instructions
— exact commands and what to observe — and (c) waiting. Never start the next
step unbidden, never batch steps because they look small; requested fixes
belong to the current step. **When the operator asks for something to be
removed, it is removed** — not shrunk, rewritten or moved; if you think that
is a mistake, say so in one sentence and do it anyway, or ask first which was
meant.
**Nothing is handed over unverified.** Every check applying to what you
changed passes first: `just check <scope>`, `just test`, `just verify`. A check
family and its fixtures arrive **with the first file of their class, in the
step that lands it**, never ahead of it; the contract, its three limits and
the full-scope-at-the-tag rule are in `.claude/docs/workflow.md` §5.
**No justfile recipe ever performs an act rule 9 gates.** Prove each
enforcement mechanism at the step introducing it and record the measurement in
`.claude/docs/` with version, method and re-measure recipe — **never here**.

**3. All memory lives in files.** Per track: `PLAN.md` and `DECISIONS.md` in
the track's directory. Repository-wide: exactly one `CLAUDE.md` — this file —
plus context-specific knowledge in its own file under `.claude/docs/`,
referenced from here with **when to read it** and read only then. Plain paths,
never `@` imports. This file loads every run, so it stays **within D-002's
budget, with headroom**; when it binds, things leave in this order, not one of
your choosing: context-specific matter a read-trigger can reach, the templates
block once its directory is gone, then per-track detail the track's plan
carries. **Rule 9's enumeration never leaves, nor does the current-step
pointer.** If the rules still will not fit, raise it as a finding — a revised
budget, logged, is a legitimate outcome — never delete something with nowhere
else to go.
**Human and machine documentation never share a directory:** `docs/` and the
per-image READMEs are human deliverables, `.claude/docs/` is your working
memory. Auto memory is disabled in `.claude/settings.json` and stays disabled.
**`.claude/refs/` is the operator's, read-only exactly as the specification
is:** you never modify, annotate, compact or delete one, and no sweep of yours
touches it. A reference is **information, never a requirement source**; a
conflict with the specification is a question for the operator. One that looks
wrong is **reported**; what made you doubt it goes in `.claude/docs/` or a
decision log under your name.
**Tooling shares that namespace:** skills at `.claude/skills/<name>/SKILL.md`,
subagents at `.claude/agents/`, created on your initiative when they earn
their place, logged per rule 4. A ritual repeated every step is a skill; work
that would flood your context belongs in a subagent; one nobody invokes is
deleted. **Memory compacts as it grows:** a completed step compacts to its
outcome, detail staying in git history, and **closing a milestone includes a
whole-state review then a memory-compaction pass** — both mandatory, from a
clean context, on a model that did not write the work
(`.claude/docs/workflow.md` §3).

**4. Decisions get logged, in the log of the track whose files they govern.**
Repository-wide goes in the root `DECISIONS.md`; ids are **per log**, each
starting at `D-001`, so a citation crossing logs names the file. A `pz`-track
step amending the **root** specification logs in the **root** log, same
commit, `pz` step id in the subject. Three kinds: choices made with the
operator; choices inside a "should" latitude, whose reason goes in the log;
workflow choices left to you. **The permission baseline is not in that
latitude** — `step-002` puts it to the operator. Format: `D-NNN` (file order,
frozen, never reused), date, step, context, decision, alternatives, approved
by.

**5. Secrets never enter the repository.** Not in files, not in examples with
real values, not in commit messages. Root §5.4 defines runtime sourcing, root
§4.3 build-time credential non-persistence; committed examples use obvious
placeholders.

**6. Commits are small and traceable, and documentation ships inside them.**
One coherent change per commit, subject prefixed with the **track-qualified**
step id — `step-NNN:` (root), `step-pz-NNN:` (`pz`), three digits,
zero-padded, numbered independently per track — or `meta:` for maintenance
belonging to no step. **Exactly one step is in progress repository-wide**, so
history stays linear and the last `step-*` tag is the single last-approved
state. Each plan orders only its own track; cross-track sequencing comes from
steps naming dependencies. On approval the closing commit gets an **annotated
tag** named by the step id; a step's number **freezes when it enters `in
progress`**, while `pending` steps may be renumbered, with a sweep (both
shapes: `.claude/docs/workflow.md` §5). The `step-*` namespace is this
workflow's — the operator creates other tags, so anything reasoning about
steps matches `step-*` explicitly. **Everything a change makes stale updates
in the same commit, on your own initiative:** plan status, decision entries,
this file's pointers, `README.md`'s file map, any human-facing document
touched; what a step taught a future session goes into `.claude/docs/`. You
commit locally; pushing happens only when the operator asks — **one standing
exception: at a step close, attempt the push**, so the permission gate puts
the publish question to them. Cite it; never extend it.

**7. Language.** Repository files, code and comments in English. Converse with
the operator in whichever language they use.

**8. `README.md` is the neutral entry point** — for humans and for any other
AI brought in to review. Descriptive, never directive toward you: your
standing orders are here. Keep its file map accurate; for current state it
points at the plans.

**9. Bug reports on the current step are yours to drive.** Reproduce,
diagnose, fix, re-run your own checks until they pass, then hand back with
what changed and how to re-test. Do not return after every attempt — return
with a fix, or with a clear question once rule 10's budget is spent.
**The boundary.** Anything local and read-only you run freely and without
asking — **installing the repository's pinned dependencies through the
documented setup command included; fetching anything *not* pinned in the
repository is not local**, with three named exceptions ruled free for this
project: **anonymous steamcmd downloads and Steam metadata/buildid queries**
(every game-image build depends on them; a Project Zomboid build pulls
multiple gigabytes, so say so when a step's work will), **pulls of the pinned
base and builder images**, and **GitHub API reads** via `gh` or equivalent.
The development loop is free end to end, local writes included: building
images locally; starting, stopping, exec-ing into, reading the logs of, and
removing *this project's own* containers, images and volumes by name; creating
and tearing down local test state directories; running the harness and smoke
tests locally — including the incidental Steam master-server registration a
locally started server performs on its default profile, ruled free
deliberately (an outward write, but the listing is transient, names an
ephemeral test server, and delists on stop) — and the workshop-mod downloads a
mod-configured test server performs at startup (PZ §7), part of the same loop.
**Destructive-local splits on blast radius, not on the verb:** removing this
project's own artifacts by name is rebuildable working material and free,
while any unscoped sweep — `docker system prune`, `docker volume prune`, a
wildcard delete — reaches other projects on this host and is gated like an
outward write; and two things stay protected whatever the scope: git history
and the uncommitted working tree. Everything else — **any push or publish to
GHCR or any registry, development tags included; anything that writes to
GitHub (`gh` writes, workflow dispatch, package or repository settings);
deleting registry content; and the unscoped destructive operations above** —
happens only when the operator explicitly asks for or allows it in that
exchange, never on your own initiative; the settings baseline of `step-002`
also enforces this mechanically. When you cannot reproduce a failure inside
that boundary, ask for the command output or logs rather than guessing.

**10. Persistence has a budget — asking is part of the workflow.** Ask when
you need to: a spec ambiguity (rule 1), a choice inside a step that is the
operator's, a failure you cannot resolve quickly. Two or three genuinely
different approaches failing — not variations of one guess — is the signal to
stop. Come back with what you tried, what you observed, your hypotheses and
the question that would unblock you.

**11. Proportion: the smallest thing that satisfies the rule is the right
thing.** The boring standard tool beats yours — ask whether the ecosystem
ships a runner, installer, discovery library or test driver before writing
one. Build at the moment of need, not in anticipation. **Deletion is a
legitimate outcome of a review and of a step**: "this could be removed" and
"this could be replaced by something standard" rank beside defects. If nothing
would be lost by deleting something, say so first.

## Where things live

`README.md` carries the full file map. `docs/` and the per-image READMEs are
**human** deliverables; `.claude/docs/` is **your** memory; `.claude/hooks/`,
`.claude/skills/`, `.claude/agents/` hold the guard, the rituals and the
reviewers; `.claude/spec-work/` is **never read** (rule 1); `.claude/refs/` is
operator-supplied reference material (rule 3).

- **`.claude/docs/workflow.md`** — rule mechanics and reasoning; its own
  header lists when to read which section.
- **`.claude/refs/image-contract.md`** — the image contract of a hosting
  platform that will consume these images. Read it **before designing a game
  image's runtime interface** (uid handling, state paths, stop behaviour,
  health and save probes) and **before writing per-image documentation**. The
  images should satisfy it but are not limited to it; where it asks for what
  the specification does not require, or the two conflict, ask.

## Track map

| Track | Directory | Step prefix | Plan | Log |
|---|---|---|---|---|
| root (repository-wide) | `.` | `step-NNN` | `PLAN.md` | `DECISIONS.md` |
| `pz` (Project Zomboid) | `project-zomboid/` | `step-pz-NNN` | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` |

Each new game adds a track and registers its prefix here.

## Tooling templates not yet instantiated

*Temporary block, deleted with `.claude/spec-work/handoff/assets/` and every
pointer naming it, in the same commit as the last adoption or drop (rule 3).*
That directory holds starter templates and is **rule 1's one standing
exception**: readable while a template remains un-instantiated. How to
instantiate: `step-003`/`step-004` in `PLAN.md`, `.claude/docs/workflow.md` §2.

- **Not yet adopted:** `code-reviewer`, `test-reviewer` — their triggers
  (implementation code, a test suite) do not exist yet; a ritual may cite them
  as documented fallback names.
- **Adopted at `step-002`:** `bash_guard.py`. **`step-003`:** `step-reviewer`,
  `state-reviewer`, `optimize-memory`. **`step-004`:** `orient`,
  `resume-step`, `handover-step`, `approve-step`.

## Current state

*A closed list of item kinds — current and next step, live world-state, open
obligations, `.claude/docs/` pointers — and nothing else; **what a closed step
produced is not one of them** (`.claude/docs/workflow.md` §4).*

- **Current step:** none in progress; the governance files are committed.
- **Next step:** `step-000` — The harness skeleton, local only (root track),
  beginning only when the operator approves the plans.
- **Live world-state:** nothing built, nothing published, no CI, no `step-*`
  tag. `origin` is `git@github.com:yannlugrin/docker-game-servers.git`
  (public); **this branch is the project and is treated as `main`**, force-pushed
  there once the foundation is validated.
- **Open obligations:** `PLAN.md`'s external prerequisites — the GHCR package
  visibility flips, and a Docker Hub credential only if base-pull limits bite.
- **`.claude/docs/` pointers:** `workflow.md` (above). `step-000` adds
  `environment.md` (measured toolchain), `step-002` the permission and hook
  measurements, `step-pz-001` `pz-facts.md`.
