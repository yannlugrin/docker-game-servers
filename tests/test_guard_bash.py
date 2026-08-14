"""Behaviour of the PreToolUse Bash guard.

The guard is exercised through its real contract — a JSON tool call on
stdin, a JSON decision on stdout — rather than by importing its
internals, because that contract is what Claude Code actually invokes.

Two outcomes are asserted, and the difference matters:

- *pass through* (exit 0, no decision): the guard stays out of the way
  and the permission rules in `.claude/settings.json` decide. Commands
  the operator gates with an ask rule land here; a pass-through is not
  a claim that the command runs.
- *refused* (a `deny` decision): the guard blocks a form that an allow
  rule would otherwise have admitted without a prompt.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
GUARD = REPOSITORY / ".claude" / "hooks" / "guard-bash.py"


def invoke(payload):
    """Run the guard on one hook payload and return (exit code, decision)."""
    completed = subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload) if isinstance(payload, dict) else payload,
        capture_output=True,
        text=True,
        check=False,
    )
    decision = None
    if completed.stdout.strip():
        decision = json.loads(completed.stdout)["hookSpecificOutput"]
    return completed.returncode, decision


def call(command):
    """Run the guard on a Bash tool call carrying `command`."""
    return invoke(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command, "description": "test"},
        }
    )


class GuardAssertions(unittest.TestCase):
    def assertPassedThrough(self, command):
        code, decision = call(command)
        self.assertEqual(code, 0, f"guard refused {command!r}")
        self.assertIsNone(decision, f"guard returned a decision for {command!r}")

    def assertRefused(self, command, because=""):
        code, decision = call(command)
        self.assertNotEqual(code, 0, f"guard passed {command!r} through")
        self.assertIsNotNone(decision, f"guard gave no decision for {command!r}")
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn(because, decision["permissionDecisionReason"])


class TestEverydayCommandsPassThrough(GuardAssertions):
    """The development loop must not acquire a second layer of refusals."""

    def test_ordinary_commit(self):
        self.assertPassedThrough('git commit -m "step-001: land the guard"')

    def test_commit_with_several_message_flags(self):
        self.assertPassedThrough('git commit -m "subject" -m "body"')

    def test_staging_and_status(self):
        self.assertPassedThrough("git add -A")
        self.assertPassedThrough("git status --porcelain")

    def test_annotated_tag(self):
        self.assertPassedThrough('git tag -a step-001 -m "approved"')

    def test_tag_listing(self):
        self.assertPassedThrough("git tag -l 'step-*'")

    def test_harness(self):
        self.assertPassedThrough("just check changed")
        self.assertPassedThrough("just verify")

    def test_local_docker_loop(self):
        self.assertPassedThrough("docker build -t games-servers/steamcmd:dev .")
        self.assertPassedThrough("docker run --rm games-servers/steamcmd:dev")
        self.assertPassedThrough("docker rm -f pz-test")
        self.assertPassedThrough("docker compose up -d")
        self.assertPassedThrough("docker compose down -v")

    def test_delete_inside_the_disposable_state_root(self):
        self.assertPassedThrough("rm -rf .local/pz-test")

    def test_message_mentioning_a_guarded_flag(self):
        """A forbidden flag inside an option's *value* is text, not a flag."""
        self.assertPassedThrough('git commit -m "do not use --amend here"')
        self.assertPassedThrough('git commit -m "the -n flag skips hooks"')
        self.assertPassedThrough('git commit --message="never --no-verify"')


class TestGatedFormsStayWithTheOperator(GuardAssertions):
    """Commands rule 9 gates and no allow rule matches: not this guard's job."""

    def test_push_passes_through_to_its_ask_rule(self):
        self.assertPassedThrough("git push origin main")
        self.assertPassedThrough("docker push ghcr.io/owner/steamcmd:latest")

    def test_history_rewriting_without_an_allowed_prefix(self):
        self.assertPassedThrough("git rebase -i HEAD~2")
        self.assertPassedThrough("git reset --hard HEAD~1")
        self.assertPassedThrough("git clean -fd")

    def test_plain_amend_spelling_reaches_its_ask_rule(self):
        """`git commit --amend` matches its ask rule, so it must stay approvable."""
        self.assertPassedThrough('git commit --amend -m "reworded"')
        self.assertPassedThrough("git commit --amend --no-edit")

    def test_other_plain_spellings_reach_their_ask_rules(self):
        """Written first, each guarded flag is the spelling an ask rule matches."""
        self.assertPassedThrough('git commit --no-verify -m "x"')
        self.assertPassedThrough('git commit -n -m "x"')
        self.assertPassedThrough("git tag -d step-000")
        self.assertPassedThrough("git tag --delete step-000")
        self.assertPassedThrough("git tag -f step-000 HEAD")


class TestHistoryRewritingHiddenInAnAllowedPrefix(GuardAssertions):
    """The measured hole: a flag after the prefix an allow rule matched."""

    def test_amend_after_another_flag(self):
        self.assertRefused('git commit -a --amend -m "x"', because="--amend")

    def test_amend_at_the_end(self):
        self.assertRefused('git commit -m "x" --amend', because="--amend")

    def test_amend_in_a_bundled_short_group(self):
        self.assertRefused('git commit -am "x" --amend', because="--amend")

    def test_amend_by_git_abbreviation(self):
        self.assertRefused('git commit -a --amen -m "x"', because="--amend")

    def test_amend_behind_a_global_option(self):
        self.assertRefused('git -C . commit -a --amend -m "x"', because="--amend")

    def test_amend_behind_a_wrapper(self):
        self.assertRefused('timeout 30 git commit -a --amend -m "x"', because="--amend")
        self.assertRefused('nohup git commit -a --amend -m "x"', because="--amend")

    def test_amend_behind_an_environment_assignment(self):
        self.assertRefused('EDITOR=true git commit -a --amend -m "x"', because="--amend")

    def test_amend_in_a_compound_command(self):
        self.assertRefused('git add -A && git commit -a --amend -m "x"', because="--amend")
        self.assertRefused('git status; git commit -a --amend -m "x"', because="--amend")


class TestHarnessBypass(GuardAssertions):
    def test_no_verify_after_another_flag(self):
        self.assertRefused('git commit -m "x" --no-verify', because="--no-verify")

    def test_no_verify_bundled(self):
        self.assertRefused('git commit -an -m "x"', because="-n")

    def test_no_verify_by_git_abbreviation(self):
        self.assertRefused('git commit -a --no-ver -m "x"', because="--no-verify")


class TestTagIntegrity(GuardAssertions):
    def test_tag_deletion_hidden_behind_a_flag(self):
        self.assertRefused("git tag --sort=-v:refname -d step-000", because="-d")

    def test_tag_moved_onto_another_commit(self):
        self.assertRefused('git tag -a step-000 -m "x" --force', because="--force")
        self.assertRefused('git tag -a step-000 -m "x" -f', because="-f")


class TestPublishHiddenInABuild(GuardAssertions):
    def test_build_with_push(self):
        self.assertRefused("docker build --push -t ghcr.io/owner/x:dev .", because="--push")

    def test_buildx_build_with_push(self):
        self.assertRefused("docker buildx build --push .", because="--push")

    def test_buildx_bake_with_push(self):
        self.assertRefused("docker buildx bake --push", because="--push")

    def test_build_output_to_a_registry(self):
        self.assertRefused(
            "docker build -o type=registry,name=ghcr.io/owner/x:dev .", because="--output"
        )
        self.assertRefused(
            "docker build --output=type=registry,push=true .", because="--output"
        )

    def test_compose_push(self):
        self.assertRefused("docker compose push", because="compose push")
        self.assertRefused("docker compose -f compose.yaml push", because="compose push")


class TestDeleteEscapingTheStateRoot(GuardAssertions):
    def test_parent_traversal(self):
        self.assertRefused("rm -rf .local/../../other-project", because="..")

    def test_parent_traversal_deeper(self):
        self.assertRefused("rm -rf .local/pz/../../..", because="..")


class TestGuardContract(GuardAssertions):
    def test_other_tools_are_not_this_guards_business(self):
        code, decision = invoke(
            {"hook_event_name": "PreToolUse", "tool_name": "Edit",
             "tool_input": {"file_path": "/x", "old_string": "a", "new_string": "b"}}
        )
        self.assertEqual(code, 0)
        self.assertIsNone(decision)

    def test_unparsable_payload_is_not_a_refusal(self):
        code, decision = invoke("not json at all")
        self.assertEqual(code, 0)
        self.assertIsNone(decision)

    def test_missing_command_is_not_a_refusal(self):
        code, decision = invoke(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {}}
        )
        self.assertEqual(code, 0)
        self.assertIsNone(decision)

    def test_unparsable_command_is_still_classified(self):
        """A quoting mistake must not be a way past the guard."""
        self.assertRefused('git commit -m "unbalanced --amend', because="--amend")

    def test_unparsable_command_elsewhere_passes_through(self):
        self.assertPassedThrough('echo "unbalanced')

    def test_a_heredoc_script_is_ordinary_working_material(self):
        """Heredocs defeat the strict lexer; the loose pass must not refuse them."""
        script = (
            "cat > /tmp/probe.sh <<'SH'\n"
            "git status --porcelain\n"
            "git log --oneline -1\n"
            "SH\n"
            "bash /tmp/probe.sh"
        )
        self.assertPassedThrough(script)

    def test_a_heredoc_hiding_a_guarded_form_is_refused(self):
        script = "cat <<'SH'\ngit commit -a --amend -m x\nSH"
        self.assertRefused(script, because="--amend")

    def test_refusal_names_the_repository_and_says_nothing_ran(self):
        _, decision = call('git commit -a --amend -m "x"')
        self.assertIn("Nothing was run", decision["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main()
