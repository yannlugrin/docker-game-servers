#!/usr/bin/env bash
# `make check` — is the working tree well-formed? Every language and artifact
# the repository ships gets a family here (CLAUDE.md rule 2). Untracked files
# are included; gitignored paths and HARNESS_EXCLUDES are not.
#
# Usage: tools/check.sh [--only FAMILY[,FAMILY...]] [--list]
# A narrowed run is fine mid-step; the commit that receives a step tag runs
# the full one.

# shellcheck source=tools/lib.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/lib.sh"

FAMILIES=(markdown yaml workflows compose shell dockerfile python json governance)
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --only) ONLY="${2:-}"; shift 2 ;;
    --only=*) ONLY="${1#--only=}"; shift ;;
    --list) printf '%s\n' "${FAMILIES[@]}"; exit 0 ;;
    *) die "unknown argument: $1 (see --list)" ;;
  esac
done

require_toolchain
cd "$REPO_ROOT"

failures=()
warnings=()

# Runs one family: name, then the command. Exit 0 = pass, 2 = warnings only,
# anything else = failure. Output is shown only when it is not a clean pass.
run_family() {
  local name="$1"; shift
  local out status
  out="$("$@" 2>&1)" && status=0 || status=$?
  case "$status" in
    0) ok "$name" ;;
    2) warned "$name"; [ -n "$out" ] && printf '%s\n' "$out"; warnings+=("$name") ;;
    *) bad "$name"; [ -n "$out" ] && printf '%s\n' "$out"; failures+=("$name") ;;
  esac
}

# --- family implementations -------------------------------------------------

fam_markdown() {
  local files
  mapfile -t files < <(harness_files '*.md')
  [ ${#files[@]} -eq 0 ] && { echo "no markdown files"; return 0; }
  "${VENV_BIN}/pymarkdown" --config "${REPO_ROOT}/.pymarkdown.json" \
    scan "${files[@]}"
}

fam_yaml() {
  local files
  mapfile -t files < <(harness_files '*.yml' '*.yaml')
  [ ${#files[@]} -eq 0 ] && { echo "no yaml files"; return 0; }
  "${VENV_BIN}/yamllint" --strict --config-file "${REPO_ROOT}/.yamllint.yml" \
    "${files[@]}"
}

fam_workflows() {
  local files
  mapfile -t files < <(harness_files '.github/workflows/*.yml' \
    '.github/workflows/*.yaml')
  [ ${#files[@]} -eq 0 ] && { echo "no workflow files"; return 0; }
  "${VENV_BIN}/check-jsonschema" --builtin-schema vendor.github-workflows \
    "${files[@]}"
}

fam_compose() {
  local files file status=0
  mapfile -t files < <(harness_files '*compose*.yml' '*compose*.yaml')
  [ ${#files[@]} -eq 0 ] && { echo "no compose files"; return 0; }
  command -v docker >/dev/null ||
    { echo "docker is required to validate compose files"; return 1; }
  for file in "${files[@]}"; do
    docker compose --file "$file" config --quiet || status=1
  done
  return "$status"
}

fam_shell() {
  local files file status=0
  mapfile -t files < <(harness_files '*.sh' '.githooks/*')
  [ ${#files[@]} -eq 0 ] && { echo "no shell files"; return 0; }
  for file in "${files[@]}"; do
    bash -n "$file" || status=1
  done
  "${TOOLS_BIN}/shellcheck" --severity=style --external-sources \
    "${files[@]}" || status=1
  return "$status"
}

fam_dockerfile() {
  local files
  mapfile -t files < <(harness_files '*Dockerfile' '*Dockerfile.*' \
    '*/Dockerfile' 'Dockerfile')
  [ ${#files[@]} -eq 0 ] && { echo "no Dockerfiles yet"; return 0; }
  "${TOOLS_BIN}/hadolint" --config "${REPO_ROOT}/.hadolint.yaml" "${files[@]}"
}

fam_python() {
  local files status=0
  mapfile -t files < <(harness_files '*.py')
  [ ${#files[@]} -eq 0 ] && { echo "no python files"; return 0; }
  "${VENV_BIN}/ruff" check --config "${REPO_ROOT}/ruff.toml" \
    "${files[@]}" || status=1
  "${VENV_BIN}/ruff" format --check --config "${REPO_ROOT}/ruff.toml" \
    "${files[@]}" || status=1
  "${VENV_BIN}/python" -m py_compile "${files[@]}" || status=1
  return "$status"
}

fam_json() {
  local files
  mapfile -t files < <(harness_files '*.json')
  [ ${#files[@]} -eq 0 ] && { echo "no json files"; return 0; }
  "${VENV_BIN}/python" - "${files[@]}" <<'PY'
import json
import sys

status = 0
for path in sys.argv[1:]:
    try:
        with open(path, encoding="utf-8") as handle:
            json.load(handle)
    except (OSError, ValueError) as exc:
        print(f"{path}: {exc}")
        status = 1
sys.exit(status)
PY
}

fam_governance() {
  "${VENV_BIN}/python" "${REPO_ROOT}/tools/lint_governance.py"
}

# --- driver -----------------------------------------------------------------

selected=("${FAMILIES[@]}")
if [ -n "$ONLY" ]; then
  IFS=',' read -r -a selected <<<"$ONLY"
  for name in "${selected[@]}"; do
    printf '%s\n' "${FAMILIES[@]}" | grep -qx -- "$name" ||
      die "unknown family: ${name} (see --list)"
  done
fi

info "check — ${#selected[@]} famil$([ ${#selected[@]} = 1 ] && echo y || echo ies)"
for name in "${selected[@]}"; do
  run_family "$name" "fam_${name}"
done

say ""
if [ ${#failures[@]} -gt 0 ]; then
  bad "check failed: ${failures[*]}"
  exit 1
fi
if [ ${#warnings[@]} -gt 0 ]; then
  warned "check passed with warnings: ${warnings[*]}"
  exit 0
fi
ok "check passed"
