# The harness entry points (CLAUDE.md rule 2). `just --list` shows them all.
#
# No recipe here may perform an act rule 9 gates: the Bash guard sees
# `just <recipe>`, never the commands inside it.
#
# `--fmt`, which the check family runs over this file, is an unstable
# `just` feature and has to be enabled here.

set unstable := true

venv := justfile_directory() / ".venv"
pre_commit := venv / "bin" / "pre-commit"

# Show the available recipes.
default:
    @just --list

# Install the pinned toolchain into ./.venv and wire the git commit hooks.
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    python3 -m venv "{{ venv }}"
    "{{ venv }}/bin/pip" install --quiet --disable-pip-version-check --requirement requirements.txt
    "{{ pre_commit }}" install
    "{{ pre_commit }}" install-hooks
    echo "harness ready: $("{{ pre_commit }}" --version)"

# Is what is committed here well-formed? Pass a pathspec to narrow the scope.
check scope=".":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -x "{{ pre_commit }}" ]; then
        echo "the harness is not installed — run: just setup" >&2
        exit 1
    fi
    # Tracked and untracked files, gitignored paths excluded. The list is
    # passed explicitly because runners that enumerate from git — including
    # `pre-commit run --all-files` — see only what git already knows about.
    # `git add --intent-to-add` is never used to widen that view: it writes
    # to the index as a side effect of a check, which turns `?? file` into
    # ` A file` in the porcelain status the session rituals read, and lets
    # the next `git commit -a` sweep the file into an unrelated commit.
    mapfile -t -d '' files < <(git ls-files -z --cached --others --exclude-standard -- {{ quote(scope) }})
    if [ "${#files[@]}" -eq 0 ]; then
        echo "check: nothing to check under {{ quote(scope) }}" >&2
        exit 1
    fi
    "{{ pre_commit }}" run --files "${files[@]}"

# Is the implementation right? Behaviour this repository itself ships.
test:
    #!/usr/bin/env bash
    set -euo pipefail
    # The Bash guard's own registry is the first behaviour this repository
    # ships. --selftest runs liveness, then every case, then coverage: a rule
    # or grant that no case reaches fails it, which is what keeps the intent
    # executable rather than remembered.
    .claude/hooks/bash_guard.py --selftest

# Both gates, in order.
verify: check test
