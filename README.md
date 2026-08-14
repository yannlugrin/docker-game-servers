# Game server images

A public repository of Docker images for dedicated game servers: a
`steamcmd` builder image used as the build stage for every game, and
per-game runtime images with the game baked in at build time. The first
game is the Project Zomboid dedicated server (Build 42). Images are
generic and platform-agnostic — usable with plain `docker run`,
compose, or any orchestrator.

**Status: in progress.** The specifications are final; implementation
proceeds step by step under the plans below, each step reviewed and
approved by a human before the next begins. Current progress lives in
the plans — this file does not duplicate it.

## Authority order

When documents disagree, the earlier one in this list wins:

1. **Specifications** — `SPECIFICATIONS.md` at the root, plus
   `steamcmd/SPECIFICATIONS.md` and
   `project-zomboid/SPECIFICATIONS.md`, which are part of the
   specification (root §6). Read-only during implementation; changes
   go through the decision logs.
2. **Decision logs** — `DECISIONS.md` per track: choices made during
   implementation, with context and alternatives.
3. **Plans** — `PLAN.md` per track: derived ordering and step status.
4. **Code and other documentation.**

## File map

| Path | What it is |
|---|---|
| `SPECIFICATIONS.md` | Root specification: goals, environment facts, core model, game-image conventions, versioning, CI, deliverables |
| `PLAN.md` | Root track plan: foundation, CI, publication, shared docs |
| `DECISIONS.md` | Root track decision log |
| `steamcmd/` | The steamcmd builder image: specification, plan, decision log (image sources arrive with its plan's steps) |
| `project-zomboid/` | The Project Zomboid (Build 42) image: specification, plan, decision log (image sources arrive with its plan's steps) |
| `CLAUDE.md` | Standing instructions for the implementing AI — not documentation of the project |
| `.claude/` | Implementation-agent workspace (settings, working notes, references). Everything human-facing is authoritative without it |
| `justfile` | Task runner: `just setup`, `just check [scope]`, `just test`, `just verify` |
| `requirements.txt` | Pinned local tooling, installed by `just setup` into `.venv/` |
| `.pre-commit-config.yaml` | The well-formedness harness, shared by `just check` and the git pre-commit hook |
| `.pymarkdown.yaml`, `.codespellrc` | Prose-lint configuration |
| `LICENSE` | MIT — arrives at root plan `step-003` |

## Local checks

Installed once by hand, outside this repository: `git`,
[`just`](https://github.com/casey/just), and `python3` (3.9 or newer)
with its `venv` module. From a fresh clone, one command does the rest:

```sh
just setup
```

It creates `.venv/`, installs the pinned tooling from
`requirements.txt`, and installs the git pre-commit hook.

| Command | What it answers |
|---|---|
| `just check` | Is what is committed here well-formed? The whole working tree, untracked files included, gitignored paths excluded |
| `just check changed` | The same checks over what differs from `HEAD` — staged, unstaged and untracked — for the development loop |
| `just test` | Is the implementation right? Nothing here has runtime behaviour of its own yet, and the command says so |
| `just verify` | `just check` and `just test` |

`check` takes a `scope` parameter, `all` by default. The default scope
is the gate: step handover, milestone review, CI. `changed` is the fast
form and does not replace it — it cannot see a file that was committed
earlier and is broken by a config change made now.

Both scopes run the same `.pre-commit-config.yaml` definitions, as does
the git pre-commit hook (over the staged files), so no runner can
disagree with another about *what* gets checked — only about how much
of the tree it looks at. Everything under `.claude/spec-work/` sits
outside the harness, keyed on path.

**A failing check can modify the working tree.** Three hooks —
`end-of-file-fixer`, `trailing-whitespace` and `mixed-line-ending` —
repair what they find rather than only reporting it, which is the
pre-commit convention and what makes the commit hook worth having. A
*passing* check never writes anything; a failing one prints `files were
modified by this hook` and leaves the change visible in `git diff`. The
read-only documents are not exempt: stray whitespace in a
`SPECIFICATIONS.md` would be repaired in place. Every document in the
tree is whitespace-clean today, so nothing fires.

Local, disposable test state — bind-mount roots, downloaded game or
steamcmd content — belongs under `.local/`, which is ignored.

## For reviewers

A review of this repository — human or AI — should frame findings this
way:

- The specifications' reading rules apply: **"must"** statements are
  requirements; **"should"** statements are recommended defaults an
  implementation may deviate from *with reason*; statements of fact
  describe the environment.
- Code contradicting a *must* is a defect.
- A deviation from a *should* **without** a decision-log entry is a
  finding; one **with** an entry is a judgement to assess on its
  stated reasons.
- Anything apparently missing is checked against the active plan's
  current step before being flagged — most gaps are simply
  not-yet-reached steps.
- A problem in the specification itself is a question for the human
  owner, never a change to propose.
- Each plan step lists the spec sections it implements: that list is
  the review checklist for that step.
