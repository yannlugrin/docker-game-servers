# Workflow mechanics and the reasoning behind the rules

Working memory, lazily loaded. `CLAUDE.md` states the rules; this file holds
the shapes they take and the reasons they exist, so `CLAUDE.md` can stay
small enough to load every run.

**When to read it:**

- **before amending a specification** — section 0;
- **before opening, handing over or closing a step** — sections 1, 3 and 5;
- **before moving a step to another track, or renumbering one** — section 5,
  which carries what a move silently drops;
- **before instantiating a tooling template** under `.claude/skills/` or
  `.claude/agents/` — section 2;
- **when a rule's reason matters** — before applying one to an awkward case,
  and always before proposing to change one — section 6.

`/handover-step` and `/approve-step` exist as of `step-004` and carry the
**order** of their own rituals — what to run, in what sequence, and what only
the ritual can know. **The shapes stay here and are not copied into them:**
the compacted plan entry is §1, the tag message §5, the two milestone passes
§3, and a close reads those sections rather than a transcription that can
drift. `CLAUDE.md` carries no plan conventions — that section moved here at
`step-002` (`DECISIONS.md` D-002), so §1 is the tie-breaker on entry shape,
not `CLAUDE.md`.

---

## 0. Amending a specification (rule 1 mechanics)

The rule: specifications are read-only, and a change happens only through a
logged decision landing in the same commit as the amendment. The mechanics:

- **The decision entry is written before the amendment**, never as a
  rationalisation after it.
- **One commit carries the entry and the specification text and nothing
  else** — no code, no documentation fixes. Subject names the decision:
  `step-pz-012: spec amendment — D-NNN, <what changed>`.
- **Code, and any documentation the amendment makes stale, follow in the
  step's later commits.** For amendment commits this beats rule 6's
  same-commit staleness sweep; the two rules would otherwise collide with no
  winner.
- **The entry lands alone** only when the amendment belongs to a later step —
  and then it says so and names that step.
- The log follows **the document being amended**, not the step doing the work
  (rule 4): a `pz`-track step amending the root specification logs in the root
  log. An amendment touching both specifications is two entries, one per log,
  cross-citing.

## 1. Plan-step entry shape

An **open** step entry carries:

- **objective** — one sentence on what will exist afterwards;
- **spec sections implemented** — the review checklist for the step;
- **depends on** — what must be `done` first. **A step's dependency line, not
  its position, is what sequences it**, within a track as much as across
  tracks;
- **deliverables** — what the step decides or builds *beyond* the
  specification, citing sections for the rest. The six foundation steps are
  the deliberate exception: they carry their bootstrap prescriptions in full,
  because the prompt that stated them is consumed once;
- **how I test it** — exact commands and what the operator should observe.
  **Where the test crosses rule 9's boundary, it says so, what it costs, and
  how to clean up afterwards.** A cost that is free but slow (a
  multi-gigabyte Steam download) is stated too;
- **status** — `pending` / `in progress` / `awaiting test` / `done`.

**On approval the entry keeps none of that.** It is replaced, not annotated:

    ### <step id> — <step title> — `done`

    - **Outcome (approved YYYY-MM-DD, tag `<step id>`):** what now exists and
      what it decided, in a few lines, citing the decision entries it rests
      on. Detail in git history between tags `<previous step tag>` and
      `<step id>`.

`<previous step tag>` is the `step-*` tag immediately before this one **of
any track** — history is linear repository-wide, so a track's own previous
tag may have another track's steps between it and this one.

Why replace rather than annotate: the entry described intentions the step
itself has since changed, and it sits in a file every session reads at start.

## 2. Governance placeholders in tooling

Each template under `.claude/skills/` and `.claude/agents/` is instantiated
**once**, repository-wide. Ordinary placeholders are filled with this
repository's real commands and paths. The governance set —
`{{PLAN}}`, `{{DECISIONS}}`, `{{SPEC}}`, `{{STEP_ID}}` — is the exception to
literal filling: it resolves to the **active track at invocation**, from the
track map and `CLAUDE.md`'s `Current state` pointer, never to one literal
path. On a `pz`-track step, `{{SPEC}}` includes the root specification.

**One exception, and it is the one that fails silently:** rituals fired as
part of *closing* a step — the milestone state review and the memory
compaction above all — key on the track of the step **just closed**, named
explicitly at spawn, never on the pointer. The close ritual advances that
pointer before it fires them, so at a cross-track milestone boundary
resolve-at-invocation would aim both passes at the wrong track, and a state
reviewer reading the wrong track's plan reports nothing wrong.

Two further rules on instantiation:

- **A template arrives with placeholders on purpose:** a leftover one is
  visible, a plausible wrong filename is not. Fill a placeholder with a
  verified real path, or leave it as a placeholder — never guess.
- Where a template's own enumeration of a routine is **narrower than the rule
  it claims to execute**, the rule wins and the enumeration is rewritten to
  match. A ritual that reads less than the rule it executes is a ritual that
  skips reading.

## 3. Closing a milestone

Two passes, in this order, both mandatory whoever performs them:

1. **The whole-state review** — everything `done`, judged as one system
   against the specifications and the decision logs.
2. **The memory-compaction pass** — completed plan steps compact to their
   outcomes, decision entries to their kernel (the decision, the reason that
   stops re-litigation, the approval), git history the sole archive.

Both run **from a clean context** and **on a model that did not write the
work** — not merely a model other than the current one, since a milestone can
span models. Pass the model override explicitly at spawn: neither agent pins
one, and omitting it means inheriting the caller's, which is the outcome to
avoid. `state-reviewer` and `optimize-memory` perform them where adopted;
otherwise brief a fresh subagent inline.

The review runs first so it reads uncompacted memory. **No forward obligation
may be orphaned by compaction:** anything still operative moves to the plan
step, decision log or `.claude/docs/` file that will need it, in the same
pass.

Without milestones, run the same compaction whenever the memory files have
grown noticeably.

## 4. Why `Current state` is a closed list

`CLAUDE.md`'s `Current state` holds a closed list of item kinds: the current
and next step, live world-state, open obligations, and the `.claude/docs/`
pointers. **What a closed step produced is not one of them** — its outcome
belongs in its plan entry and its tag, a durable fact in `.claude/docs/`, an
invariant in a decision log — so a close **deletes** that paragraph rather
than demoting it.

The reason is measured, not theoretical: without the closed list, each close
adds one reasonable paragraph, every one defensible on its own, and the
section becomes a changelog. It was measured once at 131 lines.

## 5. The harness contract, and the closing tag (rule 2 and rule 6 mechanics)

**The three entry points.** `just check <scope>` asks "is what is committed
here well-formed?" — syntax, lint and formatting, untracked files included,
gitignored paths and the two standing path exclusions
(`.claude/spec-work/`, `.claude/refs/`) out. `just test` asks "is the
implementation right?" — fixtures and expectations over the behaviour **this
repository itself ships**, the cases that must fail included. `just verify`
runs both.

**Three limits that keep `test` honest:**

- a third-party tool is never retested;
- a must-warn case is required only where the implementation already defines a
  warning tier — never a reason to invent one;
- where the repository ships no behaviour of its own yet, a `test` command
  that says so is the correct state, not a gap to fill.

**Never ahead of need.** Every artifact class the repository ships gets a
check family, and a family — with its fixtures — arrives **with the first file
of its class, in the step that lands it**. A family for an artifact the
repository does not yet contain is scaffolding, not coverage. Two families
belong on the list whatever the stack: **governance well-formedness** (skill
and agent frontmatter parse, `.claude/settings.json` parses, the hook path in
it resolves) and **prose lint over the governance documents**, configured to
them as they already are — the specifications are read-only, so the lint bends
to them and never the reverse, and excluding a document from a rule is a
logged decision, not a quiet config line.

**Scope at the gate.** A narrowed `check` is legitimate mid-step; the commit
that receives a step tag runs the full scope.

**The annotated tag** on a closing commit carries: a title line
`<step id> — <step title>`, then `Approved YYYY-MM-DD.`, then a short
paragraph of the step's notable outcomes. Write it as the plan entry's outcome
bullet expanded, in the same commit-and-tag pass, so the two cannot disagree.

**Renumbering.** A step's number freezes when it enters `in progress`.
`pending` steps may be renumbered; a renumbering commit sweeps every step
reference in that track's plan and in the decision logs, and decision entries
cite not-yet-started steps by number **plus title**, so a missed sweep stays
decodable.

**Moving a step to another track: restate what its position guaranteed.**
Measured once, at the bootstrap. When the builder image moved from a
root-track step sitting after the foundation into its own track, it kept its
content and its explicit dependency — and silently lost the sequencing it had
been getting from *position*, which was that the whole foundation came first.
Three verification passes (references resolve, coverage intact, cross-track
edges symmetric) all came back clean, because each asked *is this internally
consistent?* and none asked *did something that used to be guaranteed stop
being guaranteed?* Nothing reports this class of regression.

So, before moving a step across tracks or plans: list what its old position
implied — what ran before it, what it could assume existed — and restate each
as an explicit dependency edge in both plans' cross-track tables. Prefer
restating an **inherited** edge at both ends over relying on the chain: an
inherited edge is invisible in the file that depends on it, and is the first
thing a later move drops.

## 6. The reasons behind the rules

`CLAUDE.md` states these rules without their justifications, to stay inside
its budget. The reasons live here so they are recoverable rather than lost —
above all before anyone proposes changing a rule.

**Rule 1 — specifications read-only.** The decision entry precedes the
amendment so the record is reasoning, never rationalisation. Both land in one
commit because a commit where the log and the specification disagree is a
state a session can resume onto and misread as drift; and `git blame` on an
amended line must land on a diff carrying the reasoning. Code stays out so
`git log -- SPECIFICATIONS.md project-zomboid/SPECIFICATIONS.md` remains a
readable history of amendments. Silent drift between specification and
implementation is the failure this rule exists to prevent.

**Rule 1 — escalation beats pre-commitment.** A pre-committed response fixes
what will happen, not who watches it land. An outcome that moves a
requirement, a variable's tier, a documented capability or limitation, or the
ship decision is the operator's call even where the specification already
wrote down what to do about it.

**Rule 2 — the gate is behaviour, not typos.** The operator's gate exists to
judge behaviour against the real world; the harness catches everything else,
which is why nothing is handed over unverified. A check family for an
artifact the repository does not yet contain is scaffolding, not coverage —
hence never-ahead. A third-party tool is never retested: that shellcheck
reports SC2086 is its maintainers' problem.

**Rule 2 — the full check at the tag commit.** A narrowed check is legitimate
mid-step, but the commit receiving a step tag is the state every later session
treats as known-good, so it runs the whole thing.

**Rule 2 — no gated act in a justfile recipe.** The Bash guard sees
`just release`, never the `docker push` inside it. Gated acts therefore live
in CI or in a command the operator invokes directly.

**Rule 2 — measurements never live in standing instructions.** A
version-stamped fact restated in `CLAUDE.md` outlives its version in silence.
`.claude/docs/` files carry the version, the method and a re-measure recipe;
`CLAUDE.md` carries only the pointer.

**Rule 3 — the budget.** `CLAUDE.md` loads on every run, so its size is paid
constantly. A file at its cap forces the next session that must add one
pointer to reflow the whole document first, which is why it is written with
headroom. The eviction order is fixed so the cheapest thing to delete is
never the thing with nowhere else to go.

**Rule 3 — auto memory stays off.** It is machine-local and unversioned: a
second memory outside git, outside review and outside these rules.

**Rule 3 — `.claude/refs/` is not this repository's.** Its authority is the
source it came from, so rule 1's amendment channel does not apply: there is
nothing to decide. A reference that looks wrong is reported; what you learned
that made you doubt it goes in your own files, never edited into the
operator's document.

**Rule 6 — one step in progress repository-wide.** History stays linear and
the last `step-*` tag remains the single last-approved state that
re-orientation depends on. Step numbers are identifiers, not positions: a
number freezes when the step enters `in progress` because commits and its tag
reference it from then on.

**Rule 6 — same-commit staleness.** Documentation updated later is
documentation that drifts.

**Rule 6 — the push attempt at a close.** That is the moment the operator
wants the commit and its tag published and the moment they forget to say so,
and the permission gate puts the question to them. It is an exception to
cite, never a pattern to extend: nowhere else is a gated act attempted
because something downstream might catch it.

**Rule 9 — the boundary's shape.** Destructive-local splits on blast radius,
not on the verb: this project's own artifacts are rebuildable working
material, while an unscoped sweep reaches other projects on the host. The
Steam master-server registration a local test server performs is an outward
write ruled free deliberately — the listing is transient, names an ephemeral
test server, and delists on stop.

**Rule 11 — why a rule asks for less.** Every other rule rewards
thoroughness, so nothing else in them ever asks for restraint. Before writing
a runner, installer, discovery library or test driver, ask whether the
ecosystem ships one: that question costs a sentence, and skipping it has cost
six hundred lines. A clean review is not evidence the work was worth doing.
