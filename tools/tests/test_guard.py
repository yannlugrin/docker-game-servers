"""The rule-9 guard: every case is an allow-listed prefix with the act
hiding later in the line. The failure mode is silence, which no linter sees.
"""

import json
import subprocess
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parent.parent.parent / ".claude" / "hooks" / "guard.py"

SILENT, ASK, DENY = "silent", "ask", "deny"

BASH = [
    (SILENT, "gh api repos/yannlugrin/docker-game-servers"),
    (ASK, "gh api -X DELETE /user/packages/container/steamcmd"),
    (ASK, "gh api -XPOST /repos/x/y/releases"),
    (ASK, "gh api --method=POST /repos/x/y/releases"),
    (ASK, "gh api /repos/x/y/dispatches -f event_type=go"),
    (ASK, "gh workflow run publish.yml"),
    (SILENT, 'git commit -m "step-000: x"'),
    (ASK, 'git commit -m "x" --amend'),
    (ASK, "git push origin main"),
    (DENY, "git push --force origin main"),
    (SILENT, 'git tag -a step-000 -m "x"'),
    (DENY, "git tag -d step-000"),
    (DENY, 'git tag -a -f step-000 -m "x"'),
    (ASK, "git reset --hard HEAD~1"),
    (SILENT, "docker build -t pz:dev project-zomboid"),
    (ASK, "docker build --push -t ghcr.io/x/y:1 ."),
    (ASK, "docker compose build --push"),
    (ASK, "docker buildx build --output type=registry -t ghcr.io/x/y:1 ."),
    (ASK, "docker push ghcr.io/x/y:1"),
    (SILENT, "docker volume rm pz-test"),
    (ASK, "docker image prune -a"),
    (SILENT, "docker image prune --filter label=project=games-servers"),
    (ASK, "docker system prune -af"),
    (SILENT, "curl -sS https://api.steampowered.com/x"),
    (ASK, "curl -XPOST https://example.test"),
    (ASK, "wget --post-data=a=b https://example.test"),
    (DENY, "cat .claude/spec-work/reviews/013.md"),
    (DENY, "ls .claude/spec-work"),
    (SILENT, "grep -r x .claude/spec-work/handoff/assets/"),
    # A heredoc body is data — a commit message quoting a gated command is not
    # that command — unless it is fed to an interpreter, where it is.
    (SILENT, "git commit -F - <<'EOF'\nstep-000: why git push --force is denied\nEOF"),
    (DENY, "bash <<'EOF'\ngit push --force origin main\nEOF"),
]

FILES = [
    (DENY, "Read", "/repo/.claude/spec-work/decisions.md"),
    (SILENT, "Read", "/repo/PLAN.md"),
    (DENY, "Edit", "/repo/.claude/refs/image-contract.md"),
    (ASK, "Edit", "/repo/project-zomboid/SPECIFICATIONS.md"),
    (SILENT, "Edit", "/repo/PLAN.md"),
]


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


@pytest.mark.parametrize(("expected", "command"), BASH, ids=lambda v: v[:40])
def test_bash_commands(expected: str, command: str):
    assert verdict("Bash", "command", command) == expected


@pytest.mark.parametrize(("expected", "tool", "path"), FILES, ids=lambda v: v[:40])
def test_file_tools(expected: str, tool: str, path: str):
    assert verdict(tool, "file_path", path) == expected


def test_a_broken_payload_asks_rather_than_failing_open():
    result = subprocess.run([str(GUARD)], input="not json", capture_output=True, text=True, check=False)
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == ASK
