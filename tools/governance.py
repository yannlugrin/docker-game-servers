#!/usr/bin/env python3
"""The checks no off-the-shelf linter can do: this workflow's own state.

Settings and tooling parse, every name and path they use resolves, the memory
pointers agree with the plans, and CLAUDE.md stays inside its line budget.

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

TRACK_PLANS = {"root": "PLAN.md", "sc": "steamcmd/PLAN.md", "pz": "project-zomboid/PLAN.md"}
STATUSES = {"pending", "in progress", "awaiting test", "done"}
BUILTIN_COMMANDS = {"clear", "compact", "config", "context", "doctor", "help", "resume"}

BACKTICKED = re.compile(r"`([^`\n]+)`")
PATH_LIKE = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_./-]*\.(md|sh|py|json|ya?ml|txt)$")
SLASH_COMMAND = re.compile(r"^/([a-z][a-z0-9-]*)$")
AGENT_MENTION = re.compile(
    r"(?:`([a-z][a-z0-9-]*)`\s+agent)"
    r"|(?:agents?\s*[:(]?\s*((?:`[a-z][a-z0-9-]*`[,\s]*(?:and\s*)?)+))"
)

errors: list[str] = []
warnings: list[str] = []


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict | None:
    """Parse YAML frontmatter without a YAML library: the keys we check are
    flat strings, and a body we cannot split is itself the finding."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    data: dict[str, str] = {}
    for line in text[4 : end + 1].splitlines():
        match = re.match(r"^([a-zA-Z][\w-]*):\s*(.*)$", line)
        if match:
            data[match.group(1)] = match.group(2).strip()
        elif line.strip() and not line.startswith((" ", "-", "#")):
            return None
    return data


def check_settings() -> None:
    path = ROOT / ".claude" / "settings.json"
    if not path.exists():
        errors.append(".claude/settings.json: missing")
        return
    try:
        data = json.loads(read(path))
    except ValueError as exc:
        errors.append(f".claude/settings.json: does not parse as JSON: {exc}")
        return
    if data.get("autoMemoryEnabled") is not False:
        errors.append(".claude/settings.json: autoMemoryEnabled must be present and false (rule 3)")
    for matchers in (data.get("hooks") or {}).values():
        for matcher in matchers:
            for hook in matcher.get("hooks", []):
                command = hook.get("command", "")
                target = command.split()[0].replace("$CLAUDE_PROJECT_DIR", str(ROOT))
                if not os.access(target, os.X_OK):
                    errors.append(f".claude/settings.json: hook not executable: {command}")


def tooling_files() -> list[Path]:
    return sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md")) + sorted(
        (ROOT / ".claude" / "agents").glob("*.md")
    )


def check_tooling() -> None:
    for path in tooling_files():
        name = str(path.relative_to(ROOT))
        text = read(path)
        data = frontmatter(text)
        if data is None:
            errors.append(f"{name}: missing or unparseable frontmatter")
            continue
        expected = path.parent.name if path.name == "SKILL.md" else path.stem
        if data.get("name") != expected:
            errors.append(f"{name}: frontmatter name is {data.get('name')!r}, expected {expected!r}")
        if not data.get("description"):
            errors.append(f"{name}: frontmatter description is missing or empty")
        for leftover in re.findall(r"\{\{[A-Z_]+\}\}", text):
            errors.append(f"{name}: unresolved template placeholder {leftover}")


def not_yet_adopted() -> set[str]:
    claude_md = ROOT / "CLAUDE.md"
    if not claude_md.exists():
        return set()
    match = re.search(r"Not yet adopted[^:]*:(.*?)\.\s", read(claude_md), re.DOTALL)
    return set(re.findall(r"`([a-z][a-z0-9-]*)`", match.group(1))) if match else set()


def check_references() -> None:
    """Nothing may name a skill, an agent or a path that does not exist."""
    skills = {p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md")}
    agents = {p.stem for p in (ROOT / ".claude" / "agents").glob("*.md")}
    deferred = not_yet_adopted()

    for path in [*tooling_files(), ROOT / "CLAUDE.md", ROOT / "README.md"]:
        if not path.exists():
            errors.append(f"{path.name}: missing")
            continue
        name = str(path.relative_to(ROOT))
        text = read(path)
        for token in (t.strip() for t in BACKTICKED.findall(text)):
            command = SLASH_COMMAND.match(token)
            if command:
                skill = command.group(1)
                if skill not in skills and skill not in deferred and skill not in BUILTIN_COMMANDS:
                    errors.append(f"{name}: references skill /{skill}, which does not exist")
            elif PATH_LIKE.match(token) and not (ROOT / token).exists():
                errors.append(f"{name}: references path `{token}`, which does not exist")
        for single, group in AGENT_MENTION.findall(text):
            for agent in [single] if single else re.findall(r"`([a-z][a-z0-9-]*)`", group):
                if agent and agent not in agents and agent not in deferred:
                    errors.append(f"{name}: references agent `{agent}`, which does not exist")


def plan_steps(path: Path) -> dict[str, str]:
    steps: dict[str, str] = {}
    current = None
    for line in read(path).splitlines():
        heading = re.match(r"^###\s+(step-[a-z]*-?\d+)\b", line)
        status = re.match(r"^-\s+\*\*Status\*\*:\s*([a-z ]+?)\.?\s*$", line)
        if heading:
            current = heading.group(1)
        elif status and current:
            value = status.group(1).strip()
            if value not in STATUSES:
                errors.append(f"{path.name}: {current} has unknown status {value!r}")
            steps[current] = value
            current = None
    return steps


def check_memory() -> None:
    claude_md = ROOT / "CLAUDE.md"
    if not claude_md.exists():
        errors.append("CLAUDE.md: missing")
        return

    lines = len(read(claude_md).splitlines())
    if lines > MAX_LINES:
        errors.append(f"CLAUDE.md: {lines} lines exceeds the {MAX_LINES}-line budget (rule 3)")
    elif lines >= WARN_LINES:
        warnings.append(f"CLAUDE.md: {lines} lines; the budget is {MAX_LINES} (rule 3)")

    steps = {}
    for track, relative in TRACK_PLANS.items():
        path = ROOT / relative
        if path.exists():
            steps[track] = plan_steps(path)
        else:
            errors.append(f"{relative}: missing")

    running = [
        f"{step} ({track})" for track, s in steps.items() for step, v in s.items() if v == "in progress"
    ]
    if len(running) > 1:
        errors.append(f"plans: more than one step in progress repository-wide (rule 6): {', '.join(running)}")

    pointer = re.search(r"Current step:\s*\*\*(step-[a-z]*-?\d+)\s*\(([a-z ]+)\)\*\*", read(claude_md))
    if not pointer:
        errors.append("CLAUDE.md: Current state does not name a step as 'Current step: **step-… (status)**'")
        return
    step_id, status = pointer.group(1), pointer.group(2).strip()
    track_match = re.match(r"^step-([a-z]+)-\d+$", step_id)
    track = track_match.group(1) if track_match else "root"
    if track not in steps:
        errors.append(f"CLAUDE.md: current step {step_id} names track {track!r}, which has no plan")
    elif step_id not in steps[track]:
        errors.append(f"CLAUDE.md: current step {step_id} is not in {TRACK_PLANS[track]}")
    elif steps[track][step_id] != status:
        errors.append(
            f"CLAUDE.md: current step {step_id} is {status!r} here "
            f"but {steps[track][step_id]!r} in {TRACK_PLANS[track]}"
        )


def main() -> int:
    check_settings()
    check_tooling()
    check_references()
    check_memory()
    for message in errors:
        print(f"error: {message}")
    for message in warnings:
        print(f"warning: {message}")
    return 1 if errors else (2 if warnings else 0)


if __name__ == "__main__":
    sys.exit(main())
