# shellcheck shell=bash
# shellcheck disable=SC2034  # consumed by the scripts that source this file
# Pinned harness binaries (CLAUDE.md rule 9: nothing unpinned is fetched).
# Bump = edit here, re-run `make setup`, log the reason if it changes behavior.
# Checksums are of the release assets as published for linux/x86_64.

SHELLCHECK_VERSION="v0.11.0"
SHELLCHECK_SHA256="8c3be12b05d5c177a04c29e3c78ce89ac86f1595681cab149b65b97c4e227198"

HADOLINT_VERSION="v2.15.1"
HADOLINT_SHA256="c7187db94eeeeca956519a6af171adc31453941a1e777961f6e680f697c8c507"
