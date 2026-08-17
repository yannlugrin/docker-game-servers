#!/usr/bin/env python3
"""Every hook command declared in Claude Code settings resolves to a runnable file.

The failure this exists for is silent. A `command` naming a file that is not
there leaves valid JSON, a settings file that still loads, a green lint — and
a hook that never runs. `check-json` cannot see it, because the document is
well-formed; `bash_guard.py --liveness` cannot see it either, because that
asks whether the guard is correct, not whether anything calls it.

What this still does not prove is that Claude Code *reaches* the hook. Nothing
in a repository can prove that; only a live probe can, by issuing a command
the guard must refuse and seeing it refused **by name**. The measurements file
carries that probe.
"""

from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path

SETTINGS = ("settings.json", "settings.local.json")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def declared_commands(settings: dict) -> list[tuple[str, str]]:
    """Every (event, command) pair declared under `hooks`."""
    found: list[tuple[str, str]] = []
    for event, matchers in (settings.get("hooks") or {}).items():
        for matcher in matchers or ():
            for hook in matcher.get("hooks") or ():
                if hook.get("type") == "command" and hook.get("command"):
                    found.append((event, hook["command"]))
    return found


def resolve(command: str, root: Path) -> Path:
    """The file a hook command would execute, with the project variable expanded."""
    word = shlex.split(command)[0] if command.strip() else ""
    expanded = os.path.expanduser(
        word.replace("$CLAUDE_PROJECT_DIR", str(root)).replace(
            "${CLAUDE_PROJECT_DIR}", str(root)
        )
    )
    path = Path(expanded)
    return path if path.is_absolute() else root / path


def main() -> int:
    root = project_root()
    problems: list[str] = []
    checked = 0

    for name in SETTINGS:
        path = root / ".claude" / name
        if not path.exists():
            continue
        try:
            settings = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            problems.append(f"{name}: does not parse ({error})")
            continue
        for event, command in declared_commands(settings):
            checked += 1
            target = resolve(command, root)
            where = f"{name}: {event} hook {command!r}"
            if not target.exists():
                problems.append(f"{where}: {target} does not exist")
            elif not os.access(target, os.X_OK):
                problems.append(f"{where}: {target} is not executable")

    for problem in problems:
        print(f"UNRESOLVED  {problem}")
    print(f"{checked - len(problems)}/{checked} declared hook commands resolve")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
