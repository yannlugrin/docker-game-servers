#!/usr/bin/env python3
"""PreToolUse guard for CLAUDE.md rule 9's boundary.

Permission patterns match a command prefix, which is not enough for three
rules this repository needs enforced mechanically:

* `gh api` is one command for both reads and writes — the method decides;
* a flag anywhere in the line changes the act (`git commit … --amend`,
  `docker … prune` without a scoping filter, `curl -X POST`);
* rule 1's read ban on `.claude/spec-work/` (bar `handoff/assets/`) has to
  hold for shell commands too, not only for the Read tool.

Decisions: **deny** what has no authorized use at all, **ask** for everything
rule 9 gates, stay silent otherwise so the permission rules decide. Silence is
never an approval — it just means this guard has no opinion.
"""

from __future__ import annotations

import json
import re
import sys

SPEC_WORK_BAN = re.compile(r"\.claude/spec-work(?!/handoff/assets)")

# (pattern, reason) — checked against the whole command line.
DENY: list[tuple[re.Pattern[str], str]] = [
    (SPEC_WORK_BAN, "rule 1: the specification phase's archive is not an input to implementation"),
    (
        re.compile(r"\bgit\s+push\b.*?(--force\b|--force-with-lease\b|\s-f\b|--mirror\b|--delete\b)"),
        "rule 6: history is linear and published state is never rewritten",
    ),
    (
        re.compile(r"\bgit\s+(filter-branch|filter-repo)\b"),
        "rule 6: rewriting history has no authorized use here",
    ),
    (
        # Position-independent: `git tag -a -f step-000` moves a tag as surely
        # as `git tag -f` does, and `-a` is allow-listed.
        re.compile(r"\bgit\s+tag\b(?=.*(\s-d\b|\s--delete\b|\s-f\b|\s--force\b))"),
        "rule 6: step tags mark operator-approved states and are never moved or deleted",
    ),
    (
        re.compile(r"\bgit\s+(reflog\s+(expire|delete)|gc\s+.*--prune|update-ref\s+-d)\b"),
        "rule 9: destroying git's recovery data has no authorized use",
    ),
]

ASK: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bgit\s+push\b"), "rule 9: pushing is an outward write"),
    (
        re.compile(r"\bgit\s+(commit\b.*--amend|rebase\b|reset\s+(--hard|--merge|--keep)\b)"),
        "rule 9: this rewrites history or destroys committed state",
    ),
    (
        re.compile(r"\bgit\s+(clean\b|stash\s+(drop|clear)\b|restore\b|checkout\s+--\s|branch\s+-[dD]\b)"),
        "rule 9: this destroys uncommitted or untracked work",
    ),
    (
        re.compile(
            r"\bdocker\s+(compose\s+)?push\b"
            r"|\bdocker\s+(image|manifest)\s+push\b"
            # `docker build --push` is the modern spelling; so is an
            # `--output type=registry`, which publishes without saying "push".
            # `docker compose build --push` and `buildx bake --push` publish too.
            r"|\bdocker\s+(compose\s+|buildx\s+)?(build|bake)\b.*"
            r"(--push\b|--output[= ][^|;]*type=registry)"
        ),
        "rule 9: publishing an image outward (release tags are immutable, root spec 7)",
    ),
    (
        re.compile(r"\bdocker\s+system\s+prune\b"),
        "rule 9: host-global prune — this host runs other projects",
    ),
    (
        re.compile(
            r"\bdocker\s+(image|volume|container|network|builder|buildx)\s+prune\b(?!.*(--filter|-f\s+label))"
        ),
        "rule 9: unscoped prune — scope it by label or filter to this project",
    ),
    (
        # The separator is optional: -XPOST, -X POST and --method=POST all work.
        re.compile(r"\bgh\s+api\b.*(-X\s*|--method[=\s])(?!GET\b|HEAD\b)\w"),
        "rule 9: a non-GET gh api call is a GitHub write",
    ),
    (
        re.compile(r"\bgh\s+api\b.*(--input\b|-f\s|--field\b|--raw-field\b|-F\s)"),
        "rule 9: gh api with fields posts a write",
    ),
    (
        re.compile(r"\bgh\s+(workflow\s+run|secret|variable|cache\s+delete|label\s+(create|delete))\b"),
        "rule 9: a GitHub write through gh",
    ),
    (
        re.compile(
            r"\bgh\s+(pr|issue|release|repo|gist)\s+"
            r"(create|edit|merge|close|delete|upload|comment|review|ready|reopen|archive|rename|transfer)\b"
        ),
        "rule 9: a GitHub write through gh",
    ),
    (
        re.compile(
            r"\b(curl|wget)\b.*("
            r"(-X\s*|--request[=\s])(?!GET\b|HEAD\b)\w"
            r"|--data\b|--data-\w+\b|\s-d[\s@']|--json\b|--form\b|\s-F[\s@']"
            r"|--upload-file\b|\s-T\s|--post-data\b|--post-file\b|--method[=\s](?!GET\b|HEAD\b)\w"
            r")"
        ),
        "rule 9: this HTTP call writes rather than reads",
    ),
]

FILE_TOOLS = {"Read", "Edit", "Write", "NotebookEdit", "MultiEdit"}
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
SPEC_FILES = re.compile(r"(^|/)SPECIFICATIONS\.md$")
REFS_DIR = re.compile(r"\.claude/refs/")


def decide(tool_name: str, tool_input: dict) -> tuple[str, str] | None:
    if tool_name == "Bash":
        command = str(tool_input.get("command", ""))
        for pattern, reason in DENY:
            if pattern.search(command):
                return "deny", reason
        for pattern, reason in ASK:
            if pattern.search(command):
                return "ask", reason
        return None

    if tool_name in FILE_TOOLS:
        path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        if SPEC_WORK_BAN.search(path):
            return "deny", "rule 1: the specification phase's archive is not an input to implementation"
        if tool_name in EDIT_TOOLS:
            if REFS_DIR.search(path):
                return "deny", "rule 3: operator-supplied references are never edited"
            if SPEC_FILES.search(path):
                return (
                    "ask",
                    "rule 1: specifications are read-only — an amendment needs the operator's agreement "
                    "and lands with its decision entry in one commit",
                )
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        verdict = decide(str(payload.get("tool_name", "")), payload.get("tool_input") or {})
    # A broken guard must not fail open: any internal error becomes an ask.
    except Exception as exc:
        verdict = ("ask", f"guard hook error, decide manually: {exc}")

    if verdict is None:
        return 0

    decision, reason = verdict
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
