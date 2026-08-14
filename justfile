# Task runner for the local development loop.
#
# Prerequisites installed by hand, once, outside this repository:
# git, just, and python3 (>= 3.9) with its `venv` module. Everything
# else arrives through `just setup`.

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

# Is what is committed here well-formed? The whole working tree,
# untracked files included, gitignored paths excluded; `.claude/spec-work/`
# is excluded by .pre-commit-config.yaml, keyed on path. This is the gate:
# step handover, milestone review, CI. Use `check-changed` while working.
check:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -x "{{ pre_commit }}" ]; then
        echo "Tooling missing. Run: just setup" >&2
        exit 1
    fi
    # Read-only file enumeration: never `git add --intent-to-add`, which
    # would write index state and corrupt the clean-tree signal.
    git -C "{{ justfile_directory() }}" ls-files --cached --others --exclude-standard -z \
        | xargs -0 --no-run-if-empty "{{ pre_commit }}" run --files

# The development-loop form of `check`: only what differs from HEAD —
# staged, unstaged and untracked. Not a substitute for `just check` at a
# handover, a milestone review or in CI: it cannot see a file that was
# already committed and is broken by a config change made here.
check-changed:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -x "{{ pre_commit }}" ]; then
        echo "Tooling missing. Run: just setup" >&2
        exit 1
    fi
    # --diff-filter=d drops deletions: a removed path must not be handed
    # to a hook. Untracked files are added separately; `git diff` never
    # reports them.
    mapfile -d '' changed < <( {
        git -C "{{ justfile_directory() }}" diff --name-only --diff-filter=d -z HEAD
        git -C "{{ justfile_directory() }}" ls-files --others --exclude-standard -z
    } | sort -zu )
    if [ "${#changed[@]}" -eq 0 ]; then
        echo "Nothing changed since HEAD. Run \`just check\` for the whole tree."
        exit 0
    fi
    printf '%s\0' "${changed[@]}" | xargs -0 "{{ pre_commit }}" run --files

# Is the implementation right?
test:
    @echo "No shipped behaviour to test yet."
    @echo
    @echo "This repository currently holds specifications, plans, decision"
    @echo "logs and this local harness. None of it has runtime behaviour of"
    @echo "its own, and third-party tools are not retested here. Test suites"
    @echo "arrive in the steps that land the code they cover."

# Both of the above.
verify: check test
