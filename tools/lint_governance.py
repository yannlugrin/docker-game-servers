#!/usr/bin/env python3
"""Governance well-formedness checks (CLAUDE.md rule 2).

The workflow's own load-bearing files are artifacts like any other, so they
get a check family: settings and tooling parse, every name and path they use
resolves, the memory pointers agree with the plans, and CLAUDE.md stays inside
its line budget.

Exit codes: 0 clean, 1 errors present, 2 warnings only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

SETTINGS = REPO_ROOT / ".claude" / "settings.json"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
MAKEFILE = REPO_ROOT / "Makefile"

# CLAUDE.md rule 3: hard budget of 200 lines, with a shoulder to warn on.
CLAUDE_MD_MAX_LINES = 199
CLAUDE_MD_WARN_LINES = 190

PLANS = {
    "root": REPO_ROOT / "PLAN.md",
    "sc": REPO_ROOT / "steamcmd" / "PLAN.md",
    "pz": REPO_ROOT / "project-zomboid" / "PLAN.md",
}
STATUSES = {"pending", "in progress", "awaiting test", "done"}

errors: list[str] = []
warnings: list[str] = []


def error(where: object, message: str) -> None:
    errors.append(f"{where}: {message}")


def warn(where: object, message: str) -> None:
    warnings.append(f"{where}: {message}")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter, body); frontmatter is None when absent or invalid."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text
    raw = text[4 : end + 1]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, text[end + 5 :]
    if not isinstance(data, dict):
        return None, text[end + 5 :]
    return data, text[end + 5 :]


# --- tooling: skills, agents, settings ---------------------------------------


def check_settings() -> None:
    if not SETTINGS.exists():
        error(rel(SETTINGS), "missing")
        return
    try:
        data = json.loads(read(SETTINGS))
    except ValueError as exc:
        error(rel(SETTINGS), f"does not parse as JSON: {exc}")
        return
    if data.get("autoMemoryEnabled") is not False:
        error(rel(SETTINGS), "autoMemoryEnabled must be present and false (rule 3)")
    for event, matchers in (data.get("hooks") or {}).items():
        for matcher in matchers:
            for hook in matcher.get("hooks", []):
                command = hook.get("command", "")
                path_part = command.split()[0] if command else ""
                path_part = path_part.replace("$CLAUDE_PROJECT_DIR", str(REPO_ROOT))
                candidate = Path(path_part)
                if not candidate.exists():
                    error(rel(SETTINGS), f"{event} hook command not found: {command}")
                elif not candidate.is_file() or not candidate.stat().st_mode & 0o111:
                    error(rel(SETTINGS), f"{event} hook command not executable: {command}")


def tooling_files() -> list[Path]:
    files = sorted(SKILLS_DIR.glob("*/SKILL.md")) if SKILLS_DIR.exists() else []
    files += sorted(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.exists() else []
    return files


def check_tooling_frontmatter() -> None:
    for path in tooling_files():
        text = read(path)
        data, _ = split_frontmatter(text)
        if data is None:
            error(rel(path), "missing or unparseable YAML frontmatter")
            continue
        expected = path.parent.name if path.name == "SKILL.md" else path.stem
        if data.get("name") != expected:
            error(rel(path), f"frontmatter name is {data.get('name')!r}, expected {expected!r}")
        if not str(data.get("description", "")).strip():
            error(rel(path), "frontmatter description is missing or empty")
        for leftover in re.findall(r"\{\{[A-Z_]+\}\}", text):
            error(rel(path), f"unresolved template placeholder {leftover}")


# --- references resolve -------------------------------------------------------

BACKTICKED = re.compile(r"`([^`\n]+)`")
PATH_LIKE = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_./-]*\.(md|sh|py|json|ya?ml|txt)$")
SLASH_COMMAND = re.compile(r"^/([a-z][a-z0-9-]*)$")
# Claude Code's own commands: named freely, owned by nobody here.
BUILTIN_COMMANDS = {"clear", "compact", "config", "context", "doctor", "help", "resume"}
MAKE_TARGET = re.compile(r"\bmake ([a-z][a-z0-9-]*)\b")
AGENT_MENTION = re.compile(
    r"(?:`([a-z][a-z0-9-]*)`\s+agent)|(?:agents?\s*[:(]?\s*((?:`[a-z][a-z0-9-]*`[,\s]*(?:and\s*)?)+))"
)


def make_targets() -> set[str]:
    if not MAKEFILE.exists():
        return set()
    return set(re.findall(r"^([a-zA-Z][a-zA-Z0-9_-]*):", read(MAKEFILE), re.MULTILINE))


def not_yet_adopted() -> set[str]:
    if not CLAUDE_MD.exists():
        return set()
    match = re.search(r"Not yet adopted[^:]*:(.*?)\.\s", read(CLAUDE_MD), re.DOTALL)
    if not match:
        return set()
    return set(re.findall(r"`([a-z][a-z0-9-]*)`", match.group(1)))


def check_references() -> None:
    known_skills = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")} if SKILLS_DIR.exists() else set()
    known_agents = {p.stem for p in AGENTS_DIR.glob("*.md")} if AGENTS_DIR.exists() else set()
    deferred = not_yet_adopted()
    targets = make_targets()

    scanned = [*tooling_files(), CLAUDE_MD, REPO_ROOT / "README.md"]
    for path in scanned:
        if not path.exists():
            error(rel(path), "missing")
            continue
        text = read(path)
        for token in BACKTICKED.findall(text):
            token = token.strip()
            if SLASH_COMMAND.match(token):
                name = token[1:]
                if name in BUILTIN_COMMANDS:
                    continue
                if name not in known_skills and name not in deferred:
                    error(rel(path), f"references skill /{name}, which does not exist")
                continue
            if PATH_LIKE.match(token) and not (REPO_ROOT / token).exists():
                error(rel(path), f"references path `{token}`, which does not exist")
        for target in MAKE_TARGET.findall(text):
            if targets and target not in targets:
                error(rel(path), f"references `make {target}`, which is not a Makefile target")
        for single, group in AGENT_MENTION.findall(text):
            names = [single] if single else re.findall(r"`([a-z][a-z0-9-]*)`", group)
            for name in names:
                if name and name not in known_agents and name not in deferred:
                    error(rel(path), f"references agent `{name}`, which does not exist")


# --- memory pointers ----------------------------------------------------------


def check_claude_md_budget() -> None:
    if not CLAUDE_MD.exists():
        error(rel(CLAUDE_MD), "missing")
        return
    lines = len(read(CLAUDE_MD).splitlines())
    if lines > CLAUDE_MD_MAX_LINES:
        error(rel(CLAUDE_MD), f"{lines} lines exceeds the {CLAUDE_MD_MAX_LINES}-line budget (rule 3)")
    elif lines >= CLAUDE_MD_WARN_LINES:
        warn(rel(CLAUDE_MD), f"{lines} lines; the budget is {CLAUDE_MD_MAX_LINES} (rule 3)")


def plan_steps(path: Path) -> dict[str, str]:
    """Map step id -> status for one plan file."""
    steps: dict[str, str] = {}
    current = None
    for line in read(path).splitlines():
        heading = re.match(r"^###\s+(step-[a-z]*-?\d+)\b", line)
        if heading:
            current = heading.group(1)
            continue
        status = re.match(r"^-\s+\*\*Status\*\*:\s*([a-z ]+?)\.?\s*$", line)
        if status and current:
            value = status.group(1).strip()
            if value not in STATUSES:
                error(rel(path), f"{current} has unknown status {value!r}")
            steps[current] = value
            current = None
    return steps


def track_of(step_id: str) -> str:
    match = re.match(r"^step-([a-z]+)-\d+$", step_id)
    return match.group(1) if match else "root"


def check_pointers() -> None:
    all_steps: dict[str, dict[str, str]] = {}
    for track, path in PLANS.items():
        if not path.exists():
            error(rel(path), "missing")
            continue
        all_steps[track] = plan_steps(path)

    in_progress = [
        f"{step} ({track})"
        for track, steps in all_steps.items()
        for step, status in steps.items()
        if status == "in progress"
    ]
    if len(in_progress) > 1:
        error("plans", f"more than one step in progress repository-wide (rule 6): {', '.join(in_progress)}")

    if not CLAUDE_MD.exists():
        return
    pointer = re.search(r"Current step:\s*\*\*(step-[a-z]*-?\d+)\s*\(([a-z ]+)\)\*\*", read(CLAUDE_MD))
    if not pointer:
        error(rel(CLAUDE_MD), "Current state does not name a step as 'Current step: **step-... (status)**'")
        return
    step_id, status = pointer.group(1), pointer.group(2).strip()
    track = track_of(step_id)
    steps = all_steps.get(track)
    if steps is None:
        error(rel(CLAUDE_MD), f"current step {step_id} names track {track!r}, which has no plan")
        return
    if step_id not in steps:
        error(rel(CLAUDE_MD), f"current step {step_id} is not in {rel(PLANS[track])}")
    elif steps[step_id] != status:
        error(
            rel(CLAUDE_MD),
            f"current step {step_id} is {status!r} here but {steps[step_id]!r} in {rel(PLANS[track])}",
        )


def main() -> int:
    check_settings()
    check_tooling_frontmatter()
    check_references()
    check_claude_md_budget()
    check_pointers()

    for message in errors:
        print(f"error: {message}")
    for message in warnings:
        print(f"warning: {message}")
    if errors:
        return 1
    return 2 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
