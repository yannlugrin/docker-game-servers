# The permission baseline, as measured

Working memory, lazily loaded. Every claim here was **measured on a stated
version by a stated method**, and carries a recipe to re-measure it. Nothing
here is taken from documentation, from the guard's own docstring, or from
`PLAN.md` — all three are belief until a probe agrees, and this file exists
because a permission mechanism that quietly enforces nothing announces
nothing.

**When to read it:**

- **before changing `.claude/settings.json` or the guard's registry** —
  sections 2 and 3;
- **before relying on a permission mechanism to stop something** — section 1,
  and section 5, which lists what is *not* yet proven;
- **after a Claude Code update** — re-measure with section 6, and update the
  figures **and their version stamp**.

Measured on **Claude Code 2.1.234**, 2026-08-17, at `step-002`.

---

## 1. What the installed version actually does

| Claim | Measured | Method |
|---|---|---|
| `permissions.defaultMode` exists as a settings key | **Yes** | the binary carries its own diagnostics for it, e.g. `settings defaultMode "…" is not supported in CLAU…` |
| Valid modes | `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, `plan`; **`manual` is an alias for `default`** | binary strings; `claude --help` lists the session flag's choices |
| **`auto` cannot be set from a project settings file** | **Confirmed** — ignored as repo-controllable | binary: `an "auto" defaultMode in project .claude/settings.json or .claude/settings.local.json is ignored`, plus a runtime message `settings defaultMode "auto" ignored` |
| `dontAsk` **auto-denies** instead of prompting | **Confirmed** | binary: a tool call is *auto-denied without an interactive permission prompt* under `dontAsk`, alongside the auto-mode classifier and deny rules |
| A `deny` rule overrides a hook's `allow`/`ask` | **Confirmed** | binary: `PreToolUse hook denies, and deny-rule overrides of hook allow/ask decisions` |
| An `ask` rule forces a prompt | **Confirmed** | binary: `Set when a user-configured ask RULE (permissions.ask) forced this prompt` |
| `autoMemoryEnabled` is a real key | **Yes** — `isAutoMemoryEnabled` is evaluated | binary strings |

**Two behaviours turned out to depend on the mode**, so both were measured
twice — first under `auto` (the session that wrote the proposal) and again
under `acceptEdits` (the committed baseline, in a restarted session). Where
they disagree, **`acceptEdits` is what binds**, because that is what ships.

| Behaviour | Under `auto` | Under `acceptEdits` |
|---|---|---|
| `touch ../escaped-probe.txt` from the project root, with `Bash(touch:*)` allowed | **succeeded silently** — no working-directory boundary | **prompted** — the boundary holds and outranks a matching allow rule |
| the implementer editing `.claude/settings.json` | **refused** by the auto-mode classifier | **succeeded** |

The second row is the uncomfortable one and is stated plainly rather than
buried:

**Under the committed baseline, the implementer can edit its own permission
boundary.** It edited `.claude/settings.json` to add one entry, and — during
the fail-open probe below — disabled the guard entirely with `chmod -x`, a
command the allow list permits. Neither action prompted. The `deny` list is no
better protected: it lives in the same editable file.

So the honest statement of what this baseline is for: **it stops mistakes, not
a determined agent.** It makes an outward write announce itself, it puts an
irreversible act in front of the operator, and it fails loudly when the guard
dies. What actually bounds a determined implementer is the operator reading
the diff — which is why every change here lands in a reviewed commit. Section
7 proposes the hardening that would close the casual half of this.

## 2. The guard

`.claude/hooks/bash_guard.py`, instantiated from the handoff template with
**only its `REGISTRY` edited**, as the template requires. Four tools:

- **`git`** — the template's ground rules, unchanged, worktree rules kept
  (this repository uses worktrees under `.claude/worktrees/`).
- **`docker`** — the template's rules, unchanged. They already map onto rule 9
  exactly: publishing asks, host-global prunes ask, removing this project's
  own containers and images by name stays silent.
- **`gh`** — new. Grants, not rules: rule 9 rules GitHub API *reads* free and
  gates every write, and the reads are the finite side to enumerate.
- **`steamcmd`** — new. Grants over a vocabulary, so an anonymous download or
  metadata query is silent and a credential is not.

`just` and `pre-commit` are deliberately **absent**. A registry entry with no
rules, grants or handoff is silence, which is what an unregistered tool
already gets. What keeps them safe is rule 2's invariant — *no justfile recipe
ever performs an act rule 9 gates* — which lives outside this file and has to
be honoured whenever a recipe changes.

**Measured costs** (this machine, section 1's version): `--liveness` **0.03 s**,
`--selftest` **0.04 s**, `scripts/check_settings_hooks.py` **0.01 s**. The
liveness gate is in the commit path, so its cost is paid on every commit; at
30 ms it is not worth optimising.

**The liveness gate caught a real mistake while this step was being written.**
A first draft of the `gh` help/version grant carried no condition at all;
`--liveness` refused it with *"gh grant: matches everything, so the tool is not
gated at all"*. It was rewritten with `require_any`. Recorded because it is the
only direct evidence that this mechanism catches something rather than merely
passing.

**Both gates are wired, and they ask different questions.** `--liveness` runs
in `pre-commit` on **every** commit — `always_run`, not keyed on the guard's
own path, because one of the deaths it exists to catch is a **rename**, and a
path-keyed hook would be skipped by the very commit that broke it.
`--selftest` is `just test`: liveness, then all 133 registry cases and 174
engine cases, then coverage — **57/57 rules and grants reached by a case**, and
a rule no case reaches fails the run.

## 3. The settings, as installed

Proposed by the implementer, reviewed and **applied by the operator** on
2026-08-17, with `Bash(cd:*)` added afterwards (section 5 says why). The file
itself is the authority; this listing is here so the reasoning below has
something to point at.

```json
{
  "autoMemoryEnabled": false,
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(git:*)", "Bash(docker:*)", "Bash(gh:*)", "Bash(steamcmd:*)",
      "Bash(just:*)", "Bash(pre-commit:*)", "Bash(python3:*)",
      "Bash(cd:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)",
      "Bash(grep:*)", "Bash(rg:*)", "Bash(find:*)", "Bash(wc:*)",
      "Bash(sort:*)", "Bash(uniq:*)", "Bash(cut:*)", "Bash(tr:*)",
      "Bash(sed:*)", "Bash(awk:*)", "Bash(diff:*)", "Bash(file:*)",
      "Bash(stat:*)", "Bash(du:*)", "Bash(df:*)", "Bash(free:*)",
      "Bash(nproc:*)", "Bash(uname:*)", "Bash(which:*)", "Bash(echo:*)",
      "Bash(printf:*)", "Bash(basename:*)", "Bash(dirname:*)",
      "Bash(readlink:*)", "Bash(realpath:*)", "Bash(date:*)", "Bash(jq:*)",
      "Bash(mkdir:*)", "Bash(cp:*)", "Bash(touch:*)", "Bash(chmod:*)",
      "Bash(xargs:*)", "Bash(tee:*)"
    ],
    "ask": [
      "Bash(curl:*)", "Bash(wget:*)"
    ],
    "deny": [
      "Bash(git push --force:*)", "Bash(git push -f:*)",
      "Bash(git push --force-with-lease:*)", "Bash(git push --mirror:*)",
      "Bash(git filter-branch:*)", "Bash(git filter-repo:*)",
      "Bash(git reflog expire:*)", "Bash(git reflog delete:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/bash_guard.py"
          }
        ]
      }
    ]
  }
}
```

Why each part is shaped that way:

- **A broad allow per registry tool, and the guard claws back.** That is the
  whole pairing: broad allow plus a narrow hook replaces a long, brittle allow
  list. A gated tool with no allow line would prompt on everything and its
  grants would never be reached.
- **No `ask` rule for anything the guard gates.** A matching `ask` prompts
  *even where a hook returns allow* (section 1), so one `ask Bash(gh:*)` would
  cancel every carve-out the registry expresses. `ask` is left for tools with
  no registry entry: `curl` and `wget`, whose job is fetching things that are
  not pinned in the repository — outside rule 9's free boundary.
- **No prefix rule restating a guard decision.** `Bash(git push:*)` misses
  `git -C dir push`, which the guard catches; two sources of truth, the weaker
  one winning nothing. `git push` is gated in the guard's ground rules and
  **asks and is never denied**, because a denied pattern cannot be approved in
  the very exchange rule 9 relies on.
- **A short `deny` backstop, and it is the one deliberate duplication.** A
  hook fails open — a syntax error, a lost `+x`, a missing `python3`, and
  Claude Code proceeds to the permission rules with the guard's opinion
  missing. Under a *narrow* allow list a dead guard costs extra prompts; under
  `Bash(git:*)` it costs an unprompted `git push --force`. The broad allow and
  this list are a package. It is kept to eight entries, all of them permanent
  history loss, so the exception stays visible as one.
- **`rm` and `mv` are deliberately not allowed**, and will prompt. Rule 9 does
  rule removing *this project's own* artifacts free, but that is a **path**
  condition and an allow rule cannot express one. They were first excluded
  because no working-directory boundary had been observed; that premise
  changed when the boundary turned out to hold under `acceptEdits` (section 1),
  which would in principle bound a broad `Bash(rm:*)` to the project. They stay
  out anyway, on one observation from a prompt the operator declined — enough
  to know a boundary exists, not enough to know whether it blocks or merely
  asks. Revisit with a real measurement if the prompting proves noisy; the
  alternative answer is a guard entry with path-scoped grants, built when it
  bites rather than in anticipation.

**The mode, and why not the others.** `acceptEdits` auto-accepts file edits
while leaving Bash to the rules and the guard, which is what removes any need
for a blanket `Edit(/**)` allowance. The alternatives are ruled out by
measurement, not preference: `auto` is **ignored** in a project settings file;
`dontAsk` **auto-denies** rather than prompting, which would destroy the
operator's ability to approve in-exchange — the thing rule 9's boundary and
rule 6's push-at-close both depend on; `bypassPermissions` removes the gate
entirely; `plan` is a working mode, not a baseline. That leaves `default` and
`acceptEdits`, and `default` prompts on every file edit, which is how an
operator ends up reaching for a looser mode — the failure the whole design is
trying to avoid.

**What a dead guard leaves open, stated plainly.** With this baseline and a
guard that never runs: every `git` and `docker` subcommand except the eight
denied ones proceeds unprompted — including `docker push` to GHCR, `docker
system prune`, `git reset --hard`, `git clean`; every `gh` write proceeds,
including `gh workflow run` and `gh release create`; and `steamcmd` runs with
any credentials. That is a materially wider surface than a narrow allow list
would have been, and it is exactly why `--liveness` sits in the commit path
and why the deny list exists.

**The widest single entry is `Bash(python3:*)`**, and it is worth naming: the
guard does not read `python3 -c` program text (its docstring says so), so a
broad python3 allow can reach anything the guard would otherwise gate. It is
proposed because this repository's harness, its guard and its checks are
Python and the development loop runs it constantly. The alternative is to drop
it and accept a prompt on every Python invocation. **This is a judgement for
the operator, not the implementer.**

## 4. The three-command liveness probe

The check `step-004`'s session rituals run, and the **only** thing that says
the hook is *reached*. `--liveness` and `--selftest` both answer whether the
file is correct, never whether anything calls it.

| Command | Must do | Reads |
|---|---|---|
| `gh run list` | run silently | the `gh` read grant |
| `git commit -m "$(date)"` | be **granted** — no prompt despite the substitution | the one `allow` rule |
| `docker system prune --help` | be **refused, naming the rule** — "this sweep is host-global and reaches other projects on this machine" | the `docker` sweep rule |

The third is the decisive one. If it merely prompts generically, or simply
runs, **the hook is not wired**: the settings' deny backstop is then the only
thing left, while `--liveness` and `--selftest` would both still pass.

**`--help` is not decoration on that third command.** The rule matches on the
subcommand path, so `docker system prune --help` reads the same rule as the
bare form — but if the hook turns out *not* to be reached, `Bash(docker:*)`
allows whatever was typed and it runs. The bare form would then prune this
host, and `environment.md` §3 records that this daemon holds another project's
running container and 7.5 GB of build cache. A probe whose failure mode is
destroying someone else's work is the wrong probe; this one costs a usage
message.

The second command is safe for a similar reason worth stating: with nothing
staged, `git commit` creates nothing whatever the guard decides. Run it on a
clean index, never as a way to make a commit.

## 5. The probe results, and what activation costs

**Installing the settings does not make the guard live.** Measured
2026-08-17, immediately after the operator applied section 3, in the session
that had proposed it: `scripts/check_settings_hooks.py` reported 1/1 resolved,
`gh run list` ran silently — and **`docker system prune --help` ran** instead
of being refused. Fed the same command directly, the guard answered `ask`,
naming its rule. The guard was correct and was not called.

The cause is in the installed version's own words: the settings watcher *"only
watches directories that had a settings file when this session started"*, and a
newly added hook needs **`/hooks` opened once, or a session restart**. Sound
behaviour — the alternative is an agent granting itself a hook by editing a
file. **A mode set in settings binds the next session too, not the one that
wrote it.**

**This is the exact failure this file exists to catch, and every gate was green
throughout it:** `--liveness` passed, `--selftest` passed 133 + 174 cases at
57/57 coverage, the pointer check passed. All three answer whether the guard is
*correct*, never whether anything *calls* it.

### After the restart — all three probes pass

| Probe | Result |
|---|---|
| `gh run list` | **silent** |
| `git commit -m "$(date)"` | **granted** — no prompt despite the substitution, so the one `allow` rule works |
| `docker system prune --help` | **refused, naming its rule** |

The third came back as `Hook PreToolUse:Bash requires confirmation for this
command: this sweep is host-global and reaches other projects on this machine
[rule docker system prune]`. That the prompt is attributed to the hook, carries
the guard's own reason, and appears **despite `Bash(docker:*)` being allowed**,
is what proves the hook is reached and outranks the broad allow.

**Run each probe as a bare command.** Measured the hard way: a compound line
(`cd … ; git status ; gh run list`) prompted on `cd`, which was missing from the
allow list — a result that says nothing about the probe. Permission rules are
matched per command in the line. `cd` has since been added.

### A hook fails open — proven, not assumed

The premise the whole `deny` backstop rests on, measured directly:

1. `docker system prune --help` — **refused**, naming its rule.
2. `chmod -x .claude/hooks/bash_guard.py`, then the same command — **it ran, no
   prompt at all.** The broad `Bash(docker:*)` allow carried it straight
   through.
3. `chmod +x` restored, same command — **refused** again.

So a guard that dies takes its opinion with it and everything falls back to the
permission rules, silently. That is why `--liveness` sits in the commit path,
and why the `deny` list is worth its duplication. It is also why `chmod` being
in the allow list is a loose end (section 7).

### Still unproven

- **Which spelling of a path rule the file tools match** (`Edit(.claude/x)` vs
  `Edit(./.claude/x)` vs an absolute form). Not yet probed, and section 7's
  proposal depends on the answer. The cheap method is a `deny` rule, whose
  effect the implementer can observe directly without an operator prompt.

## 7. Proposed hardening — not applied, for the operator

Section 1 measured that the implementer can edit `.claude/settings.json` and
can `chmod -x` the guard, neither with a prompt. Two changes would close the
casual half of that, and both are the operator's call:

1. **An `ask` rule on the boundary's own files** — the settings file and
   `.claude/hooks/**`. `ask` rather than `deny`, so the operator can still
   approve a legitimate registry change in-exchange; a `deny` cannot be lifted
   in the exchange that needs it. This also makes mechanical what the guard's
   docstring already requires in prose: *every rule change is the operator's
   call*. Needs the path-spelling probe above first.
2. **Drop `Bash(chmod:*)` from the allow list.** It is rarely needed, and it is
   the one allowed command that can disable the guard outright. Prompting on it
   costs almost nothing.

Neither is applied. Both are recorded here so the gap is visible rather than
discovered.

## 6. Re-measure recipe

Run after any Claude Code update, and update the version stamp with the
figures.

```sh
claude --version
B=$(readlink -f "$(which claude)")
strings -el "$B" | grep -i 'defaultMode'          # modes, and which are ignored
strings -el "$B" | grep -i 'autoMemory'           # the memory key still exists
strings -el "$B" | grep -iE 'auto-denied|deny-rule overrides'

.claude/hooks/bash_guard.py --liveness            # structure and contract
.claude/hooks/bash_guard.py --selftest            # behaviour and coverage
scripts/check_settings_hooks.py                   # declared hook paths resolve

# the sandbox question, from the project root; remove the file if it appears
touch ../escaped-probe.txt && echo "NO SANDBOX" && rm -f ../escaped-probe.txt
```

Then re-run section 4's three commands and confirm silence, a grant, and a
refusal **naming its rule**.
