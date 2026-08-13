"""tools/governance.py: does it catch the states it exists to catch?"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO / "tools" / "governance.py"

CLEAN = 0
ERROR = 1
WARNING = 2


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        env={"GOVERNANCE_ROOT": str(root), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """The smallest tree governance.py considers well-formed."""
    (tmp_path / ".claude" / "skills" / "orient").mkdir(parents=True)
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / "steamcmd").mkdir()
    (tmp_path / "project-zomboid").mkdir()

    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\n"
        "Rituals: `/orient`. Not yet adopted: `state-reviewer`.\n\n"
        "## Current state\n\n"
        "Active track: root. Current step: **step-000 (pending)**\n"
    )
    (tmp_path / "README.md").write_text("# repo\n")
    (tmp_path / "PLAN.md").write_text("### step-000 — Foundation\n\n- **Status**: pending.\n")
    (tmp_path / "steamcmd" / "PLAN.md").write_text("### step-sc-001 — Builder\n\n- **Status**: pending.\n")
    (tmp_path / "project-zomboid" / "PLAN.md").write_text(
        "### step-pz-001 — Facts\n\n- **Status**: pending.\n"
    )
    (tmp_path / ".claude" / "settings.json").write_text('{"autoMemoryEnabled": false}\n')
    (tmp_path / ".claude" / "skills" / "orient" / "SKILL.md").write_text(
        "---\nname: orient\ndescription: Orientation.\n---\n\nRead `PLAN.md`.\n"
    )
    return tmp_path


def test_clean_tree_passes(repo: Path):
    assert run(repo).returncode == CLEAN


def test_the_repository_itself_is_clean():
    result = run(REPO)
    assert result.returncode in (CLEAN, WARNING), result.stdout


def test_claude_md_over_budget_fails(repo: Path):
    with (repo / "CLAUDE.md").open("a") as handle:
        handle.write("filler\n" * 210)
    result = run(repo)
    assert result.returncode == ERROR
    assert "budget" in result.stdout


def test_claude_md_near_budget_warns(repo: Path):
    path = repo / "CLAUDE.md"
    padding = 195 - len(path.read_text().splitlines())
    with path.open("a") as handle:
        handle.write("filler\n" * padding)
    result = run(repo)
    assert result.returncode == WARNING
    assert "budget" in result.stdout


def test_unparseable_settings_fail(repo: Path):
    (repo / ".claude" / "settings.json").write_text('{"autoMemoryEnabled": false,\n')
    assert "does not parse" in run(repo).stdout


def test_auto_memory_must_stay_off(repo: Path):
    (repo / ".claude" / "settings.json").write_text('{"autoMemoryEnabled": true}\n')
    result = run(repo)
    assert result.returncode == ERROR
    assert "autoMemoryEnabled" in result.stdout


def test_broken_skill_frontmatter_fails(repo: Path):
    (repo / ".claude" / "skills" / "orient" / "SKILL.md").write_text("no frontmatter here\n")
    result = run(repo)
    assert result.returncode == ERROR
    assert "frontmatter" in result.stdout


def test_dangling_path_reference_fails(repo: Path):
    skill = repo / ".claude" / "skills" / "orient" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nAlso read `does-not-exist.md`.\n")
    result = run(repo)
    assert result.returncode == ERROR
    assert "does-not-exist.md" in result.stdout


def test_dangling_agent_reference_fails(repo: Path):
    skill = repo / ".claude" / "skills" / "orient" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nRun the `no-such-reviewer` agent.\n")
    result = run(repo)
    assert result.returncode == ERROR
    assert "no-such-reviewer" in result.stdout


def test_not_yet_adopted_agents_may_be_named(repo: Path):
    skill = repo / ".claude" / "skills" / "orient" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nLater, the `state-reviewer` agent does this.\n")
    assert run(repo).returncode == CLEAN


def test_pointer_disagreeing_with_the_plan_fails(repo: Path):
    (repo / "PLAN.md").write_text("### step-000 — Foundation\n\n- **Status**: done.\n")
    result = run(repo)
    assert result.returncode == ERROR
    assert "step-000" in result.stdout


def test_two_steps_in_progress_fail(repo: Path):
    (repo / "PLAN.md").write_text("### step-000 — Foundation\n\n- **Status**: in progress.\n")
    (repo / "project-zomboid" / "PLAN.md").write_text(
        "### step-pz-001 — Facts\n\n- **Status**: in progress.\n"
    )
    result = run(repo)
    assert result.returncode == ERROR
    assert "more than one step in progress" in result.stdout
