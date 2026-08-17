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

**The session this was measured in ran in `auto` mode**, which was not assumed
but proven the hard way: writing `.claude/settings.json` came back
`Permission for this action was denied by the Claude Code auto mode
classifier`. Two consequences, both load-bearing:

- **The implementer cannot install its own permission baseline.** That is the
  correct behaviour — an agent editing the file that bounds it is exactly what
  a classifier should stop — and it matches `CLAUDE.md`'s ruling that this
  baseline is outside the implementer's latitude. Section 3 is therefore a
  proposal for the operator to apply, not a description of what is installed.
- **No working-directory sandbox was observed.** `touch ../escaped-probe.txt`
  from the project root **succeeded** and created the file outside the
  repository (removed immediately). The guard's docstring describes a sandbox
  that blocks exactly this when a command is merely permitted by a rule; under
  `auto` mode on this version, it did not. **So nothing in section 3 leans on
  a sandbox**, which is why no broad allow is proposed for `rm` or `mv`.
  Re-measure under the proposed mode once it is applied — the result may
  differ, and the conservative allow list stands either way.

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

## 3. The proposed settings — for the operator to apply

The implementer cannot write this file (section 1). Proposed content for
`.claude/settings.json`:

```json
{
  "autoMemoryEnabled": false,
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(git:*)", "Bash(docker:*)", "Bash(gh:*)", "Bash(steamcmd:*)",
      "Bash(just:*)", "Bash(pre-commit:*)", "Bash(python3:*)",
      "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)",
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
  rule removing *this project's own* artifacts free, but that boundary is a
  path condition, and section 1 measured that no sandbox enforces one here. A
  broad `Bash(rm:*)` would be unbounded. If the prompting proves noisy, the
  answer is a guard entry with path-scoped grants, not a wider allow — built
  when it bites, not in anticipation.

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

## 5. Installing the settings does not make the guard live

Measured 2026-08-17, immediately after the operator applied section 3, in the
session that had proposed it:

- `scripts/check_settings_hooks.py` reports **1/1 declared hook commands
  resolve** — the pointer is good.
- `gh run list` ran silently, and `git commit -m "$(date)"` was **not**
  prompted despite carrying a substitution.
- **`docker system prune --help` ran.** It was not refused. Fed the same
  command directly, the guard answers
  `ask — this sweep is host-global and reaches other projects on this machine
  [rule docker system prune]`.

So the guard is correct and **was not called**. The cause is in the installed
version's own words: the settings watcher *"only watches directories that had
a settings file when this session started"*, and a newly added hook needs
**`/hooks` opened once (which reloads config), or a session restart**. A hook
added mid-session does not take effect in that session — which is sound, since
the alternative is an agent granting itself a hook by editing a file.

**This is the exact failure this whole file exists to catch.** Both gates were
green throughout: `--liveness` passes, `--selftest` passes 133 + 174 cases at
57/57 coverage, and the pointer check passes — because all three answer whether
the guard is *correct*, never whether anything *calls* it. Until the probe in
section 4 comes back refused, the honest description of this repository is: the
deny backstop is the only mechanism actually enforcing anything.

### Still unproven, and to be settled in a session started after the install

1. **Whether the hook is reached** — section 4's third command must come back
   refused, naming its rule.
2. **Whether `acceptEdits` does what section 3 assumes** to an unmatched Bash
   command. The session measured above began before the mode was set, so it was
   still running under `auto`; a mode in a settings file binds the *next*
   session, not the one that wrote it.
3. **Whether a hook genuinely fails open** — remove the guard's `+x`
   deliberately and confirm a gated command proceeds to the permission rules
   rather than being blocked. Restore afterwards.
4. **Whether a working-directory sandbox exists under `acceptEdits`**, given
   section 1 measured none under `auto`.

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
