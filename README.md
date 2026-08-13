# docker-game-servers

Docker images for dedicated game servers: a `steamcmd` builder image
that installs any Steam dedicated server at build time, and per-game
runtime images with the game baked in. The first game is the Project
Zomboid dedicated server (Build 42). Images are linux/amd64, based on
Debian 13 slim, published publicly on GHCR (`ghcr.io/yannlugrin`), and
platform-neutral: usable with plain `docker run`, compose, or any
orchestrator.

The project is under implementation. It is specification-driven and
built stepwise by an AI implementer under human review; the current
state of the work is in the plans listed below, not duplicated here.

## Repository map

| Path | What it is |
|---|---|
| `SPECIFICATIONS.md` | Root specification: goals, environment facts, core model, the conventions every game image obeys, versioning, CI, documentation deliverables |
| `steamcmd/SPECIFICATIONS.md` | Pointer — the builder is specified by root §4 |
| `project-zomboid/SPECIFICATIONS.md` | Per-game specification for the Project Zomboid image (part of the specification, same reading contract) |
| `PLAN.md` | Root-track implementation plan (foundation, CI, shared docs) and plan conventions |
| `steamcmd/PLAN.md` | Builder-track implementation plan |
| `project-zomboid/PLAN.md` | Project Zomboid-track implementation plan |
| `DECISIONS.md` | Root-track decision log |
| `steamcmd/DECISIONS.md`, `project-zomboid/DECISIONS.md` | Per-track decision logs |
| `CLAUDE.md` | Standing instructions for the AI implementer — workflow rules, not project documentation |
| `Makefile`, `requirements.txt`, `.pre-commit-config.yaml` | The checks and how to run them: pinned tools, and the hooks pre-commit runs |
| `tools/` | `governance.py` — the memory-consistency check no linter can do |
| `ruff.toml`, `.yamllint.yml`, `.pymarkdown.json` | Linter configuration, one file per tool |
| `.gitignore` | Ignored paths — also what `make check` does not look at |
| `.github/workflows/` | CI. Today: the harness on every push and pull request. Image build and publish workflows arrive with the images |
| `LICENSE` | MIT — covers the image recipes and tooling, not the game content inside the images |
| `.claude/` | Implementer workspace: settings, working memory, tooling, and the archived specification-phase history — not authoritative for humans |

Documentation written for people lives at the paths above and, as the
work progresses, in per-image READMEs and `docs/`; everything under
`.claude/` can be ignored by human readers entirely.

## Working on the repository

From a fresh clone, one setup command creates the virtual environment from
`requirements.txt` and installs the git hook:

```sh
make setup    # .venv from requirements.txt, pre-commit installed
make check    # every linter over the tree (pre-commit), untracked files included
make test     # behavior tests — none yet; they arrive with the images
make verify   # both
```

The same commands run in CI and from the git hook — there is no separate
CI-only configuration. Shell, Dockerfile and compose checks are added to
`.pre-commit-config.yaml` when the first such file arrives.

## Authority order

When documents disagree, authority runs:

1. **The specifications** — root `SPECIFICATIONS.md`, then the per-game
   specifications under it (root §6 binds them to the same contract);
2. **The decision logs** — recorded amendments, deviations and choices,
   each with its approval;
3. **The plans** — what is built, in what order, and each step's status;
4. **The code and images themselves.**

A disagreement between a lower and a higher layer is a defect in the
lower one.

## For reviewers

To review this repository (human or AI):

- The specifications' reading rules apply: **"must"** is a requirement —
  code contradicting one is a defect; **"should"** is a recommended
  default — a deviation *with* a decision-log entry is a judgement to
  assess, a deviation *without* one is a finding; plain statements about
  tools and protocols are environment facts.
- Anything apparently missing is checked against the current step in the
  plans before being flagged — most absences are steps not yet reached.
- Each plan step lists the spec sections it implements: that list is the
  review checklist for the step.
- A problem in the specification itself is a question to raise with the
  human maintainer, never a change to propose.
