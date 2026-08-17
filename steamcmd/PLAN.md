# Implementation plan — `sc` track (steamcmd builder image)

The `sc` track owns the steamcmd builder image: its Dockerfile and its README.
**It does not own publication** — the publish workflow, the date-tag
computation and the never-reuse enforcement are CI, and CI lives in
`.github/workflows/`, a root directory, so the root track owns them
(`../PLAN.md` `step-006`; the criterion is `DECISIONS.md` D-005).

`root §N` references point to the repository-root `SPECIFICATIONS.md`, which
specifies this image in full; `SPECIFICATIONS.md` in this directory is a
pointer to it and carries no requirements (root §6, `DECISIONS.md` D-004).
**The root specification is never "another track's document"** (rule 3): root
§3 and §4 above all are standing reading for every step here. The step-entry
shape, the status vocabulary and the compaction-on-approval rule live in
`../.claude/docs/workflow.md` §1.

## How to read this plan

- Steps are ordered by dependency; the numbers are identifiers, frozen on
  entering `in progress`, never reused. **A step's dependency line, not its
  position, is what sequences it.**
- Exactly one step is in progress repository-wide, whichever track it belongs
  to.
- **Deliverables state what a step decides or builds beyond the
  specification, and cite the sections for the rest** — the session routine
  reads those sections anyway, and a copy of a read-only document can only go
  stale.
- **Paths: a deliverable inside this track's directory (`steamcmd/`) needs no
  path; anything outside it names its path.** So "the Dockerfile" means
  `steamcmd/Dockerfile`, while a justfile recipe or a `.claude/docs/` note is
  written with its path.
- Each test states whether it crosses the rule-9 boundary, what it costs and
  how to clean up. Anonymous steamcmd downloads and local builds are **free**
  per rule 9.
- **This track has no milestones.** Two steps do not earn the grouping, and
  the state review and memory-compaction passes are triggered by the root and
  `pz` milestone closes, which review the whole repository state rather than
  one track's delta (`../.claude/docs/workflow.md` §3).

---

### step-sc-001 — The builder image — `pending`

- **Objective.** A working, minimal steamcmd builder image, built locally,
  usable on its own as a generic "install a Steam app" builder.
- **Spec sections implemented.** root §4.1–§4.4, root §3.1 (the shared base),
  root §2.1, root §2.2, root §5.8 in part (the builder's own annotations).
- **Depends on.** **`step-005` done — the whole foundation, CI green.** No
  component-track step starts before the foundation is complete: `step-002`'s
  guard is what gates the image builds and steamcmd downloads this step
  performs, and `step-003`/`step-004` provide the review and handover rituals
  every handover from here uses. `step-000` is named separately as the reason
  the **Dockerfile lint family** can arrive with this step's first Dockerfile,
  but it is not sufficient on its own. (This edge used to come from position,
  when the builder was a root-track step sitting after the foundation; moving
  it here removed the guarantee without removing the requirement, so it is now
  stated.)
- **Deliverables.**
  - The **Dockerfile** on the base root §3.1 names, with a working steamcmd
    **already run once at build time** so its self-update is baked into the
    layer (root §4.2), and nothing beyond steamcmd's needs (root §4.4).
  - The app-id / branch / validation interface of root §4.3, including
    password-protected beta branches, and a **credential channel that leaves
    nothing in any layer or in the image's build history** — which rules out
    a plain build argument or a baked environment variable (root §4.3,
    root §10.4). The channel chosen is a logged decision.
  - The **Dockerfile lint** family arrives with this, the first Dockerfile in
    the repository (rule 2, never-ahead).
  - **Measurements** root §2.9 ordered taken at implementation, recorded in
    `.claude/docs/`: the base image's own size and the builder's size on top
    of it — the evidence for or against "Debian slim is the smallest workable
    base". A result that moves the expectation moves the named consequence,
    not the architecture; one implying a different base is a root §3.1
    **requirement** change and comes back to the operator first.
  - A local build recipe in the root `justfile` (no gated act — rule 2's
    invariant).
  - **Premises to verify here, not assume:** that the base tag root §3.1
    names resolves as written (`docker buildx imagetools inspect`); and what a
    steamcmd anonymous metadata query actually returns on a cold cache —
    whether it needs an explicit info-update step to answer at all, and what
    exit status a *failed* query gives. The last one matters because the
    publish gate of `../PLAN.md` `step-006` is built on it, and **a gate that
    passes on empty output gates nothing**.
- **How I test it.** Free and local, but not instant: building runs steamcmd,
  which downloads its own runtime from Steam (free per rule 9 — tens of
  megabytes here, not the gigabytes a game build pulls). Build it, read the
  reported size, then run an anonymous metadata query inside it and see it
  return a non-empty answer and exit zero; run a deliberately invalid query
  and see a non-zero exit. Cleanup: `docker image rm` the local tag by name
  (free — this project's own artifact).
- **Status.** `pending`

### step-sc-002 — The builder image README — `pending`

- **Objective.** The builder's per-image documentation, which is also its
  GHCR page.
- **Spec sections implemented.** root §9 (per-image README), root §4.1 (**it
  is not a runtime image and its documentation must say so**), root §7 (the
  builder's date-stamped tag policy), root §11 (the
  no-general-purpose-runtime-steamcmd non-goal, stated where a reader would
  otherwise assume otherwise).
- **Depends on.** `step-sc-001`.
- **Deliverables.** The **README** covering what the image is and what it is
  **not**; use as a build stage and standalone; the root §4.3 interface and
  the credential non-persistence rule; the tag scheme and that consumers pin a
  date tag or digest; platform-neutral throughout (root §9). Root §9's
  per-image content list applies as far as it is meaningful for a non-runtime
  image — a builder has no ports, no state root and no shutdown semantics, and
  says so rather than shipping empty sections.
- **How I test it.** Free and local. Read it; follow its standalone example
  against the locally built image and see the documented result.
- **Status.** `pending`

---

## Cross-track dependencies

| This track | needs | for |
|---|---|---|
| `step-sc-001` | **`step-005` done** (the whole foundation, CI green) | no component-track step starts before the foundation; `step-000` within it is what the Dockerfile lint family joins |
| **Other tracks need from here** | | |
| `step-006` (root) | `step-sc-001`, `step-sc-002` done | an image and its README before CI publishes them |
| `step-pz-001` (`pz`) | `step-sc-001` done | a builder image to build the game against |

## Coverage map — the root sections this track implements

`SPECIFICATIONS.md` in this directory is a pointer and has no sections of its
own to cover. What this track implements of the **root** document:

| Root section | Step(s) |
|---|---|
| §2.1 steamcmd is 32-bit glibc; amd64 only | `step-sc-001` |
| §2.2 steamcmd self-updates, no versions | `step-sc-001` (the pre-warmed layer); `step-006` (date tags) |
| §2.9 base-size measurement | `step-sc-001` |
| §3.1 the shared base; the pinned builder reference | `step-sc-001` |
| §4.1 purpose; not a runtime image | `step-sc-001`, `step-sc-002` |
| §4.2 pre-warmed steamcmd | `step-sc-001` |
| §4.3 app id, branch, validation, credential non-persistence | `step-sc-001` |
| §4.4 nothing beyond steamcmd's needs | `step-sc-001` |
| §5.8 the builder's own annotations | `step-sc-001` |
| §9 the per-image README | `step-sc-002` |
| §11 the no-runtime-steamcmd non-goal, documented | `step-sc-002` |

Root §7's builder tag scheme and root §8's publish gate are **root-track**
work (`../PLAN.md` `step-006`) and are mapped there, because CI lives in a
root directory.

## Open questions for the operator

1. **No milestones here, deliberately.** Two steps do not earn the grouping,
   and the repository-wide passes fire at the root and `pz` milestone closes.
   If this track grows a second builder line — root §10.1 contemplates a
   Wine/Proton pair — grouping becomes worth revisiting.
2. **The credential channel of root §4.3 is mine to choose** (the
   specification states the guarantee, not the mechanism), so I will log it
   rather than ask. Say so beforehand if you have a preference; `step-sc-001`
   is where it binds.
