#!/usr/bin/env bash
# The one documented setup command (via `make setup`): installs every pinned
# harness dependency and points git at the repository's hooks. Idempotent;
# `--force` reinstalls from scratch.

# shellcheck source=tools/lib.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/lib.sh"
# shellcheck source=tools/tool-versions.sh
source "${REPO_ROOT}/tools/tool-versions.sh"

FORCE=""
[ "${1:-}" = "--force" ] && FORCE=1

os="$(uname -s)"
arch="$(uname -m)"
[ "$os" = "Linux" ] && [ "$arch" = "x86_64" ] ||
  die "harness toolchain is pinned for linux/x86_64 only (found ${os}/${arch}); \
the images themselves are linux/amd64 too (root spec 2.1)"

command -v python3 >/dev/null || die "python3 is required"
command -v curl >/dev/null || die "curl is required"
command -v tar >/dev/null || die "tar is required"

stamp_want="shellcheck=${SHELLCHECK_VERSION} hadolint=${HADOLINT_VERSION} $(
  sha256sum "${REPO_ROOT}/tools/requirements.txt" | cut -d' ' -f1
)"

if [ -n "$FORCE" ]; then
  info "removing existing toolchain (--force)"
  rm -rf "$VENV_DIR" "${REPO_ROOT}/.tools"
fi

if [ -f "$TOOLS_STAMP" ] && [ "$(cat "$TOOLS_STAMP")" = "$stamp_want" ] &&
  [ -x "${VENV_BIN}/yamllint" ]; then
  ok "toolchain already at pinned versions"
else
  info "installing pinned Python tools into .venv"
  [ -x "${VENV_BIN}/python" ] || python3 -m venv "$VENV_DIR"
  "${VENV_BIN}/python" -m pip install --quiet --upgrade pip >/dev/null
  "${VENV_BIN}/python" -m pip install --quiet --disable-pip-version-check \
    --requirement "${REPO_ROOT}/tools/requirements.txt"

  mkdir -p "$TOOLS_BIN"
  install_binary() {
    local name="$1" version="$2" want_sha="$3" url="$4" archive="$5"
    local tmp got
    tmp="$(mktemp -d)"
    info "fetching ${name} ${version}"
    curl --fail --silent --show-error --location --output "${tmp}/dl" "$url"
    got="$(sha256sum "${tmp}/dl" | cut -d' ' -f1)"
    if [ "$got" != "$want_sha" ]; then
      rm -rf "$tmp"
      die "${name} ${version} checksum mismatch: expected ${want_sha}, got ${got}"
    fi
    if [ "$archive" = "tar.xz" ]; then
      tar --extract --xz --file "${tmp}/dl" --directory "$tmp"
      find "$tmp" -type f -name "$name" -exec install -m 0755 {} \
        "${TOOLS_BIN}/${name}" \;
    else
      install -m 0755 "${tmp}/dl" "${TOOLS_BIN}/${name}"
    fi
    rm -rf "$tmp"
  }

  install_binary shellcheck "$SHELLCHECK_VERSION" "$SHELLCHECK_SHA256" \
    "https://github.com/koalaman/shellcheck/releases/download/${SHELLCHECK_VERSION}/shellcheck-${SHELLCHECK_VERSION}.linux.x86_64.tar.xz" \
    tar.xz
  install_binary hadolint "$HADOLINT_VERSION" "$HADOLINT_SHA256" \
    "https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-linux-x86_64" \
    raw

  printf '%s' "$stamp_want" >"$TOOLS_STAMP"
  ok "toolchain installed"
fi

# Pre-commit hooks run the same harness as `make check` (rule 2).
git -C "$REPO_ROOT" config core.hooksPath .githooks
ok "git hooks path set to .githooks"

info "installed versions"
"${VENV_BIN}/yamllint" --version
"${VENV_BIN}/pymarkdown" version | sed 's/^/pymarkdown /'
"${VENV_BIN}/ruff" --version
"${VENV_BIN}/check-jsonschema" --version
"${TOOLS_BIN}/shellcheck" --version | sed -n 's/^version: /shellcheck /p'
"${TOOLS_BIN}/hadolint" --version

say ""
say "Next: make check   (working tree well-formed)"
say "      make test    (harness behavior against fixtures)"
say "      make verify  (both)"
