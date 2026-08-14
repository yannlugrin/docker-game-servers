# What the permission and hook mechanisms actually do

Read this before editing `.claude/settings.json` or
`.claude/hooks/guard-bash.py`, and before assuming any sentence below is
still true: every claim here is a measurement, not a reading of the
documentation, and the mechanisms belong to a tool that updates itself.

**Measured on Claude Code 2.1.232 (native build, linux-x64), 2026-08-14,
at root `step-001`.** Each probe ran a separate non-interactive session
(`claude -p --output-format json`) that was asked to attempt exactly one
command; the outcome was read from the harness's own
`permission_denials` array and from the startup warnings on stderr, not
from the model's prose. Probes are independent: one passing says nothing
about another.

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

The practical consequence for this repository: **an `ask` rule that
overlaps an intended `allow` rule silently cancels it.** A blanket
`Bash(rm *)` in `ask` would have cancelled the `Bash(rm .local/*)`
allowance, so gating by *absence* of an allow rule is the tool that fits
the disposable state root, not a broad ask rule.

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
  rule, and no guard is needed for that shape.

`.claude/hooks/guard-bash.py` exists for the first item and nothing else.

## What a PreToolUse hook can and cannot do

| Probe | Result |
|---|---|
| Hook returns `deny` while an allow rule matches | Call blocked |
| Hook returns `escalate` while an allow rule matches | **Call ran** |
| Hook returns `escalate` on a built-in read-only command | Call ran |
| Hook exits 1 after writing to stderr | Call ran |
| Hook script missing from the configured path | Call ran |
| Undocumented `"ask"` value in `permissionDecision` | Call blocked |

Two consequences shape the guard:

1. **A hook cannot turn an allowed call into a prompt.** `escalate` is
   ignored where an allow rule already grants the call, so `deny` is the
   only decision that binds. A guarded form is therefore refused
   outright rather than put to the operator — which is why the guard
   covers only the forms an allow rule would otherwise carry through
   unprompted, and leaves the plain spellings (`git commit --amend ...`,
   `git push ...`) to their ask rules, where they still prompt.
2. **A hook is fail-open.** A missing, unreadable or crashing hook lets
   the call through, silently. The permission rules are the boundary;
   the guard only subtracts from what they allow. `just check` (the file
   parses, is executable, has its shebang) and `just test` (41 cases on
   its real stdin/stdout contract) are what keep it honest.

`${CLAUDE_PROJECT_DIR}` in a hook's `command` resolves: the guard blocked
a call in this repository from a session started here.

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

Nothing here is guaranteed across versions, and two findings would
silently weaken the baseline if they changed: hook `deny` beating an
allow rule, and the guard being reached at all. The cheapest live check,
run from the repository:

1. `git status --porcelain` — must run with no prompt (allow rules and
   workspace trust are in force).
2. `git tag --sort=-v:refname -d step-nonexistent-probe` — must be
   refused by the guard, naming `-d`. If it runs, the hook is not
   reaching the tool call.
3. `git push --dry-run origin main` — must prompt (ask rules are in
   force).

Any change in those three, or a new startup warning on stderr, is a
finding to bring to the operator before trusting the baseline again.
