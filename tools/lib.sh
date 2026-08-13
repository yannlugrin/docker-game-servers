# Shared helpers for the harness scripts. Sourced, never executed.
# shellcheck shell=bash

set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
VENV_BIN="${VENV_DIR}/bin"
TOOLS_BIN="${REPO_ROOT}/.tools/bin"
# shellcheck disable=SC2034  # used by tools/setup.sh
TOOLS_STAMP="${REPO_ROOT}/.tools/.stamp"

# Paths the harness never inspects, whatever they contain:
#   .claude/spec-work/  — the specification phase's archive (rule 1: not an
#                         input to implementation; not ours to keep lintable)
#   .claude/refs/       — operator-supplied reference material (rule 3: never
#                         edited, so never a finding we could act on)
#   tools/tests/fixtures/ — deliberately malformed inputs for `make test`
HARNESS_EXCLUDES=(
  ".claude/spec-work/"
  ".claude/refs/"
  "tools/tests/fixtures/"
)

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
  C_BOLD=$'\033[1m'; C_OFF=$'\033[0m'
else
  C_RED=""; C_GREEN=""; C_YELLOW=""; C_BOLD=""; C_OFF=""
fi

say() { printf '%s\n' "$*"; }
info() { printf '%s\n' "${C_BOLD}$*${C_OFF}"; }
ok() { printf '%s\n' "${C_GREEN}PASS${C_OFF}  $*"; }
warned() { printf '%s\n' "${C_YELLOW}WARN${C_OFF}  $*"; }
bad() { printf '%s\n' "${C_RED}FAIL${C_OFF}  $*"; }
die() { printf '%s\n' "${C_RED}error:${C_OFF} $*" >&2; exit 1; }

# The working tree as the harness sees it: tracked plus untracked files,
# gitignored paths dropped by git itself, HARNESS_EXCLUDES dropped by path.
# Optional arguments are shell glob patterns matched against the path.
harness_files() {
  local patterns=("$@") file keep pattern excluded
  while IFS= read -r file; do
    excluded=""
    for pattern in "${HARNESS_EXCLUDES[@]}"; do
      case "$file" in "$pattern"*) excluded=1; break ;; esac
    done
    [ -n "$excluded" ] && continue
    [ -e "${REPO_ROOT}/${file}" ] || continue
    if [ ${#patterns[@]} -eq 0 ]; then
      printf '%s\n' "$file"
      continue
    fi
    keep=""
    for pattern in "${patterns[@]}"; do
      # shellcheck disable=SC2254  # patterns are globs on purpose
      case "$file" in $pattern) keep=1; break ;; esac
    done
    [ -n "$keep" ] && printf '%s\n' "$file"
  done < <(git -C "$REPO_ROOT" ls-files --cached --others --exclude-standard)
  return 0
}

require_toolchain() {
  [ -x "${VENV_BIN}/yamllint" ] && [ -x "${TOOLS_BIN}/shellcheck" ] ||
    die "toolchain missing — run 'make setup' first"
}
