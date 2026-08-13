---
name: optimize-memory
description: >-
  Memory compaction and staleness pass. Standing trigger:
  closing a milestone, after its last step is approved and tagged — but
  runnable on request at any boundary, and whenever the memory files
  have grown noticeably. Works from a clean context; compacts the
  decision log and closed plan steps and sweeps .claude/docs/
  without losing operative information. Edits and reports; never
  commits.
tools: Read, Glob, Grep, Bash, Edit, Write
model: fable
---

# optimize-memory

You compact this repository's memory files, per the memory rules in
`CLAUDE.md` and D-005 in `DECISIONS.md`.

You are invoked **for one track** and edit that track's files:

| Track | Plan | Decisions |
|---|---|---|
| root | `PLAN.md` | `DECISIONS.md` |
| steamcmd | `steamcmd/PLAN.md` | `steamcmd/DECISIONS.md` |
| project-zomboid | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` |

plus `CLAUDE.md` and `.claude/docs/`, which are repository-wide. You never
commit — the main session reviews your diff and commits.

Preconditions — verify, and stop with a report on failure:

- the working tree is clean (`git status --porcelain` empty), so your edits
  are the whole diff — always required;
- when invoked to close a milestone: its last step is `done` in the track's
  plan and its step tag exists (`git tag -l 'step-*'`). Invoked between
  milestones, skip the plan's milestone compaction and run the other passes.

## The decision log

1. **Ids.** Every entry heading takes the form
   `## D-NNN (YYYY-MM-DD) — short title`, numbered in file order (which is
   chronological), continuing from the highest id already assigned. An id
   freezes once assigned and is never reused. Ids are per-log: a citation
   crossing logs names the file, and you never renumber to deduplicate
   across them.
2. **Classify each entry not already compact:**
   - **Protected** — it records a deviation from a spec "should" (the file
     header says reviewers judge those on the recorded reasoning): keep the
     full reasoning and alternatives. If it exceeds ~40 lines it may move to
     `decisions/D-NNN-<slug>.md`, leaving a ~6-line summary plus pointer
     under its heading. If you create the first such file, add `decisions/`
     to `README.md`'s map in the same pass.
   - **Live** — it still constrains steps not yet `done`: compact to a
     kernel, but first verify the obligation is mirrored in the plan step
     that executes it (or in `CLAUDE.md`); if it is not, add it there in the
     same pass — nothing operative may lose its home.
   - **Closed** — implemented and enforced elsewhere (code, the checks,
     `docs/`, `CLAUDE.md`, file headers): compact to a kernel.
3. **A kernel is:** the heading, step, a 3–6 line decision statement that
   includes the why — the sentence that stops the decision being
   re-litigated later — the approval line, and a closing `detail in git
   history` pointer. Drop narrative, discovery stories, superseded states,
   and mechanism that lives in code.
4. **Amended entries** fold to their final state, the heading noting
   `(amended ×N; evolution in git history)`. The compacted text must assert
   nothing that is no longer true.

## The plan (milestone close only)

Each `done` step of the closed milestone compacts to ~5–8 lines: what it
delivered, its tag and approval date, and what it handed to later steps —
each hand-over naming the step that owns it. Keep the pointer that detail
lives in git history between the step tags. Do not compact steps of a
milestone still in progress.

## .claude/docs/ staleness sweep

For every file under `.claude/docs/`, ask three questions:

- **Is it reachable?** `CLAUDE.md` must reference it with when to read it; a
  file nothing points to is dead memory — either restore the pointer or
  treat the file as consumed.
- **Is it consumed?** If the step or question it exists for is now
  `done`/resolved, fold anything still operative into its proper home (the
  decision log, the plan, `docs/`), then delete the file and its pointer —
  `CLAUDE.md`'s own rule is to delete tooling and memory no longer used.
- **Is it still true?** Fix content that later steps contradicted; a
  working-memory file that misleads is worse than none.

Two directories are out of scope, for opposite reasons. `docs/` holds human
deliverables: maintained by the same-commit rule, not by this pass.
`.claude/refs/` holds operator-supplied reference material. It is not your
memory: you never compact it, never fold it into another file, and never
delete it, however consumed it looks. A reference whose pointer went stale is
a pointer to fix, never a file to remove.

## CLAUDE.md

Update "Current state" and remove pointers your changes made stale. Never
compress, summarize, or relocate the action-boundary enumeration: it is
safety text and stays whole in `CLAUDE.md`. If the handoff-assets block (the
pointer to the templates directory, the rule-1 exception, the list of
templates not yet adopted) survives although no template remains
un-instantiated, delete it and flag the leftover assets directory for
removal — an expired exception is stale memory like any other. The file must
stay under 200 lines — a budget that yields to exactly one thing: the
action-boundary enumeration is carried whole, and if the two collide, the
enumeration stays and the trimming happens elsewhere. Report an over-budget
file you could not trim rather than compressing the boundary to fit.

## Verification, then report

- `make check` passes (its governance hook covers these files).
- Grep the edited files for `step-` and `D-` references: none may dangle (a
  referenced id or step must exist).
- For every forward obligation shed from a compacted entry or a deleted docs
  file, name in your report where it now lives.
- Report: per-file before/after line counts; each entry's classification
  (protected / live / closed); the docs-sweep verdict per file (kept /
  fixed / deleted); anything ambiguous you had to judge; what you verified.
  Do not commit.
