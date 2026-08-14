#!/usr/bin/env python3
"""PreToolUse guard closing the one hole permission patterns leave open.

Permission rules match a command's *prefix*, so a broad allow rule also
admits any flag that appears later in the same command. Measured on
Claude Code 2.1.232 (see `.claude/docs/permissions.md`):
`Bash(git commit -m *)` allows `git commit -a --amend -m x` to run with
no prompt, because the ask rule written for `git commit --amend*` never
matches once a flag precedes `--amend`.

This guard re-reads the *whole* command and denies the forms an allow
rule must never carry: history rewriting, harness bypass, a publish
hidden in a build, a delete escaping the disposable state root. It
covers exactly the prefixes `.claude/settings.json` allows and nothing
else — everything else rule 9 gates has no allow rule, so it already
prompts on its own and stays approvable in the exchange.

Deliberate limits, both measured rather than assumed:

- A hook is fail-open. If this file is missing, unreadable or crashes,
  Claude Code lets the call through. The permission rules are the
  boundary; this guard only subtracts from what they allow. `just check`
  and `just test` are what keep it alive.
- A hook cannot turn an allowed call into a prompt: `permissionDecision:
  "escalate"` is ignored when an allow rule matches. `deny` is the only
  decision that binds, so a guarded form is refused outright rather than
  put to the operator. The plain spellings (`git commit --amend ...`,
  `git push ...`) carry an ask rule instead and still prompt normally.

Input and output are the PreToolUse hook contract: the tool call arrives
as JSON on stdin, a decision leaves as JSON on stdout.
"""

import json
import re
import shlex
import sys

# Wrappers Claude Code strips before matching a permission rule; the
# guard strips the same ones, or `timeout 5 git commit --amend` would
# match an allow rule while slipping past this file.
WRAPPERS = frozenset(
    {"timeout", "time", "nice", "nohup", "stdbuf", "command", "builtin", "noglob", "xargs"}
)

# Options of those wrappers that consume the token after them.
WRAPPER_VALUE_OPTS = frozenset({"-n", "-s", "--signal", "-k", "--kill-after", "-i", "-o"})

# Global options that sit between the program and its subcommand.
GLOBAL_OPTS = {
    "git": frozenset(
        {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
    ),
    "docker": frozenset(
        {"-H", "--host", "--context", "--config", "-l", "--log-level", "--tlscacert",
         "--tlscert", "--tlskey"}
    ),
}

SEPARATOR_CHARS = frozenset("&|;()<>")


class Refusal(Exception):
    """A guarded form was recognised in the command."""


def _new_subcommand(tokens):
    """Split shell tokens into subcommands on the operators Claude Code honours."""
    current = []
    for token in tokens:
        if token and all(char in SEPARATOR_CHARS for char in token):
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


def tokenize(command):
    """Tokenize a command line into subcommands.

    Raises ValueError on input the shell lexer cannot parse, which the
    caller answers with a second, quote-blind pass rather than with a
    refusal: heredocs are unparsable by this lexer and are ordinary
    working material.
    """
    subcommands = []
    for line in command.splitlines():
        if not line.strip():
            continue
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        subcommands.extend(_new_subcommand(list(lexer)))
    return subcommands


def tokenize_loosely(command):
    """Tokenize without honouring quotes, for input the shell lexer rejects.

    Quoting is what the strict pass could not resolve, so this one gives
    it up: it splits on the shell operators and on whitespace, and reads
    a `--flag` as a flag wherever it sits. A guarded flag quoted inside a
    message is therefore refused here, which is the safe direction and
    only reachable once the strict pass has already failed.
    """
    subcommands = []
    for chunk in re.split(r"&&|\|\||[;&|()\n]", command):
        tokens = [token.strip("\"'") for token in chunk.split()]
        tokens = [token for token in tokens if token]
        if tokens:
            subcommands.append(tokens)
    return subcommands


def strip_prelude(tokens):
    """Drop leading environment assignments and wrapper commands."""
    tokens = list(tokens)
    changed = True
    while changed and tokens:
        changed = False
        head = tokens[0]
        if "=" in head and head.split("=", 1)[0].replace("_", "a").isalnum():
            tokens.pop(0)
            changed = True
            continue
        if head in WRAPPERS:
            tokens.pop(0)
            changed = True
            while tokens and tokens[0].startswith("-"):
                option = tokens.pop(0)
                if option in WRAPPER_VALUE_OPTS and tokens:
                    tokens.pop(0)
            # `timeout 30 cmd` and `nice 10 cmd`: drop a bare duration.
            if head in {"timeout", "nice"} and tokens:
                candidate = tokens[0].rstrip("smhd")
                if candidate.replace(".", "", 1).isdigit():
                    tokens.pop(0)
    return tokens


def skip_global_options(tokens):
    """Return the tokens from a program's subcommand onwards."""
    program = tokens[0]
    value_opts = GLOBAL_OPTS.get(program, frozenset())
    index = 1
    while index < len(tokens) and tokens[index].startswith("-"):
        option = tokens[index]
        index += 1
        if "=" not in option and option in value_opts and index < len(tokens):
            index += 1
    return [program] + tokens[index:]


def iter_options(tokens, value_opts, short_value_opts):
    """Yield the option tokens of a command, skipping the values they take.

    Values are skipped so that `git commit -m "use --amend next time"`
    is read as a message, not as a request to amend.
    """
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token.startswith("-") or token == "-" or token == "--":
            continue
        name = token.split("=", 1)[0]
        yield name
        if "=" in token:
            continue
        if token.startswith("--"):
            if name in value_opts and index < len(tokens):
                index += 1
            continue
        # A bundled short group such as `-am`: every letter is a flag,
        # and only the last one can consume the following token.
        for letter in token[1:]:
            yield "-" + letter
        if token[-1] in short_value_opts and index < len(tokens):
            index += 1


def matches_long(option, forbidden):
    """Match a long option, including the unique abbreviations git accepts."""
    if option in forbidden:
        return option
    if len(option) >= 4:
        for candidate in forbidden:
            if candidate.startswith(option):
                return candidate
    return None


def check_flags(tokens, guard):
    """Refuse a command carrying one of the guarded prefix's forbidden flags.

    A flag written first, exactly as `.claude/settings.json` spells it in
    an ask rule, is left alone: that spelling is the one the ask rule
    matches, so the operator gets a prompt and can approve it. Every
    other position is a form no ask rule can catch while an allow rule
    still matches the prefix, and that is what this guard refuses.
    """
    value_opts = guard.get("value_opts", frozenset())
    short_value_opts = guard.get("short_value_opts", "")
    forbidden_long = guard.get("forbidden_long", {})
    forbidden_short = guard.get("forbidden_short", {})
    abbreviations = guard.get("abbreviations", False)
    leading = tokens[0] if tokens else None

    for option in iter_options(tokens, value_opts, short_value_opts):
        if option.startswith("--"):
            hit = matches_long(option, forbidden_long) if abbreviations else (
                option if option in forbidden_long else None
            )
            entry = forbidden_long.get(hit) if hit else None
        else:
            hit = option
            entry = forbidden_short.get(option[1:])
        if entry is None:
            continue
        if entry["prompts_when_first"] and leading == hit:
            continue
        raise Refusal(entry["reason"])


def check_output_target(tokens, guard):
    """Refuse a build whose `--output` writes to a registry."""
    targets = guard.get("registry_output_opts")
    if not targets:
        return
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        name, _, inline = token.partition("=")
        if name not in targets:
            continue
        value = inline
        if not value and index < len(tokens):
            value = tokens[index]
            index += 1
        lowered = value.lower()
        if "type=registry" in lowered or "push=true" in lowered:
            raise Refusal(
                "`--output` publishes to a registry, which is a shared-state write"
            )


def check_subcommand(tokens, guard):
    """Refuse a forbidden subcommand of a guarded family, such as `compose push`."""
    forbidden = guard.get("forbidden_subcommands")
    if not forbidden:
        return
    value_opts = guard.get("value_opts", frozenset())
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if token.startswith("-"):
            if "=" not in token and token in value_opts and index < len(tokens):
                index += 1
            continue
        if token in forbidden:
            raise Refusal(forbidden[token])
        return


def check_paths(tokens, guard):
    """Refuse a delete that climbs out of the path its allow rule names."""
    if not guard.get("reject_parent_paths"):
        return
    for token in tokens:
        if token.startswith("-"):
            continue
        if ".." in token.replace("\\", "/").split("/"):
            raise Refusal(
                "the path climbs out of its directory with `..`, so the allow rule "
                "for the disposable state root does not describe what is deleted"
            )


GUARDS = (
    {
        "prefix": ("git", "commit"),
        "abbreviations": True,
        "value_opts": frozenset(
            {"--message", "--reuse-message", "--reedit-message", "--file", "--author",
             "--date", "--cleanup", "--trailer", "--fixup", "--squash",
             "--pathspec-from-file"}
        ),
        "short_value_opts": "mCcF",
        "forbidden_long": {
            "--amend": {
                "prompts_when_first": True,
                "reason": "`--amend` rewrites the previous commit behind a flag, where "
                          "no ask rule can see it; rule 9 keeps history rewriting with "
                          "the operator",
            },
            "--no-verify": {
                "prompts_when_first": True,
                "reason": "`--no-verify` skips the pre-commit harness behind a flag, "
                          "where no ask rule can see it; rule 2 requires that harness "
                          "green on every commit",
            },
        },
        "forbidden_short": {
            "n": {
                "prompts_when_first": True,
                "reason": "`-n` is `--no-verify`: it skips the pre-commit harness that "
                          "rule 2 requires green on every commit",
            },
        },
    },
    {
        "prefix": ("git", "tag"),
        "abbreviations": True,
        "value_opts": frozenset(
            {"--message", "--file", "--local-user", "--sort", "--format", "--points-at",
             "--contains", "--no-contains", "--merged", "--no-merged"}
        ),
        "short_value_opts": "mFu",
        "forbidden_long": {
            "--delete": {
                "prompts_when_first": True,
                "reason": "deleting a tag destroys an approval marker, and behind a flag "
                          "no ask rule can see it; rule 9 keeps that with the operator",
            },
            "--force": {
                "prompts_when_first": True,
                "reason": "`--force` moves an existing tag onto another commit, and "
                          "behind a flag no ask rule can see it; rule 9 keeps that with "
                          "the operator",
            },
        },
        "forbidden_short": {
            "d": {
                "prompts_when_first": True,
                "reason": "`-d` deletes a tag, destroying an approval marker; rule 9 "
                          "keeps that with the operator",
            },
            "f": {
                "prompts_when_first": True,
                "reason": "`-f` moves an existing tag onto another commit; rule 9 keeps "
                          "that with the operator",
            },
        },
    },
    {
        "prefix": ("docker", "build"),
        "value_opts": frozenset(
            {"-t", "--tag", "-f", "--file", "--build-arg", "--target", "--platform",
             "--network", "--cache-from", "--cache-to", "--secret", "--ssh", "--label",
             "--iidfile", "--progress", "--add-host", "--builder", "--metadata-file",
             "--provenance", "--sbom", "--shm-size", "--ulimit", "--cgroup-parent",
             "--memory", "--attest", "--annotation", "--allow"}
        ),
        "short_value_opts": "tfm",
        "forbidden_long": {
            "--push": {
                # No ask rule can catch this one: `Bash(docker * push*)` needs a
                # space before `push` and never matches `--push`, so the build's
                # own allow rule would carry the publish through unprompted.
                "prompts_when_first": False,
                "reason": "`--push` publishes to a registry from inside a build, which "
                          "rule 9 gates as a shared-state write; publish through the "
                          "publication step's own path instead",
            },
        },
        "registry_output_opts": frozenset({"-o", "--output"}),
    },
    {
        "prefix": ("docker", "compose"),
        "value_opts": frozenset(
            {"-f", "--file", "-p", "--project-name", "--profile", "--project-directory",
             "--env-file", "--parallel", "--progress", "--ansi"}
        ),
        "forbidden_subcommands": {
            "push": "`docker compose push` publishes to a registry, which rule 9 gates "
                    "as a shared-state write",
        },
    },
    {
        "prefix": ("rm",),
        "reject_parent_paths": True,
    },
)

# `docker buildx build` and `docker buildx bake` take the same guard as
# `docker build`: they are the same publish hidden in the same place.
_BUILD_GUARD = next(guard for guard in GUARDS if guard["prefix"] == ("docker", "build"))
GUARDS = GUARDS + (
    dict(_BUILD_GUARD, prefix=("docker", "buildx", "build")),
    dict(_BUILD_GUARD, prefix=("docker", "buildx", "bake")),
)


def classify(command):
    """Return a refusal reason for a guarded command, or None to stay out of the way."""
    try:
        subcommands = tokenize(command)
    except ValueError:
        subcommands = tokenize_loosely(command)

    for tokens in subcommands:
        tokens = strip_prelude(tokens)
        if not tokens:
            continue
        tokens = skip_global_options(tokens)
        for guard in GUARDS:
            prefix = guard["prefix"]
            if tuple(tokens[: len(prefix)]) != prefix:
                continue
            rest = tokens[len(prefix):]
            try:
                check_flags(rest, guard)
                check_output_target(rest, guard)
                check_subcommand(rest, guard)
                check_paths(rest, guard)
            except Refusal as refusal:
                return str(refusal)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str):
        return 0

    reason = classify(command)
    if reason is None:
        return 0

    message = (
        f"Blocked by the repository's Bash guard: {reason}. "
        "Nothing was run. Ask the operator to run it, or use the plain spelling, "
        "which prompts instead of being refused."
    )
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    print(message, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
