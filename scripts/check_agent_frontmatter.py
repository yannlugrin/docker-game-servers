#!/usr/bin/env python3
"""Every agent and skill definition has frontmatter that parses and names itself.

The failure this exists for is silent in the worst way: a malformed agent does
not error, it simply never loads. The ritual that names it then skips a step
and reports success, because nothing anywhere says the agent was missing. A
malformed skill fails the same way, one level up: `/handover-step` is not
found, so the handover happens by improvisation instead.

Deliberately narrow. Three things are checked because all three are exact: the
frontmatter parses as YAML, it carries `name` and `description`, and `name`
matches **the string rituals actually spawn or type** — the filename for an
agent, the directory name for a skill, whose file is always `SKILL.md`.
Nothing else is checked. Scanning the body for backticked tokens and asserting
each resolves would be a false-positive machine that grows worse as the
repository does, and `tools:` cannot be validated here either: the set of real
tool names belongs to the installed Claude Code, not to this repository, and
an unlisted name is dropped in silence rather than refused.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

FRONTMATTER = "---"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def definitions(root: Path) -> list[tuple[Path, str, str]]:
    """Every governance definition, as (path, kind, the name it must carry)."""
    found = [(path, "agent", path.stem) for path in (root / ".claude" / "agents").glob("*.md")]
    # A skill is identified by its directory: the file is always SKILL.md, so
    # the stem would be the same string for every one of them.
    found += [
        (path, "skill", path.parent.name)
        for path in (root / ".claude" / "skills").glob("*/SKILL.md")
    ]
    return sorted(found)


def frontmatter_of(path: Path) -> tuple[dict | None, str | None]:
    """Return (parsed mapping, error). Exactly one of the two is None."""
    text = path.read_text()
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER:
        return None, "no frontmatter: the first line is not ---"
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == FRONTMATTER)
    except StopIteration:
        return None, "frontmatter is never closed by a second ---"
    try:
        parsed = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        return None, f"frontmatter does not parse: {error}"
    if not isinstance(parsed, dict):
        return None, "frontmatter is not a mapping"
    return parsed, None


def main() -> int:
    root = project_root()
    problems: list[tuple[Path, str]] = []
    found = definitions(root)

    for path, kind, expected in found:
        where = path.relative_to(root)
        parsed, error = frontmatter_of(path)
        if error is not None:
            problems.append((path, f"{where}: {error}"))
            continue
        for key in ("name", "description"):
            if not str(parsed.get(key, "")).strip():
                problems.append((path, f"{where}: no {key}, so nothing can select this {kind}"))
        name = parsed.get("name")
        if name and name != expected:
            problems.append((path, f"{where}: name {name!r} does not match {expected!r}"))

    for _, problem in problems:
        print(f"MALFORMED  {problem}")
    # Count offending *files*, not problems: one definition can fail several
    # ways, and subtracting problem count from file count prints a negative.
    bad = len({path for path, _ in problems})
    print(f"{len(found) - bad}/{len(found)} agent and skill definitions well-formed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
