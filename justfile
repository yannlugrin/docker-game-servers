# Task runner for the local development loop.
#
# Prerequisites installed by hand, once, outside this repository:
# git, just, and python3 (>= 3.9) with its `venv` module. Everything
# else arrives through `just setup`.
#
# Nothing here holds its own list of checks. Both scopes of `check` and
# the git pre-commit hook all read `.pre-commit-config.yaml`, so they
# can differ in how much of the tree they look at and never in what
# they look for.
#
# Only the single comment line directly above a recipe reaches
# `just --list`; anything longer belongs in the recipe body.

venv := justfile_directory() / ".venv"
pre_commit := venv / "bin" / "pre-commit"

# Show the available recipes.
default:
    @just --list --unsorted

# Fresh clone -> working toolchain. The one documented setup command.
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    python3 -m venv "{{ venv }}"
    "{{ venv }}/bin/python" -m pip install --quiet --disable-pip-version-check \
        --requirement "{{ justfile_directory() }}/requirements.txt"
    "{{ pre_commit }}" install
    "{{ pre_commit }}" install-hooks
    echo "Setup complete. Try: just verify"

# Well-formedness. scope: all (whole tree, the gate) | changed (vs HEAD).
check scope="all": _require-tooling
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ justfile_directory() }}"
    case "{{ scope }}" in
    all)
        # The gate: step handover, milestone review, CI. Untracked files
        # included, gitignored paths excluded; `.claude/spec-work/` is
        # excluded by .pre-commit-config.yaml, keyed on path. The
        # enumeration stays read-only: never `git add --intent-to-add`,
        # which would write index state and corrupt the clean-tree
        # signal this gate depends on.
        mapfile -d '' files < <(git ls-files --cached --others --exclude-standard -z)
        empty="No files to check."
        ;;
    changed)
        # The development loop: staged, unstaged and untracked. Not a
        # substitute for scope=all at a handover, a milestone review or
        # in CI — it cannot see a file committed earlier that a config
        # change made here has broken.
        #
        # --diff-filter=d drops deletions: a removed path must not be
        # handed to a hook. `git diff` never reports untracked files,
        # hence the second enumeration.
        mapfile -d '' files < <( {
            git diff --name-only --diff-filter=d -z HEAD
            git ls-files --others --exclude-standard -z
        } | sort -zu )
        empty="Nothing changed since HEAD. Run \`just check\` for the whole tree."
        ;;
    *)
        echo "Unknown scope '{{ scope }}'. Use: all | changed" >&2
        exit 2
        ;;
    esac
    if [ "${#files[@]}" -eq 0 ]; then
        echo "$empty"
        exit 0
    fi
    printf '%s\0' "${files[@]}" | xargs -0 "{{ pre_commit }}" run --files

# Is the implementation right?
test:
    @echo "No shipped behaviour to test yet."
    @echo
    @echo "This repository currently holds specifications, plans, decision"
    @echo "logs and this local harness. None of it has runtime behaviour of"
    @echo "its own, and third-party tools are not retested here. Test suites"
    @echo "arrive in the steps that land the code they cover."

# The whole-tree `check`, then `test`.
verify: check test

[private]
_require-tooling:
    #!/usr/bin/env bash
    if [ ! -x "{{ pre_commit }}" ]; then
        echo "Tooling missing. Run: just setup" >&2
        exit 1
    fi
