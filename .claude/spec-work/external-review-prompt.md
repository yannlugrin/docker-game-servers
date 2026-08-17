# External review prompt

Copy everything below the line into the other AI, and attach (or paste at
the end, clearly separated) the two specification files:

- `SPECIFICATIONS.md` (repository root)
- `PROJECT-ZOMBOID_SPECIFICATIONS.md`

---

You are an independent reviewer of a project specification. You have no
prior context on this project — that is deliberate; you are the fresh eyes.
The document is intended to be implemented by an AI coding agent without
supervision, so its quality gates that implementation. It has already been
through several internal review rounds; do not soften findings out of
politeness, and do not invent findings to seem thorough — disagreement is
acceptable, specificity is valued, and "nothing substantive found" is a
valid and useful verdict. Your findings will be triaged by the project's
operator, who accepts or rejects each one individually.

**What you are reviewing.** Two documents that together form one
specification for a public repository of Docker images running dedicated
game servers: a root `SPECIFICATIONS.md` (goal, environment facts, core
model, conventions every game image must obey, versioning, CI, and
documentation requirements) and a per-game `PROJECT-ZOMBOID_SPECIFICATIONS.md`
(the first game). The root document's §6 makes per-game documents part of
the specification. Inside the per-game document, references written `§N`
point to that document itself and references written `root §N` point to the
root document.

**The doctrine the documents claim to follow — hold them to it:**

- A reading contract with three tiers: requirements ("must" — closed
  decisions carrying their reasoning), recommended defaults ("should" —
  deviation with reason allowed), and environment constraints (researched
  facts, stated with the reason they matter).
- Reasoning attached to every non-obvious "must", so it can be evaluated
  rather than merely obeyed.
- A bias against silent failures: dangerous behavior must fail loudly, and
  prohibitions should name the silent failure they prevent.
- Precision proportional to risk: high-altitude where any competent choice
  works, specific where a wrong guess is expensive or silent. The document
  never prescribes implementation (no code, no file layouts, no tool
  syntax) — a missing mechanism is a defect only when its absence would
  make two reasonable implementations diverge in what an operator can
  observe.
- Honest scope edges: Non-Goals with reasons and blast radius, Future
  Considerations that must not be precluded, admitted open questions (the
  per-game document carries a deliberate list of open facts, each with a
  pre-committed response if it resolves unfavorably — an open item is a
  defect only if it could strand the implementation).

**What to look for:** comprehensibility problems; contradictions between
sections or between the two documents; gaps a reasonable implementation
would stumble into; silent-failure risks without a loud failure path;
requirements with no reasoning; misclassified tiers (a load-bearing
"should", a "must" that is really taste); implementation detail creeping
in; asserted facts you have grounds to doubt; ambiguity that forces the
implementer to guess; over- or under-specification relative to risk.

**Report structure (please follow it exactly):**

1. **Summary-back** — the project as you understood it, in your own words,
   a dozen lines at most. Comprehension mismatches are themselves findings
   for the authors to catch.
2. **Findings** — numbered, most severe first, each with: severity
   (blocking | important | minor), the section(s) concerned, the evidence
   (exact quote or precise paraphrase), and a suggested direction (not a
   rewritten text).
3. **Questions for the operator** — what you would need answered before
   trusting the document, numbered.
4. **Verdict** — one line: the count of blocking and important findings,
   and whether you consider the review quiet (nothing substantive found).

Also state, as one line in your report, whether every `§N`/`root §N`
cross-reference you followed resolved to an existing section.
