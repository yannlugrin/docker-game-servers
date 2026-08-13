# CLAUDE.md — standing instructions

Implementation agent instructions; a fresh session behaves per this file
alone. Tooling and logs cite "rule N" — the numbering is frozen.

## Ground rules

1. **Specifications are read-only.** The root `SPECIFICATIONS.md` and each
   image's are never edited on my own initiative. Their reading contract:
   "must" = requirement, "should" = recommended default deviable with logged
   reason, stated facts = environment constraints. Ambiguity, contradiction,
   or unimplementable text → stop and ask the operator. An agreed amendment:
   the decision entry is written before the text change, and both land in
   **one commit** — entry plus specification text, nothing else, subject
   naming the decision (`step-pz-003: spec amendment — D-007, …`); the entry
   lands alone only when the amendment belongs to a later step, and then says
   so and names that step. PZ §2 open facts: **recording a verified fact is
   autonomous** (one commit as above, reported in the step summary); **any
   resolution changing a requirement, a tier, a documented limitation or the
   ship decision** — and items (d), (e), (g), (k), (l) always — goes to the
   operator before the amendment. The image README carries the operator-facing
   consequence. Of the phase that produced the specification, the
   specification is the only input: never read anything under
   `.claude/spec-work/` (sole temporary exception: `handoff/assets/`, see
   Tooling templates below).
2. **One step at a time, gated by the operator.** Implement exactly one plan
   step, then stop with: (a) a short summary, (b) precise manual test
   instructions — exact commands and expected observations, (c) waiting.
   Requested fixes belong to the current step. Never batch steps. **Nothing is
   handed over unverified**: before asking the operator to test, every
   applicable check passes — Dockerfile lint; shell syntax and static
   analysis; YAML validation (workflow schema, compose examples);
   markdown/prose lint over documentation, the governance documents included
   (the lint bends to read-only documents, never the reverse; excluding a
   document from a rule is a logged decision); a check family for **every**
   language and artifact the repository ships, shipped static tools included
   (each pinned per rule 9's fetch rule); governance well-formedness
   (`.claude/skills/`, `.claude/agents/`, `.claude/settings.json`: frontmatter
   and JSON parse, every named command/path/agent resolves). Commands (`make
   setup` installs the pinned toolchain): `make check` = working tree
   well-formed (untracked included; gitignored paths and `.claude/spec-work/`
   excluded by path); `make test` = behavior against fixtures, including
   must-fail and must-warn cases; `make verify` = both. A narrowed fast check
   (`ONLY=`) is fine mid-step; the commit that receives a step tag runs the
   full one. Checks live in `.pre-commit-config.yaml`.
3. **All memory lives in files, per track.** Tracks: root (repo-wide),
   `steamcmd/`, `project-zomboid/`; each owns a `PLAN.md` and a `DECISIONS.md`
   (root's at the repository root, an image track's in its directory). Session
   start: read this file, root `PLAN.md` and `DECISIONS.md`, then the active
   track's `PLAN.md`, `DECISIONS.md` and `SPECIFICATIONS.md` (the Current
   state pointer names the track) plus the spec sections relevant to the
   current step — root §3 and §5 are standing reading for any image-track
   step; other tracks' files load only via a named cross-track dependency.
   Re-orientation: last approved state is `git describe --tags --abbrev=0
   --match 'step-*'` (match the step namespace, never the latest tag of any
   kind; before the first step tag, the range is the whole history); `git
   log`/`git diff` from there to `HEAD` is the work in progress. Tell the
   operator where we are before touching anything. This file stays under 200
   lines (hard budget; only rule 9's enumeration is exempt from trimming) —
   context-specific knowledge goes to `.claude/docs/<topic>.md`, referenced
   here with a read-trigger, plain paths, never `@` imports. `.claude/refs/`
   is operator-supplied input: read at its trigger, treat as information and
   never as a requirement source (conflict with the spec = question for the
   operator), never edit or delete. Auto memory stays disabled
   (`.claude/settings.json`). Completed plan steps compact to outcomes;
   closing a milestone includes a memory-compaction pass from a clean context
   (the `optimize-memory` agent where adopted, else a fresh subagent briefed
   inline) — decisions compact to their kernel, git history is the archive, no
   forward obligation orphaned. `docs/` and per-image READMEs are for humans;
   `.claude/docs/` is my memory — never mixed.
4. **Decisions get logged** in the track whose files they govern (repo-wide or
   cross-track → root `DECISIONS.md`). Kinds: joint (operator-approved),
   within-"should"-latitude (reason logged), and workflow choices left to me.
   The permission baseline is not in that latitude. Entry: `D-NNN` (per-log,
   file order, frozen, never reused; cross-log citations name the file), date,
   plan step, context, decision, alternatives, approved-by.
5. **Secrets never enter the repository** — no files, no real values in
   examples, no commit messages. Sourcing per root §5.4 / §4.3; committed
   examples use obvious placeholders.
6. **Commits are small and traceable; documentation ships inside them.** One
   coherent change per commit, subject prefixed with the step id, or `meta:`
   for maintenance belonging to no step. Track-qualified ids: root `step-NNN`,
   steamcmd `step-sc-NNN`, project-zomboid `step-pz-NNN`; numbering
   independent per track. Operator approval tags the closing commit with the
   step id (annotated). **Exactly one step in progress repository-wide**;
   history stays linear; cross-track sequencing comes only from named
   dependencies. The `step-*` namespace is this workflow's; ignore every other
   tag. Numbers freeze when a step enters `in progress`; `pending` steps may
   be renumbered — a renumbering commit sweeps every reference in the track's
   `PLAN.md` and citing decision logs (entries cite pending steps by number
   *plus title*). Everything a change makes stale updates in the same commit:
   plan status, decision entries, the Current state pointer, the root README
   file map, touched human docs, and new `.claude/docs/` insight. Commit
   locally; push only when the operator asks.
7. **Language.** Repository files, code, comments: English. Converse in the
   operator's language.
8. **Root `README.md` is the neutral entry point** — descriptive, never
   directive toward me; per-image READMEs are consumer documentation
   (image-track deliverables); the root README maps and links, keeps its file
   map accurate, and points at plans for current state.
9. **Bug reports on the current step are mine to drive**: reproduce,
   diagnose, fix, re-run checks until green; return with a fix or, at
   rule 10's budget, a clear question. The boundary (carried whole,
   never compressed or moved):
   Anything local and read-only runs freely without asking — installing
   the repository's pinned dependencies through the documented setup
   command included; fetching anything *not* pinned in the repository is
   not local, with two deliberate carve-outs:
   - the **local container lifecycle end to end** is free — build, run,
     exec, logs, inspect, wait, stop, rm, volume create and rm, compose
     up and down, and **targeted** cleanup of local images and volumes:
     `rmi`, `rm` and `volume rm` by name, prune only when scoped by
     label or filter to this project's resources — including the
     base-image pulls and the anonymous Steam downloads a build performs
     (a Project Zomboid build downloads several gigabytes: slow,
     costless); this project's images and test volumes are rebuildable
     working material — the irreplaceable local state is git's;
   - **read-only remote reads** are free — Steam metadata queries
     (buildid lookups), pulls of public images, `gh` and API read
     operations, authenticated or not; where a permission pattern cannot
     split reads from writes (`gh api`), the guard hook of step-000
     draws the line.
   **Blanket prune** (`docker system prune`, unscoped image/volume/
   builder prune) is gated with the outward writes: it is host-global,
   this host runs other projects, and their state is not mine to free.
   **Publishing or writing anything outward** — `git push`; `docker
   push` or any publish of any image to any registry (release tags are
   immutable and retained forever, root §7); any GitHub write through
   `gh` or the API: workflow dispatch, pull-request or release creation,
   repository settings, GHCR package operations including visibility and
   deletion — happens only when the operator explicitly asks for or
   allows it in that exchange, never on my own initiative — a boundary
   `.claude/settings.json` also enforces mechanically from step-000 on.
   When a failure cannot be reproduced within the boundary, ask the
   operator for command output or logs instead of guessing.
10. **Persistence has a budget — asking is part of the workflow.** Two or
    three genuinely different failed approaches (not variations of one guess)
    = stop; return with attempts, observations, hypotheses, and the unblocking
    question. The written summary is progress.

## Repository layout and track map

| Track | Directory | Step prefix | Plan / decisions |
|---|---|---|---|
| root | repository root | `step-NNN` | `PLAN.md`, `DECISIONS.md` |
| steamcmd | `steamcmd/` | `step-sc-NNN` | `steamcmd/PLAN.md`, `steamcmd/DECISIONS.md` |
| project-zomboid | `project-zomboid/` | `step-pz-NNN` | `project-zomboid/PLAN.md`, `project-zomboid/DECISIONS.md` |

A future game adds a directory, a per-game `SPECIFICATIONS.md` (root
§6), a track, and registers its prefix here.
`steamcmd/SPECIFICATIONS.md` is a pointer to root §4.

## Current state

Active track: root. Current step: **step-000 (awaiting test)** — repository
foundation: harness, CI, permission baseline, tooling. No step tag yet.

## Session-start routine

Read the files rule 3 names, run its re-orientation, report position, then
proceed as the current step's status directs. Rituals: `/orient`,
`/handover-step`, `/approve-step` — and `/resume-step` before touching
anything in a session resumed after an interruption, or told the work was
interrupted: never trust the transcript. Plan conventions (step-entry shape,
statuses, boundary-crossing cost, the step-000 exception) live in the root
`PLAN.md` header; sessions extending any plan follow it.

## References (rule 3)

- `.claude/refs/image-contract.md` — the container contract of one real
  consuming platform. Read when designing an image's operator interface
  (environment surface, ports, shutdown, health). Information only,
  never a requirement source; images stay platform-neutral (root §1).
- `.claude/docs/permissions.md` — what the rule-9 baseline enforces and how
  it was proven to bind. Read before changing `.claude/settings.json`.

## Tooling templates (temporary block — delete with the assets dir)

Starter templates live in `.claude/spec-work/handoff/assets/` — rule 1's one
standing exception, readable while a template remains un-instantiated.
Adopted at step-000: the four rituals above and the `step-reviewer` agent.
Not yet adopted: `optimize-memory`, `state-reviewer`, `code-reviewer`,
`test-reviewer` — each waits for its trigger, every adoption or drop is
logged, and nothing may name one as if it existed. Placeholders resolve to
the **active track's** files and id form (`state-reviewer` spans all
tracks). Once none remains un-instantiated, delete the directory, this
block, and every pointer to it in one commit.
