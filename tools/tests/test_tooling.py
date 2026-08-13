"""Tests for the two scripts this repository ships.

One case per rule, not per spelling: enough to show each rule works, and
cheap enough that nobody is tempted to skip them.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
GOVERNANCE = REPO / "tools" / "governance.py"
GUARD = REPO / ".claude" / "hooks" / "guard.py"

CLEAN, ERROR, WARNING = 0, 1, 2
SILENT, ASK, DENY = "silent", "ask", "deny"


# --- tools/governance.py ------------------------------------------------------


def governance(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GOVERNANCE)],
        env={"GOVERNANCE_ROOT": str(root), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """The smallest tree governance.py considers well-formed."""
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text('{"autoMemoryEnabled": false}\n')
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\n## Current state\n\nCurrent step: **step-000 (pending)**\n"
    )
    (tmp_path / "PLAN.md").write_text("### step-000 — Foundation\n\n- **Status**: pending.\n")
    return tmp_path


def test_a_well_formed_tree_passes(repo: Path):
    assert governance(repo).returncode == CLEAN


def test_the_repository_itself_passes():
    assert governance(REPO).returncode in (CLEAN, WARNING), governance(REPO).stdout


def test_pointer_disagreeing_with_the_plan_fails(repo: Path):
    (repo / "PLAN.md").write_text("### step-000 — Foundation\n\n- **Status**: done.\n")
    result = governance(repo)
    assert result.returncode == ERROR
    assert "step-000" in result.stdout


def test_two_steps_in_progress_fail(repo: Path):
    """A second track's plan is found by glob — adding a game edits nothing."""
    (repo / "PLAN.md").write_text("### step-000 — Foundation\n\n- **Status**: in progress.\n")
    (repo / "new-game").mkdir()
    (repo / "new-game" / "PLAN.md").write_text("### step-ng-001 — Facts\n\n- **Status**: in progress.\n")
    assert "more than one step in progress" in governance(repo).stdout


def test_claude_md_budget(repo: Path):
    path = repo / "CLAUDE.md"
    body = path.read_text()
    path.write_text(body + "filler\n" * (195 - len(body.splitlines())))
    assert governance(repo).returncode == WARNING
    path.write_text(body + "filler\n" * 210)
    assert governance(repo).returncode == ERROR


def test_broken_skill_frontmatter_fails(repo: Path):
    skill = repo / ".claude" / "skills" / "orient"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("no frontmatter here\n")
    assert "frontmatter" in governance(repo).stdout


# --- .claude/hooks/guard.py ---------------------------------------------------


def verdict(tool: str, key: str, value: str) -> str:
    result = subprocess.run(
        [str(GUARD)],
        input=json.dumps({"tool_name": tool, "tool_input": {key: value}}),
        capture_output=True,
        text=True,
        check=False,
    )
    out = result.stdout.strip()
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else SILENT


# Every case is an allow-listed prefix with the act hiding later in the line —
# what the permission patterns cannot see, and why this hook exists.
GUARDED = [
    (SILENT, "Bash", "gh api repos/yannlugrin/docker-game-servers"),
    (ASK, "Bash", "gh api -XPOST /repos/x/y/releases"),
    (SILENT, "Bash", 'git commit -m "step-000: x"'),
    (ASK, "Bash", 'git commit -m "x" --amend'),
    (DENY, "Bash", "git push --force origin main"),
    (DENY, "Bash", 'git tag -a -f step-000 -m "x"'),
    (SILENT, "Bash", "docker build -t pz:dev project-zomboid"),
    (ASK, "Bash", "docker compose build --push"),
    (ASK, "Bash", "docker image prune -a"),
    (SILENT, "Bash", "docker image prune --filter label=project=games-servers"),
    (ASK, "Bash", "curl -XPOST https://example.test"),
    (DENY, "Bash", "cat .claude/spec-work/reviews/013.md"),
    (SILENT, "Bash", "grep -r x .claude/spec-work/handoff/assets/"),
    # A heredoc body is data — a commit message quoting a gated command is not
    # that command — unless it is fed to an interpreter, where it is.
    (SILENT, "Bash", "git commit -F - <<'EOF'\nstep-000: why git push --force is denied\nEOF"),
    (DENY, "Bash", "bash <<'EOF'\ngit push --force origin main\nEOF"),
    (DENY, "Edit", "/repo/.claude/refs/image-contract.md"),
    (ASK, "Edit", "/repo/project-zomboid/SPECIFICATIONS.md"),
    (SILENT, "Edit", "/repo/PLAN.md"),
]


@pytest.mark.parametrize(("expected", "tool", "value"), GUARDED, ids=lambda v: v[:38])
def test_guard_verdicts(expected: str, tool: str, value: str):
    key = "command" if tool == "Bash" else "file_path"
    assert verdict(tool, key, value) == expected


def test_a_broken_payload_asks_rather_than_failing_open():
    result = subprocess.run([str(GUARD)], input="not json", capture_output=True, text=True, check=False)
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == ASK
