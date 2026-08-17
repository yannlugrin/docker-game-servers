# Subagents, as measured

Working memory, lazily loaded. What the installed Claude Code actually does
with an agent definition — measured, never taken from documentation or from a
template's claim about some other project.

**When to read it:**

- **before writing or editing an agent** under `.claude/agents/` — sections 1
  and 2 say what its frontmatter does and does not buy;
- **before relying on an agent's `tools:` list to prevent something** —
  section 2, and section 2's limit above all;
- **before assuming a subagent can see the standing instructions** —
  section 1, which is what every reviewer's boundary rests on;
- **after a Claude Code update** — re-measure with section 4.

Measured on **Claude Code 2.1.234**, 2026-08-17, at `step-003`. The permission
mechanisms are a different class of fact and live in `permissions.md`; they
share a re-measure moment but not a read trigger, which is why this is its own
file.

---

## 1. `CLAUDE.md` reaches a subagent's context

**Result: yes, by the same injection path a main session gets.**

Method: `step-reviewer` was spawned over `step-002..HEAD` — a real review, not
a synthetic errand — and asked, as part of its report, to state whether
`CLAUDE.md` was in its context, to **quote rule 9's opening line verbatim**,
and to say whether the text arrived on its own or had to be fetched with a
tool. That last distinction is the measurement: an agent that answers by
calling `Read` on `CLAUDE.md` proves nothing, and would pass a probe that
should fail.

What came back:

- rule 9's opening line, quoted exactly:
  `**9. Bug reports on the current step are yours to drive.**`
- delivered **before its first tool call**, as project instructions headed
  "Codebase and user instructions are shown below", containing the full file;
- `Read` was **never** called on `CLAUDE.md` at any point in the run.

**Consequence: the pre-committed unfavourable branch does not fire.** The
three agents cite rule 9 rather than carrying their own copy of the gated set,
which is the single-source-of-truth form. Had this come back the other way,
each body would have inlined the gated set, logged with its cost.

**The self-check stays anyway.** Each agent still opens by stopping and
reporting if it cannot see rule 9. It costs a paragraph, and it is what makes
a later regression — a version change, a different spawn path — announce
itself during a real run instead of producing a confidently unbounded review.

## 2. An agent's `tools:` frontmatter binds

**Result: yes, by omission. An unlisted tool is absent, not refused.**

Method: the same run. `step-reviewer` declares `tools: Read, Bash`, and was
asked to enumerate every tool actually available to it. It reported **exactly
`Read` and `Bash`** — no `Write`, no `Edit`, and none of the search or
task-spawning tools the main session has. It did not report a refusal, because
there was nothing to refuse: the tools were simply not offered.

**The limit, which matters more than the result.** `tools:` restricts *which
tools exist*, not *what they can do*. `step-reviewer` holds `Bash`, and `Bash`
writes files — so its "strictly read-only" discipline rests on the prose
instruction in its body, **not** on its tool list. Anything that must be
mechanically unable to write needs `tools: Read` alone, and then needs another
way to obtain a diff. Do not read section 2's result as "the reviewers cannot
modify anything".

**Two things this measurement did not cover**, stated so silence is not
mistaken for coverage:

- the clean `tools: Read` case, with no `Bash` escape hatch. A throwaway agent
  for it exists at `.claude/agents/probe-tools-binding.md` **only if a probe is
  in flight** — it is deleted after use, so its presence in a committed tree is
  a missed cleanup. It cannot be run in the session that creates it (below).
- whether a *listed* tool name that does not exist is dropped silently. The
  template warns it is; not verified here, and the way to avoid needing the
  answer is to check the running build's tool inventory before editing a
  `tools:` line.

## 3. A new agent is picked up only at session start

**Result: confirmed, and it costs a restart.**

Method: `.claude/agents/probe-tools-binding.md` was created mid-session and
immediately spawned. The attempt failed with `Agent type
'probe-tools-binding' not found`, listing the agents loaded when the session
began. The three agents adopted at `step-003` became available only after a
restart.

Consequence for every later step: **an agent added or renamed during a step
cannot be tested in that step's own session.** The step's test instructions
must say "restart first", and a ritual that spawns a newly created agent
would fail for a reason that looks nothing like the cause.

## 4. Re-measure recipe

Run after a Claude Code update, and update the version stamp with the results.

```sh
claude --version
```

Then, from a session started **after** any agent files changed:

1. **Reach.** Spawn `step-reviewer` on any real diff and add to the prompt:
   *"state whether `CLAUDE.md` is in your context, quote rule 9's opening line
   verbatim, and say whether it was already there or you read it with a
   tool."* A quote obtained by calling `Read` is a **failed** probe.
2. **Binding.** In the same run, ask it to list every tool available to it.
   Expect exactly the pair its frontmatter names.
3. **Binding, clean case** (optional, costs a restart): create an agent with
   `tools: Read`, restart, spawn it, ask it to write a file under the
   gitignored `.claude/reviews/`, and record whether the write is **absent**,
   **refused**, or **succeeds**. Delete the throwaway afterwards.

If step 1 comes back unfavourable, the pre-committed response is in D-011:
inline the gated set into each agent body, logged with its
single-source-of-truth cost — never a citation to a rule the agent cannot
read.
