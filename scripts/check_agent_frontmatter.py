#!/usr/bin/env python3
"""Every subagent definition has frontmatter that parses and identifies itself.

The failure this exists for is silent in the worst way: a malformed agent does
not error, it simply never loads. The ritual that names it then skips a step
and reports success, because nothing anywhere says the agent was missing.

Deliberately narrow. Three things are checked because all three are exact: the
frontmatter parses as YAML, it carries `name` and `description`, and `name`
matches the filename — the string rituals actually spawn. Nothing else is
checked. Scanning the body for backticked tokens and asserting each resolves
would be a false-positive machine that grows worse as the repository does, and
`tools:` cannot be validated here either: the set of real tool names belongs
to the installed Claude Code, not to this repository, and an unlisted name is
dropped in silence rather than refused.

`.claude/skills/*/SKILL.md` joins this check at `step-004`, which lands the
first file of that class.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

FRONTMATTER = "---"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


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
    problems: list[str] = []
    agents = sorted((root / ".claude" / "agents").glob("*.md"))

    for path in agents:
        where = path.relative_to(root)
        parsed, error = frontmatter_of(path)
        if error is not None:
            problems.append(f"{where}: {error}")
            continue
        for key in ("name", "description"):
            if not str(parsed.get(key, "")).strip():
                problems.append(f"{where}: no {key}, so nothing can select this agent")
        name = parsed.get("name")
        if name and name != path.stem:
            problems.append(
                f"{where}: name {name!r} does not match the filename {path.stem!r}"
            )

    for problem in problems:
        print(f"MALFORMED  {problem}")
    print(f"{len(agents) - len(problems)}/{len(agents)} agent definitions well-formed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
