# Game server images

A public repository of Docker images for dedicated game servers: a
`steamcmd` builder image used as the build stage for every game, and
per-game runtime images with the game baked in at build time. The first
game is the Project Zomboid dedicated server (Build 42). Images are
generic and platform-agnostic — usable with plain `docker run`,
compose, or any orchestrator.

**Status: planning.** The specifications are final; implementation
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
| `LICENSE` | MIT — arrives at root plan `step-003` |

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
