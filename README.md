# Docker images for dedicated game servers

A public repository of Docker images for dedicated game servers, built to be
as light as each game allows. Two kinds of image:

- a **builder image** carrying steamcmd and everything needed to install any
  Steam dedicated server at build time;
- **per-game runtime images**, one per game, containing the installed game,
  its runtime dependencies and a small amount of operator tooling — nothing
  else. The first game is the Project Zomboid dedicated server (Build 42).

The images are generic: they document their interface — environment
variables, ports, writable paths, configuration, shutdown behaviour — and are
usable with plain `docker run`, compose, or any orchestrator. They name and
assume no particular hosting platform. Each game image runs exactly one server
instance per container, and never installs or updates game content at runtime.

Images are published on GHCR, linux/amd64 only. Licence: MIT — it covers the
image recipes and tooling; the game content inside the images belongs to its
publishers and is not relicensed.

**No image is built yet.** This repository is at the start of implementation:
the specifications are complete, the plans are written, the local check
harness runs, and no image or CI workflow exists so far. For what exists at
any moment, read the plans — they are the current-state record, and this file
does not duplicate them.

## What each file is for

| Path | Purpose |
|---|---|
| `SPECIFICATIONS.md` | The repository-wide requirements: conventions every image obeys, the builder image, versioning and publication, build automation, documentation deliverables. |
| `project-zomboid/SPECIFICATIONS.md` | The Project Zomboid image's own specification — a per-game specification under root §6, binding in addition to the root document. |
| `steamcmd/SPECIFICATIONS.md` | The builder image's specification document. It is a **pointer**: the root document specifies the builder in full (root §4), and this file says where. Every shipped image directory carries one (root §6). |
| `PLAN.md`, `DECISIONS.md` | The root track's implementation plan and decision log: what lives at the root or in a shared directory — the harness, CI and all publication, the repository-wide documentation. |
| `steamcmd/PLAN.md`, `steamcmd/DECISIONS.md` | The same two documents for the builder image. |
| `project-zomboid/PLAN.md`, `project-zomboid/DECISIONS.md` | The same two documents for the Project Zomboid image. |
| `CLAUDE.md` | Standing instructions for the AI implementing this repository. Not a description of the project — see the note below. |
| `justfile` | The check harness's entry points: `setup`, `check`, `test`, `verify`. See "Working on this repository" below. |
| `.pre-commit-config.yaml` | What "well-formed" means here — the single declaration both `just check` and the git commit hook run, so the two cannot disagree. |
| `requirements.txt` | The pinned toolchain `just setup` installs into `./.venv`. |
| `.gitignore`, `.gitattributes` | What git ignores, and the repository's line-ending policy — LF everywhere, because these images ship shell entrypoints. |
| `LICENSE` | MIT. |
| `.claude/` | Implementation-side working material: the AI's own memory, tooling and reference inputs. Nothing here is a requirement source, and a human reader can ignore it entirely. |

Work is organised in **tracks**, one per directory: the root track owns what
lives at the repository root or in a shared directory, and each shipped image
directory is its own track with its own plan and log. Ownership follows where
the files live, not how far a change's effects reach — so CI belongs to the
root track even when it publishes an image another track owns.

As the repository grows, this map grows with it: `docs/` (human-facing
guides), `steamcmd/Dockerfile`, each game's `Dockerfile` and entrypoint, and
`.github/workflows/`. Each arrives with the plan step that creates it.

## Working on this repository

Prerequisites, none of them installed by the setup command because they are
what runs it: [`just`](https://github.com/casey/just), `python3` with the
`venv` module, and `git`.

```sh
just setup           # install the pinned toolchain into ./.venv, wire the commit hooks
just check           # is what is committed here well-formed? (whole tree)
just check <path>    # the same checks, narrowed to a pathspec
just test            # is the implementation right?
just verify          # both, in order
```

`just check` looks at tracked *and* untracked files, skipping anything
`.gitignore` covers, plus `.claude/spec-work/` and `.claude/refs/` — material
this repository does not own. The same checks run automatically on `git
commit` over what is staged. Alongside the well-formedness checks it runs a
secret scan and a set of guards against mistakes a later commit cannot undo:
an oversized file, a missing shebang or executable bit, a conflict marker, a
stray submodule. Nothing it runs rewrites a file.

`just test` currently reports that there is no behaviour of this repository's
own to test yet, which is the accurate answer rather than a gap: check
families and tests arrive with the artifacts they cover, never ahead of them.

## Authority order

When two documents disagree, the earlier one in this list wins:

1. **The specifications** — `SPECIFICATIONS.md` and each image's
   `*/SPECIFICATIONS.md`. They are the sole source of requirements.
2. **The decision logs** — where a specification permits a choice, the log
   records which choice was made and why.
3. **The plans** — what is being built, in which order, and what is done.
4. **The code, the workflows and the human documentation** — the result.

A per-game specification adds to the root conventions and may deviate from a
root *recommendation* with a recorded reason, but never weakens a root
requirement. Where the root document specifies an image in full — the builder —
its `SPECIFICATIONS.md` is a pointer to the governing sections and states no
requirements of its own.

`CLAUDE.md` sits outside this order: it holds the working rules of the AI
implementing the repository, not statements about the product. It is
deliberately not a place where requirements live.

## For reviewers

Whether you are a person or another AI asked to review, the specifications
define their own reading rules, and a review applies them:

- **"must" is a requirement.** Code contradicting one is a **defect**. Cite
  the section.
- **"should" is a recommended default** the implementation may deviate from
  *with reason*. A deviation with **no decision entry is a finding**; a
  deviation **with** an entry is a judgement to assess — read the entry's
  reasoning and say whether it holds, rather than treating the deviation
  itself as the problem.
- **Statements about tools, protocols and products are constraints of the
  environment**, not decisions — facts to verify if you doubt them, not
  choices to challenge.
- **Check anything missing against the plan before flagging it.** Work not
  yet started is not a defect. The owning track's plan says which step is
  current; each step lists the specification sections it implements, and
  **that list is the review checklist for that step**.
- **A problem in a specification itself is a question for the repository's
  owner** — never a change to propose, and never something to fix in passing.
  The same applies to anything under `.claude/refs/`, which is
  owner-supplied input from elsewhere.
- **Deletion is a legitimate finding.** "This could be removed" and "this
  could be replaced by something the ecosystem already provides" rank beside
  correctness findings.

Reviews of the specification-writing phase are not needed and its history is
not review material; review the repository as it stands against the
specifications as they stand.
