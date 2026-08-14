# CLAUDE.md — standing instructions

Spec-driven implementation of Docker images for dedicated game servers.
Authority order: the `SPECIFICATIONS.md` documents (root and per-image),
then decision logs, then plans, then code. This is the only `CLAUDE.md`
repository-wide; hard budget 200 lines.

## Session start

1. Read this file, then root `PLAN.md` and `DECISIONS.md`, then the
   active track's plan, decision log and `SPECIFICATIONS.md`, plus the
   spec sections the current step names. Root spec §3 and §5 are standing
   reading on any component-track step — the root specification is never
   "another track's document". Other tracks' files load only when the
   current step names a cross-track dependency.
2. Locate the last approved state:
   `git describe --tags --abbrev=0 --match 'step-*'` — match `step-*`
   only, other tags exist and are not step tags. `git log` and
   `git diff` from that tag to `HEAD` are exactly the work in progress;
   before the first step tag, the whole history is. Tell the operator
   where we are before touching anything.
3. A session resumed after an interruption, or told the work was
   interrupted, runs `/resume-step` before touching anything — never
   trusting the transcript. Until step-002 instantiates that skill,
   apply steps 1–2 above directly instead.

## Current state

- Active track: root. Current step: **`step-001` — Permission and hook
  baseline, awaiting test.** Next: `step-002` — Workflow tooling.

## Track map

| Track | Directory | Prefix | Plan | Decision log |
|---|---|---|---|---|
| root | `/` | `step-NNN` | `PLAN.md` | `DECISIONS.md` |
| steamcmd | `steamcmd/` | `step-sc-NNN` | `steamcmd/PLAN.md` | `steamcmd/DECISIONS.md` |
| project-zomboid | `project-zomboid/` | `step-pz-NNN` | `project-zomboid/PLAN.md` | `project-zomboid/DECISIONS.md` |

Exactly one step is in progress repository-wide; history stays linear.

## Rules — cite by number; renumbering orphans every citation

1. **Every `SPECIFICATIONS.md` is read-only.** Never edit one on your
   own initiative. Ambiguity, contradiction, unimplementable text: stop
   and raise it. An agreed change lands as one commit holding the
   decision entry plus the spec amendment, nothing else, subject naming
   the decision. **Open facts** (root §2.9, project-zomboid §2 a–o):
   verifying one and recording its pre-committed resolution is
   autonomous (one commit, reported in the step summary); any resolution
   changing a requirement, a tier, the operator surface, a documented
   limitation or the decision to ship comes back to the operator before
   the amendment. `.claude/spec-work/` is never read (exception: see
   Tooling templates below, while it stands).
2. **One step at a time, gated by the operator.** End a step with a
   summary, exact manual test instructions, then wait. Requested fixes
   belong to the current step. Asked-for removals are removed — not
   shrunk, rewritten or relocated. Hand nothing over unverified: every
   applicable check green first (`just check` / `just test` /
   `just verify` once step-000 lands), including governance
   well-formedness (skill/agent frontmatter, settings JSON parse) and
   prose lint. A new artifact class gets its check family in the step
   that lands its first file. Full `check` runs on every commit that
   receives a step tag; a narrowed fast form is fine mid-step.
3. **All memory lives in files.** Plans and logs per track (see map);
   contextual knowledge in `.claude/docs/` with a read-trigger noted
   here; `.claude/refs/` is operator-supplied input, read-only like the
   spec — a reference that looks wrong is reported, never edited.
   Auto memory stays disabled. Milestone close triggers a
   memory-compaction pass and a state review, keyed on the track of the
   step just closed. Completed steps compact to outcomes; git history is
   the archive; no forward obligation may be orphaned by compaction.
4. **Decisions get logged** in the owning track's `DECISIONS.md`
   (repository-wide → root log); ids are per log, cross-log citations
   name the file. Entry: `D-NNN`, date, step, context, decision,
   alternatives, approved-by (operator, or self-within-latitude, naming
   the latitude). Three kinds: joint choices; "should" deviations with
   reason; workflow choices left to me. The permission baseline is not
   in that latitude — step-001 puts it to the operator.
5. **Secrets never enter the repository** — files, examples, commit
   messages. Sourcing per root §5.4 and §4.3; placeholders only.
6. **Commits are small and traceable; documentation ships inside
   them.** One change per commit, subject prefixed with the step id, or
   `meta:` for stepless maintenance. Approved steps get an annotated
   `step-*` tag (id + title, approval date, notable outcomes). Step
   numbers freeze on entering `in progress`; `pending` steps may be
   renumbered with a full reference sweep. Everything a change makes
   stale — plan status, decision entries, this file's Current state and
   pointers, `README.md`'s file map, human docs — updates in the same
   commit, plus any `.claude/docs/` insight the step produced. Commit
   locally; push only when the operator asks.
7. **Language.** Repository files, code and comments in English;
   converse with the operator in the operator's language.
8. **`README.md` is the neutral entry point** — descriptive, never
   directive toward the implementer; standing orders live here only.
9. **Boundary.** Free, without asking: anything local and read-only;
   installing the repository's pinned dependencies through the
   documented setup command — fetching anything *not* pinned in the
   repository is not local; bootstrapping the toolchain before that
   command exists — each tool via its canonical distribution channel,
   user-level, pinned once chosen; a tool needing a system-level
   install (apt, anything wanting root) is never scripted or run by
   me — I name it and ask the operator to install it. The downloads
   inherent to building this project's images locally (apt inside the
   build, base images, Steam content) are part of the free build; the
   not-pinned clause governs adding unpinned dependencies to the
   repository, not these. The free side is the development loop end to
   end: building this project's images locally; creating, starting,
   stopping, exec-ing into, inspecting and removing this project's
   containers; reading their logs; creating and deleting this
   project's named images, volumes and local test state directories;
   steamcmd's anonymous Steam downloads during local builds and smoke
   tests; and anonymous remote reads with no side effect — Steam
   buildid and metadata queries, GHCR catalog and manifest reads. One
   profile rule inside that loop: a default-profile server start
   registers the server on the public Steam browser (root §5.2;
   project-zomboid §2–§3), so routine local testing prefers the
   non-Steam profile wherever it suffices; default-profile starts stay
   free — the registration is an accepted side effect — but are used
   where the specification requires them (the smoke gate of root §8,
   verification of Steam-dependent behavior), not as the habitual
   iteration loop. Destructive-local splits on blast radius, not the
   verb: removing this project's artifacts by name is rebuildable
   working material and free, while an unscoped sweep (`docker system
   prune`, a wildcard delete) reaches other projects on this host and
   sits with the gated writes. Everything on the gated side — any
   registry write (`docker push`, GHCR API writes), `git push` to any
   remote, any GitHub write (repository creation, workflow dispatch,
   secrets, package visibility), any other outward side effect
   (webhooks, mail, uploads, registrations), unscoped Docker sweeps,
   and anything that rewrites git history or destroys uncommitted or
   untracked work — happens only when the operator explicitly asks for
   or allows it in that exchange, never on my own initiative. When a
   failure cannot be reproduced within that boundary, ask for the
   command output or logs instead of guessing. This enumeration is
   carried whole here, never compressed or moved.
10. **Persistence has a budget.** Two or three genuinely different
    failed approaches — not variations of one guess — is the signal to
    stop and return with attempts, observations, hypotheses, and the
    unblocking question. Bug reports on the current step are mine to
    drive to a fix before handing back.
11. **Proportion.** The boring standard tool beats mine; build at the
    moment of need; deletion is a legitimate review outcome; a clean
    review does not prove the work was worth doing.

## Plan conventions

Step entry: **objective**, **spec sections**, **dependencies**,
**deliverables**, **how the operator tests it** (a boundary-crossing
test states that it crosses, its cost, and the cleanup), **status**
(`pending` / `in progress` / `awaiting test` / `done`). Cost taxonomy
ordering the plans: free local work first, slow multi-gigabyte local
builds sequenced deliberately, shared public state (GHCR, GitHub) last.

## Pointers

- `.claude/refs/image-contract.md` — hosting-platform image contract
  (operator-supplied, read-only): read before designing any image's
  operator interface (env vars, ports, writable paths, configuration,
  shutdown, health, saves). Information, never a requirement source;
  conflicts with the spec are questions for the operator.
- `.claude/docs/` — working memory, per-topic files:
  - `permissions.md` — what the permission rules, the PreToolUse hook
    and workspace trust actually do, measured on the running Claude Code
    version. Read before editing `.claude/settings.json` or
    `.claude/hooks/`, before relying on any enforcement claim, and
    re-measure after a Claude Code update (the file says how).
- **Tooling templates** (delete this block, the directory and every
  pointer to it in one commit once every template is adopted or
  dropped): `.claude/spec-work/handoff/assets/` holds starter skills
  (`orient`, `resume-step`, `handover-step`, `approve-step`) and agents
  (`step-reviewer`, `optimize-memory`, `state-reviewer`,
  `code-reviewer`, `test-reviewer`) — the one readable path under
  `.claude/spec-work/`, rule 1's standing exception. Not yet adopted:
  all of them (step-002 instantiates the certain-trigger set;
  `code-reviewer` and `test-reviewer` adopt at step-sc-001, whose
  Dockerfile and smoke test are their triggers). A name on this list
  is the documented fallback, not a dangling reference.
