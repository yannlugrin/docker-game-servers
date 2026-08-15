# What the enforcement mechanisms actually do

Read this before editing `.claude/settings.json`,
`.claude/hooks/bash_guard.py`, or the frontmatter of anything under
`.claude/skills/` and `.claude/agents/`, and before assuming any
sentence below is still true: every claim here is a measurement, not a
reading of the documentation, and the mechanisms belong to a tool that
updates itself.

Everything down to the re-measuring section is the permission and hook
baseline of `step-001`; the frontmatter section that follows carries its
own version stamp.

**Measured on Claude Code 2.1.232 (native build, linux-x64), 2026-08-14,
at root `step-001`.** Each probe ran a separate non-interactive session
(`claude -p --output-format json`) that was asked to attempt exactly one
command; the outcome was read from the harness's own
`permission_denials` array, from the startup warnings on stderr, and in
one case from the hook debug log — not from the model's prose. Probes
are independent: one passing says nothing about another.

## Which side of the boundary each tool sits on

This is the thing to get right before reasoning about any of the rest.

`.claude/settings.json` allows `Bash(git:*)`, `Bash(docker:*)` and
`Bash(rm:*)` outright. **For those three tools the permission rules no
longer draw the line — the guard does.** They are allowed broadly on
purpose, because a prefix rule cannot express "a force push however it
is spelled", and the guard claws back the dangerous shapes by reading
parsed argv.

Every other command is the other way round: no allow rule matches, so
the permission rules prompt on their own and the guard, if it says
anything, only adds a reason to a prompt that was already coming.

That split decides what a broken guard costs, so it is repeated in the
fail-open note below rather than left to be inferred.

## Precedence, measured rather than assumed

| Probe | Result |
|---|---|
| Allowed command, allow rule present | Ran, no prompt |
| Command matching no rule | Refused (a prompt would have fired) |
| `deny` rule over a matching `allow` rule | Refused: "has been denied" |
| `ask` rule over a broader `allow` rule | Refused: "you haven't granted it yet" |

`deny` beats `ask` beats `allow`, and specificity never enters into it.
The two refusal messages differ, which is how a probe tells a hard denial
from a prompt that could not be shown in a non-interactive session.

The practical consequence: **an `ask` rule that overlaps an intended
`allow` rule silently cancels it**, and it cancels a hook's carve-outs
too, since a matching `ask` prompts even when a hook returned `allow`.
So no tool the guard gates may carry an `ask` rule in settings — the
exception belongs in the guard, as a `Grant`. The `ask` entries that
remain (`gh`, `curl`, `wget`) name tools the guard says nothing about.

## Where prefix matching runs out

Permission rules match a command's prefix, so a rule cannot constrain
what comes later in the same command. Measured:

- `Bash(git commit -m *)` in `allow` plus `Bash(git commit --amend*)` in
  `ask` **ran `git commit -a --amend -m probe` with no prompt**. The ask
  rule never matched, because one flag precedes `--amend`. Any allow rule
  on a command that takes flags has this shape.
- A compound command is checked per subcommand: with only
  `Bash(touch allowed-*)` allowed, `touch allowed-2.tmp && touch
  other2.tmp` was refused.
- A leading environment assignment does not evade an ask rule:
  `FOO=bar git push --dry-run origin main` was refused by
  `Bash(git push*)`.
- A command containing a command substitution is refused outright —
  "Contains command_substitution" — even when an allow rule matches its
  prefix. So `docker rm $(docker ps -aq)` cannot slip through an allow
  rule, and no guard rule is needed for that shape.

The first item is why `.claude/hooks/bash_guard.py` exists at all: it
decides on parsed argv, one subcommand at a time, so a flag is found
wherever it sits.

## What a PreToolUse hook can and cannot do

| Probe | Result |
|---|---|
| Hook returns `deny` while an allow rule matches | Call blocked |
| Hook returns `ask` while an allow rule matches | Call stopped for a prompt |
| Hook returns `escalate` while an allow rule matches | **Call ran** |
| Hook exits 1 after writing to stderr | Call ran |
| Hook script missing from the configured path | Call ran |

`escalate` is not a valid decision. Claude Code validates hook output
against a schema, and the debug log prints it:

> `"permissionDecision": "\"allow\" | \"deny\" | \"ask\" | \"defer\""`

An `escalate` output fails that validation, is discarded, and the call
proceeds to the permission rules — which is why it looked like a hook
could not force a prompt. It can: `ask` is honoured
(`Hook result has permissionBehavior=ask` in the debug log), and it
overrides a matching allow rule. In `claude -p` that shows up as a
refusal only because there is nobody to answer the prompt.

Two consequences shape the guard:

1. **A hook can force a prompt over a blanket allow.** So gating does
   not have to mean refusing: `git commit -a --amend` asks, and the
   operator approves it in the exchange rule 9 is written around. `deny`
   is kept for what has no authorized use at all.
2. **A hook is fail-open.** A missing, unreadable or crashing hook lets
   the call through silently — Claude Code logs the failure and falls
   back to the permission rules. What that costs depends on which side
   of the boundary the tool sits:
   - For `git`, `docker` and `rm`, the blanket allow is left standing
     with nothing in front of it: an unprompted `git push`,
     `docker system prune`, `rm -rf /etc`. The backstops are the `deny`
     list in settings — prefix-weak, so it catches `git push --force`
     but not `git push origin --force`, and unconditional — and the
     `--selftest`, which `just check` runs through pre-commit on every
     commit and `just test` runs directly, so a broken guard fails the
     lint before it lands.
   - For everything else, a dead guard costs extra prompts and nothing
     more.

`${CLAUDE_PROJECT_DIR}` in a hook's `command` resolves: the guard
blocked a call in this repository from a session started here.

## Gating by absence depends on the permission mode

Several acts are gated by having no allow rule at all rather than by any
rule: `sudo`, `apt`, `gh`, `curl`, `wget`, and every command neither the
allow list nor the guard mentions. Under `default` (and `plan`,
`acceptEdits`) an unmatched command prompts, so absence is a real gate.
Under `auto` or `bypassPermissions` an unmatched command is
**auto-approved**, and absence gates nothing.

That is what `disableAutoMode` and `disableBypassPermissionsMode` in
`.claude/settings.json` are holding up. They are not belt-and-braces
here: remove them and every act gated by absence becomes silent.

## Workspace trust splits a committed baseline in two

Measured in an untrusted directory:

- `permissions.allow` entries from `.claude/settings.json` are
  **ignored**, with a warning on stderr naming the exact remedy
  (accept the trust dialog once interactively, or set
  `projects["<path>"].hasTrustDialogAccepted` in `~/.claude.json`).
  A `claude -p` session in a never-trusted folder never gets them.
- `permissions.deny` entries **apply** — the refusal message was the
  hard-denial one.
- `hooks` entries **run**, guard included.

So in a fresh clone the restricting half of this baseline binds
immediately and the permitting half waits for the trust dialog. The
failure mode is friction (everything prompts), never a silent widening.

## File rules: only `Edit` and `Read` are consulted

A `Write(...)` or `Glob(...)` path rule is accepted and never used.
Claude Code says so at startup:

> Permission allow rule: `Write(/docs/**)` is not matched by file
> permission checks — only `Edit(path)` rules are. Use `Edit(/docs/**)`
> instead (Edit rules cover all file-editing tools).

`Edit(path)` covers every file-editing tool, `Read(path)` every
file-reading tool, and a `Read` deny also blocks edits and writes to the
same path. The baseline uses those two spellings only.

Startup also catches typos: a rule naming no known tool
(`Nonexistent(foo)`) is reported as "matches no known tool — check for
typos". The committed baseline produces no startup warning at all, which
is itself a check worth repeating after any edit.

## `autoMemoryEnabled: false` is honoured

With `autoMemoryDirectory` pointed at an empty scratch directory and the
session asked to remember a fact for future sessions: with auto memory
enabled, `MEMORY.md` and a topic file were written; with
`autoMemoryEnabled: false`, nothing was written and the model proposed a
`CLAUDE.md` edit instead. Rule 3's "auto memory stays disabled" is
enforced, not just declared.

## Re-measuring after a Claude Code update

Nothing here is guaranteed across versions, and three findings would
silently weaken the baseline if they changed: a hook `ask` overriding a
blanket allow, a hook `deny` binding, and the guard being reached at
all. The cheapest live check, run from the repository:

1. `git status --porcelain` — must run with no prompt (allow rules and
   workspace trust are in force).
2. `git tag --sort=-v:refname -d step-nonexistent-probe` — must **ask**,
   naming the tag rule. If it runs unprompted, the hook is not reaching
   the tool call and `Bash(git:*)` is standing alone.
3. `git push --force origin main` — must be **denied** outright, by the
   guard and by the settings backstop both.
4. `git push --dry-run origin main` — must ask.
5. For the frontmatter mechanism of the next section, from a throwaway
   directory holding one agent file with `tools: Read`:
   `claude -p --agent <name> 'List every tool available to you. Then
   run: echo probe'` — it must report Read alone and attempt no Bash
   call. If Bash is present, the two reviewer agents are running
   unrestricted and their prose is all that is left.

`.claude/hooks/bash_guard.py --selftest` covers the registry itself and
is wired into `just check` and `just test`; the four probes above cover
what no selftest can see, which is whether Claude Code still calls the
hook and still honours what it returns.

Any change in those four, or a new startup warning on stderr, is a
finding to bring to the operator before trusting the baseline again.

## Skill and agent frontmatter

**Measured on Claude Code 2.1.233 (native build, linux-x64), 2026-08-14,
at root `step-002`**, the step that introduced the mechanism. The probe
workspace was a throwaway directory holding nothing but
`.claude/agents/*.md`; each run asked one session to name its own tools
and then to use one it should not have. Evidence is the `tool_use`
blocks in `--output-format stream-json --verbose`, not the model's
prose — the prose agreed, but it is a claim like any other.

| Probe | Result |
|---|---|
| Agent with `tools: Read`, asked to run Bash | **No Bash tool present.** No `tool_use`, no permission denial — the tool is absent, not refused |
| Agent with no `tools:` key at all | Full toolset, Bash included; the Bash call reached the permission layer and was refused there |
| `tools: Read, Glob, Grep, Bash` | The session holds exactly `Read, Bash` |
| `tools: Read, Glob, Grep, Bash, Edit, Write` | The session holds exactly `Read, Bash, Edit, Write` |
| The same restricted agent through the `Agent` tool rather than `--agent` | Same answer, `Read, Bash` — the subagent path and the session path filter alike |
| Skill with `allowed-tools: Read`, its body ordering a Bash command | **Bash ran**, output returned, no prompt and no denial — the key restricts nothing |

So **agent `tools:` frontmatter binds and a skill's `allowed-tools` does
not**, on the same version, in the same workspace, an hour apart. That
asymmetry is the reason the skills here carry `name` and `description`
only while the agents carry real tool lists: an allowlist that enforces
nothing is a guard on paper, and it would read as one that binds.

Two things follow for what gets written in these files:

- **`Glob` and `Grep` are not tools in this version.** Naming them is
  silently ignored — no startup warning, no error — and the list is
  honoured for the names that do exist. The instantiated agents
  therefore ask for `Bash` and search with it. A name that resolves to
  nothing is a dangling reference like any other; re-check the tool
  inventory before copying a `tools:` line from anywhere.
- **A restricted agent cannot be widened by a permission rule.** The
  tool is not in its API request at all, so an absent tool is an absent
  capability, not a prompt. Give an agent the tools its job needs, and
  gate what it must not do in prose plus the guard hook.
- **A subagent already has `CLAUDE.md`.** Asked to answer from context
  with no tool call, a subagent quoted the file's first heading and the
  opening of rule 9 verbatim, and correctly reported that `README.md`
  was *not* there. So the boundary does not need restating inside an
  agent file — and must not be: rule 9 says its enumeration is carried
  whole in `CLAUDE.md`, never compressed or moved, and two hand-copies
  of it had already drifted apart before this was measured. What an
  agent file adds is the one thing rule 9 does not say: for a subagent
  the *gated* set is forbidden outright, there being no exchange in
  which the operator could authorize it.

`model:` resolves the aliases it is given: `model: opus` started a
session reporting `claude-opus-5`, `model: fable` one reporting
`claude-fable-5` (read from the stream's `init` event and each
assistant message, not from the model, which misidentified itself in
both runs). An alias that does not resolve is worth re-probing the same
way after an update. No agent in this repository pins one, deliberately
— `/approve-step` passes the override for the two milestone passes at
invocation, for the reason D-011 records — so this measurement is here
to make that choice checkable, not to describe a file.

The probe workspace and its transcripts are disposable and live under
`.local/probes/step-002/` (`DECISIONS.md` D-004); re-create them rather
than trusting an old copy.
