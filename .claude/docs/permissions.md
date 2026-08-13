# The rule-9 permission baseline, and what was proven to bind

Read before changing `.claude/settings.json` or `.claude/hooks/guard.py`.
The decision itself is D-004 in the root `DECISIONS.md`; this file is the
operating knowledge behind it.

## Two layers, on purpose

**Permission rules** (`.claude/settings.json`) match a command **prefix** or
a file path. They are what the operator can read at a glance, so they carry
the shape of rule 9: `allow` the harness, the local container lifecycle,
read-only remote reads and additive git; `ask` everything rule 9 gates;
`deny` only what has no authorized use at all.

**The guard hook** (`.claude/hooks/guard.py`, `PreToolUse`) reads the whole
command line, which is what a prefix cannot do:

- `gh api` is one command for reads and writes — the method decides;
- the act-changing flag arrives late (`git commit -m x --amend`,
  `docker build … --push`, `docker image prune` with no scoping filter,
  `curl -XPOST`), while the allow-listed prefix is the same;
- rule 1's read ban on the specification archive must hold for shell
  commands, not only for the Read tool.

The hook returns `deny`, `ask`, or stays silent so the permission rules
decide. Silence is not approval. An internal error becomes an `ask`.

`tools/test.sh` asserts the hook's verdict on every spelling that matters —
add a case there before adding a pattern, since the failure mode is silence.

## Verified behavior (step-000 probes, 2026-08-13, Claude Code 2.1.231)

- **Permission rules bind, and relative paths in `.claude/settings.json`
  resolve from the project root.** A `Read` under
  `.claude/spec-work/reviews/**` came back "File is in a directory that is
  denied by your permission settings" — the settings layer, not the hook.
- **The hook binds in a running session.** Bash calls were denied live with
  the hook's own reason text ("rule 1: the specification phase's archive…",
  "rule 6: step tags…"), including one of the reviewer subagent's.
- **`Write(path)` rules never fire.** Claude Code matches file-editing tools
  against `Edit(path)` rules only, and warns at startup about every
  `Write(path)` rule. Use `Edit(...)`; it covers Write too.
- **`autoMemoryEnabled: false` is accepted** — the key parses, the CLI
  reports no complaint about it, and no memory store exists under `.claude/`
  or `~/.claude/`. That it is *honored* is not directly observable from
  here; the governance family asserts the key's value, which is the part
  this repository can enforce.
- **Skills and agents load from disk, but only at session start.** The four
  rituals became available mid-session; the `step-reviewer` agent did not —
  invoking it failed with "Agent type not found" until a new session picked
  it up. After adding or renaming tooling, restart before relying on it.
- **A skill's `allowed-tools` list does not restrict anything** (2.1.231):
  probed while `/orient` was active — its list has neither `Write` nor a
  general `Bash` pattern, and both a `Write` and a plain `ls` succeeded. The
  rituals' allowlists are a statement of intent, not a mechanism. Everything
  that actually binds is in `.claude/settings.json` and the guard hook; if a
  ritual must be prevented from doing something, it belongs there.
- **The subagent tool is `Agent` in this harness** (not `Task`): invoking
  `step-reviewer` through it works, and `handover-step` lists both names so
  the review cannot silently not happen.
- **The hook runs under the system `python3`**, not the pinned `.venv` — it
  must keep working with only the standard library, and a host without
  `python3` loses the guard entirely (the settings layer still holds).
- **Not verified from here**: that a hook `ask` overrides an allow-listed
  prefix (`git commit --amend` under `Bash(git commit:*)`). It needs an
  interactive prompt to appear, which only the operator can observe.

## Do not

- Add an `allow` pattern whose prefix admits a gated act (a bare
  `git commit` allowance admits `--amend`) without a matching hook rule.
- Use `deny` for something with a legitimate authorized use: `deny` has no
  in-session override, so it forces a settings edit mid-step.
- Expect `claude config get|list` to read these values — those subcommands
  no longer exist; the arguments are taken as a prompt and start a session.
