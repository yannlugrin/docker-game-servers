#!/usr/bin/env python3
"""The checks no linter can do: this workflow's own memory.

Stale memory is what actually costs a session — a pointer that disagrees with
the plan, two steps claiming to be in progress, a CLAUDE.md over its budget.
Plans are discovered, never listed: a new game track needs no edit here.

Exit codes: 0 clean, 1 error, 2 warnings only. Set GOVERNANCE_ROOT to check a
tree other than this file's repository (the tests do).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("GOVERNANCE_ROOT", Path(__file__).resolve().parent.parent))

# CLAUDE.md rule 3: a hard budget, with a shoulder to warn on.
MAX_LINES = 199
WARN_LINES = 190
STATUSES = {"pending", "in progress", "awaiting test", "done"}

errors: list[str] = []
warnings: list[str] = []


def plans() -> list[Path]:
    return sorted([*ROOT.glob("PLAN.md"), *ROOT.glob("*/PLAN.md")])


def steps(path: Path) -> dict[str, str]:
    """step id -> status, for one plan."""
    found: dict[str, str] = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^###\s+(step-[a-z]*-?\d+)\b", line)
        status = re.match(r"^-\s+\*\*Status\*\*:\s*([a-z ]+?)\.?\s*$", line)
        if heading:
            current = heading.group(1)
        elif status and current:
            value = status.group(1).strip()
            if value not in STATUSES:
                errors.append(f"{path.name}: {current} has unknown status {value!r}")
            found[current] = value
            current = None
    return found


def check_settings() -> None:
    """Only that it parses and keeps auto memory off — the rest is Claude
    Code's business, and it complains loudly on its own."""
    path = ROOT / ".claude" / "settings.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f".claude/settings.json: {exc}")
        return
    if data.get("autoMemoryEnabled") is not False:
        errors.append(".claude/settings.json: autoMemoryEnabled must be present and false (rule 3)")


def check_tooling() -> None:
    """A skill or agent whose frontmatter is broken does not load."""
    files = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    files += sorted((ROOT / ".claude" / "agents").glob("*.md"))
    for path in files:
        name = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        expected = path.parent.name if path.name == "SKILL.md" else path.stem
        if not text.startswith("---\n") or "\n---\n" not in text:
            errors.append(f"{name}: no frontmatter block")
        elif not re.search(rf"^name:\s*{re.escape(expected)}\s*$", text, re.MULTILINE):
            errors.append(f"{name}: frontmatter name must be {expected!r}")
        elif not re.search(r"^description:\s*\S", text, re.MULTILINE):
            errors.append(f"{name}: frontmatter description is missing or empty")
        for leftover in re.findall(r"\{\{[A-Z_]+\}\}", text):
            errors.append(f"{name}: unresolved template placeholder {leftover}")


def check_memory() -> None:
    claude_md = ROOT / "CLAUDE.md"
    text = claude_md.read_text(encoding="utf-8")

    lines = len(text.splitlines())
    if lines > MAX_LINES:
        errors.append(f"CLAUDE.md: {lines} lines exceeds the {MAX_LINES}-line budget (rule 3)")
    elif lines >= WARN_LINES:
        warnings.append(f"CLAUDE.md: {lines} lines; the budget is {MAX_LINES} (rule 3)")

    declared = {step: (status, path) for path in plans() for step, status in steps(path).items()}

    running = [step for step, (status, _) in declared.items() if status == "in progress"]
    if len(running) > 1:
        errors.append(f"plans: more than one step in progress repository-wide (rule 6): {running}")

    pointer = re.search(r"Current step:\s*\*\*(step-[a-z]*-?\d+)\s*\(([a-z ]+)\)\*\*", text)
    if not pointer:
        errors.append("CLAUDE.md: Current state does not name a step as 'Current step: **step-… (status)**'")
        return
    step_id, status = pointer.group(1), pointer.group(2).strip()
    if step_id not in declared:
        errors.append(f"CLAUDE.md: current step {step_id} is in no plan")
    elif declared[step_id][0] != status:
        plan = declared[step_id][1].relative_to(ROOT)
        errors.append(
            f"CLAUDE.md: current step {step_id} is {status!r} here but {declared[step_id][0]!r} in {plan}"
        )


def main() -> int:
    check_settings()
    check_tooling()
    check_memory()
    for message in errors:
        print(f"error: {message}")
    for message in warnings:
        print(f"warning: {message}")
    return 1 if errors else (2 if warnings else 0)


if __name__ == "__main__":
    sys.exit(main())
