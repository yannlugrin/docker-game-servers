#!/usr/bin/env bash
# `make test` — does the harness behave? Each case builds a throwaway copy of
# the working tree, plants one deliberately broken (or borderline) artifact in
# it, and asserts that `tools/check.sh` reacts as specified: must-fail cases
# fail, must-warn cases warn without failing, the control case stays green.
#
# A check family that cannot detect its own fixture is a family that would
# pass a broken repository just as happily.

# Case bodies are single-quoted on purpose: they are evaluated by the child
# shell that runs them, with $SNAP and $FIXTURES from its environment.
# shellcheck disable=SC2016

# shellcheck source=tools/lib.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/lib.sh"

require_toolchain
export FIXTURES="${REPO_ROOT}/tools/tests/fixtures"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

passed=0
failed=0
skipped=0

# A snapshot is the working tree minus git state and the installed toolchain,
# made into its own git repository so the harness's file discovery works, with
# the toolchain symlinked back in.
snapshot() {
  local dest="$1"
  mkdir -p "$dest"
  tar --create --directory "$REPO_ROOT" \
    --exclude=.git --exclude=.venv --exclude=.tools --exclude=.claude/worktrees \
    . | tar --extract --directory "$dest"
  ln -s "$VENV_DIR" "${dest}/.venv"
  ln -s "${REPO_ROOT}/.tools" "${dest}/.tools"
  git -C "$dest" init --quiet
}

# case <name> <family> <expected: fail|warn|pass> <expected output substring>
# The case body runs with $SNAP set to a fresh snapshot it may modify.
run_case() {
  local name="$1" family="$2" expect="$3" needle="$4" body="$5"
  local snap out status
  snap="${WORK}/${name}"
  snapshot "$snap"
  SNAP="$snap" bash -c "$body" || { bad "${name}: fixture setup failed"; failed=$((failed + 1)); return; }

  out="$("${snap}/tools/check.sh" --only "$family" 2>&1)" && status=0 || status=$?

  local problem=""
  case "$expect" in
    fail) [ "$status" -eq 0 ] && problem="expected a failure, check passed" ;;
    warn)
      [ "$status" -ne 0 ] && problem="expected a warning, check failed"
      grep -q "WARN" <<<"$out" || problem="${problem:-expected a WARN line, got none}"
      ;;
    pass) [ "$status" -eq 0 ] || problem="expected a clean pass, check failed" ;;
  esac
  if [ -z "$problem" ] && [ -n "$needle" ] && ! grep -qF -- "$needle" <<<"$out"; then
    problem="output does not mention: ${needle}"
  fi

  if [ -n "$problem" ]; then
    bad "${name} (${family}, must ${expect}): ${problem}"
    printf '%s\n' "$out" | sed 's/^/      | /'
    failed=$((failed + 1))
  else
    ok "${name} (${family}, must ${expect})"
    passed=$((passed + 1))
  fi
}

info "test — harness behavior against fixtures"

# --- per-language families: each must catch its own broken artifact ----------

run_case shell-syntax shell fail "syntax error" \
  'cp "$FIXTURES/shell/bad-syntax.sh" "$SNAP/planted.sh"'
run_case shell-lint shell fail "SC2086" \
  'cp "$FIXTURES/shell/unquoted.sh" "$SNAP/planted.sh"'
run_case markdown markdown fail "MD047" \
  'cp "$FIXTURES/markdown/bad.md" "$SNAP/planted.md"'
run_case yaml yaml fail "" \
  'cp "$FIXTURES/yaml/bad.yml" "$SNAP/planted.yml"'
run_case workflow-schema workflows fail "" \
  'mkdir -p "$SNAP/.github/workflows" && cp "$FIXTURES/workflows/invalid.yml" "$SNAP/.github/workflows/planted.yml"'
run_case json json fail "planted.json" \
  'cp "$FIXTURES/json/bad.json" "$SNAP/planted.json"'
run_case dockerfile dockerfile fail "DL3006" \
  'cp "$FIXTURES/dockerfile/bad.Dockerfile" "$SNAP/Dockerfile"'
run_case python python fail "" \
  'cp "$FIXTURES/python/bad.py" "$SNAP/planted.py"'

if command -v docker >/dev/null; then
  run_case compose compose fail "" \
    'cp "$FIXTURES/compose/bad-compose.yml" "$SNAP/compose.yml"'
else
  warned "compose (skipped: docker not available)"
  skipped=$((skipped + 1))
fi

# --- governance: the workflow's own load-bearing state -----------------------

run_case governance-clean governance pass "" 'true'
run_case settings-unparseable governance fail "does not parse as JSON" \
  'cp "$FIXTURES/governance/settings-unparseable.json" "$SNAP/.claude/settings.json"'
run_case settings-automemory governance fail "autoMemoryEnabled" \
  'cp "$FIXTURES/governance/settings-automemory-on.json" "$SNAP/.claude/settings.json"'
run_case skill-frontmatter governance fail "frontmatter" \
  'mkdir -p "$SNAP/.claude/skills/planted" && cp "$FIXTURES/governance/skill-broken-frontmatter.md" "$SNAP/.claude/skills/planted/SKILL.md"'
run_case skill-dangling-refs governance fail "does not exist" \
  'mkdir -p "$SNAP/.claude/skills/planted" && cp "$FIXTURES/governance/skill-dangling-refs.md" "$SNAP/.claude/skills/planted/SKILL.md"'
run_case claude-md-over-budget governance fail "budget" \
  'for i in $(seq 1 210); do echo "filler line $i"; done >>"$SNAP/CLAUDE.md"'
run_case claude-md-near-budget governance warn "budget is" \
  'lines=$(wc -l <"$SNAP/CLAUDE.md");
   [ "$lines" -lt 195 ] || { echo "fixture needs CLAUDE.md under 195 lines, found $lines" >&2; exit 1; };
   while [ "$lines" -lt 195 ]; do echo "" >>"$SNAP/CLAUDE.md"; lines=$((lines + 1)); done'
run_case broken-makefile governance fail "" \
  'printf "check:\n\techo unterminated \$(\n" >"$SNAP/Makefile"'
run_case pointer-status-mismatch governance fail "but" \
  'sed -i "s/\(Current step: \*\*step-000\) ([a-z ]*)\*\*/\1 (pending)**/" "$SNAP/CLAUDE.md" &&
   sed -i "0,/- \*\*Status\*\*: [a-z ]*\./s//- **Status**: done./" "$SNAP/PLAN.md"'
run_case two-steps-in-progress governance fail "more than one step in progress" \
  'sed -i "0,/- \*\*Status\*\*: pending./s//- **Status**: in progress./" "$SNAP/PLAN.md" &&
   sed -i "0,/- \*\*Status\*\*: pending./s//- **Status**: in progress./" "$SNAP/project-zomboid/PLAN.md"'

# --- the rule-9 guard hook: verdicts on the spellings that matter -----------
#
# The hook exists because permission patterns match a prefix: every case below
# has an allow-listed prefix and an outward write hiding later in the line.

guard_verdict() {
  local tool="$1" value="$2" key="command" out
  [ "$tool" = "Bash" ] || key="file_path"
  out="$("${VENV_BIN}/python" - "$tool" "$key" "$value" <<'PY'
import json
import subprocess
import sys

tool, key, value = sys.argv[1:4]
payload = json.dumps({"tool_name": tool, "tool_input": {key: value}})
result = subprocess.run(
    [".claude/hooks/guard.py"], input=payload, capture_output=True, text=True, check=False
)
out = result.stdout.strip()
print(json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else "silent")
PY
  )"
  printf '%s' "$out"
}

guard_case() {
  local label="$1" expect="$2" tool="$3" value="$4" got
  got="$(guard_verdict "$tool" "$value")"
  if [ "$got" = "$expect" ]; then
    ok "guard: ${label} (${expect})"
    passed=$((passed + 1))
  else
    bad "guard: ${label}: expected ${expect}, got ${got} — for: ${value}"
    failed=$((failed + 1))
  fi
}

guard_case "gh api read" silent Bash "gh api repos/yannlugrin/docker-game-servers"
guard_case "gh api -X DELETE" ask Bash "gh api -X DELETE /user/packages/container/steamcmd"
guard_case "gh api -XPOST" ask Bash "gh api -XPOST /repos/x/y/releases"
guard_case "gh api --method=POST" ask Bash "gh api --method=POST /repos/x/y/releases"
guard_case "gh api -f field" ask Bash "gh api /repos/x/y/dispatches -f event_type=go"
guard_case "gh workflow run" ask Bash "gh workflow run publish.yml"
guard_case "git commit" silent Bash 'git commit -m "step-000: x"'
guard_case "git commit --amend late" ask Bash 'git commit -m "x" --amend'
guard_case "git push" ask Bash "git push origin main"
guard_case "git push --force" deny Bash "git push --force origin main"
guard_case "git tag -a" silent Bash 'git tag -a step-000 -m "x"'
guard_case "git tag -d" deny Bash "git tag -d step-000"
guard_case "git tag -a -f (late flag)" deny Bash 'git tag -a -f step-000 -m "x"'
guard_case "docker build" silent Bash "docker build -t pz:dev project-zomboid"
guard_case "docker build --push" ask Bash "docker build --push -t ghcr.io/x/y:1 ."
guard_case "buildx --output registry" ask Bash "docker buildx build --output type=registry -t ghcr.io/x/y:1 ."
guard_case "compose build --push" ask Bash "docker compose build --push"
guard_case "buildx bake --push" ask Bash "docker buildx bake --push release"
guard_case "docker manifest push" ask Bash "docker manifest push ghcr.io/x/y:1"
guard_case "docker push" ask Bash "docker push ghcr.io/x/y:1"
guard_case "docker volume rm" silent Bash "docker volume rm pz-test"
guard_case "unscoped prune" ask Bash "docker image prune -a"
guard_case "scoped prune" silent Bash "docker image prune --filter label=project=games-servers"
guard_case "docker system prune" ask Bash "docker system prune -af"
guard_case "curl read" silent Bash "curl -sS https://api.steampowered.com/x"
guard_case "curl -XPOST" ask Bash "curl -XPOST https://example.test"
guard_case "curl --json" ask Bash "curl --json '{}' https://example.test"
guard_case "wget --post-data" ask Bash "wget --post-data=a=b https://example.test"
guard_case "cat the archive" deny Bash "cat .claude/spec-work/reviews/013.md"
guard_case "list the archive" deny Bash "ls .claude/spec-work"
guard_case "grep handoff assets" silent Bash "grep -r x .claude/spec-work/handoff/assets/"
guard_case "read the archive" deny Read "/repo/.claude/spec-work/decisions.md"
guard_case "edit refs" deny Edit "/repo/.claude/refs/image-contract.md"
guard_case "edit a specification" ask Edit "/repo/project-zomboid/SPECIFICATIONS.md"
guard_case "edit a plan" silent Edit "/repo/PLAN.md"

say ""
if [ "$failed" -gt 0 ]; then
  bad "test failed: ${failed} of $((passed + failed)) cases (skipped: ${skipped})"
  exit 1
fi
ok "test passed: ${passed} cases (skipped: ${skipped})"
