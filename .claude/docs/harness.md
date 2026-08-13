# The check/test/verify harness

Read this before adding a language, an artifact type, or a check family —
rule 2 requires a family for **everything the repository ships**, and a new
file type with no family is a silent hole.

## Entry points

| Command | What it does |
|---|---|
| `make setup` | installs every pinned dependency and sets `core.hooksPath` |
| `make check` | the working tree is well-formed (`ONLY=family,family` narrows it) |
| `make test` | harness behavior against fixtures (must-fail, must-warn) |
| `make verify` | check + test — the pre-handover gate |

`tools/check.sh --list` prints the families. A narrowed run is fine mid-step;
the commit that receives a step tag runs the full one.

## Layout

- `Makefile` — the four entry points, nothing else.
- `tools/lib.sh` — shared helpers. `harness_files` is the file-discovery
  contract: tracked **and** untracked files, gitignored paths dropped by git,
  `HARNESS_EXCLUDES` dropped by path (`.claude/spec-work/`, `.claude/refs/`,
  `tools/tests/fixtures/`).
- `tools/check.sh` — one `fam_<name>` function per family, plus the driver.
- `tools/test.sh` — snapshot-based behavior tests: each case copies the tree
  into a throwaway git repository, plants one fixture, and asserts how
  `tools/check.sh` reacts.
- `tools/lint_governance.py` — most of the governance family (settings,
  skills, agents, memory pointers, CLAUDE.md's line budget). Exit codes:
  0 clean, 1 error, 2 warnings only — the driver maps 2 to a non-fatal
  `WARN`. The family also parses the `Makefile` itself (`make --dry-run
  help`), the one artifact whose breakage takes every entry point with it.
- `tools/requirements.txt`, `tools/tool-versions.sh` — the pins. Python tools
  by exact version; downloaded binaries by version *and* sha256.

## Adding a family

1. Write `fam_<name>` in `tools/check.sh` (exit 0 pass, 2 warn, else fail)
   and add `<name>` to `FAMILIES`.
2. Add a fixture under `tools/tests/fixtures/<name>/` that the family must
   reject, and a case in `tools/test.sh`. A family with no failing fixture
   has never been shown to detect anything.
3. Pin any new tool in `tools/requirements.txt` or `tools/tool-versions.sh`
   (with its sha256) and install it from `tools/setup.sh`.

Configuration lives at the root, one file per tool: `.pymarkdown.json`,
`.yamllint.yml`, `.hadolint.yaml`, `ruff.toml`. Excluding a document from a
rule is a logged decision, not a quiet config edit.

## Notes that cost time to rediscover

- The pre-commit hook runs the **whole-tree** check, not the staged subset:
  a dirty tree fails the commit even when the staged part is clean.
- The toolchain is pinned for linux/x86_64 only (the images are
  linux/amd64 too); `make setup` fails loudly elsewhere.
- `make setup` is idempotent — it re-installs only when a pin moves
  (`.tools/.stamp`); `SETUP_ARGS=--force` rebuilds from nothing.
- The governance family reads `CLAUDE.md`'s "Current state" pointer and every
  plan's `**Status**:` lines. Keep both formats stable: a pointer it cannot
  parse is an error, by design.
