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

# Is what is committed here well-formed? Covers the whole working tree,
# untracked files included, gitignored paths excluded. `.claude/spec-work/`
# is excluded by .pre-commit-config.yaml, keyed on path.
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
