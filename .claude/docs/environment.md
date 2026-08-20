# The development machine, as measured

Working memory, lazily loaded. Every figure here was **measured**, not
assumed, and carries the date it was taken on. Nothing here is a
requirement: the specifications are, and a fact below that has moved is a
fact to re-measure, never a requirement to reinterpret.

**When to read it:**

- **before assuming a tool is installed** — section 1 says what this machine
  had at bootstrap and what the setup command installs;
- **before a step whose test needs disk, bandwidth or a container runtime** —
  sections 2 and 3;
- **after a distribution or toolchain upgrade** — re-measure with the recipe
  in section 4 and update the figures with a new date.

Measurements of the *permission and hook* mechanisms are a different class of
fact and live in their own file, added at `step-002`.

---

## 1. Toolchain

Measured **2026-08-17** (`step-000`).

| Tool | State at bootstrap | Who provides it |
|---|---|---|
| `python3` | 3.14.4, with `venv` and `ensurepip` working | the distribution |
| `pip` | 25.1.1 (system), and a bundled pip inside each venv | the distribution |
| `just` | 1.45.0 | the operator, before `just setup` runs |
| `git` | 2.53.0 | the distribution |
| `gh` | 2.97.0, authenticated as `yannlugrin` over SSH | the operator |
| `docker` | client and server 29.6.2, `overlayfs`, root `/var/lib/docker` | the distribution |
| `bash` | 5.3.9 | the distribution |
| `pre-commit` | **absent** | `just setup`, pinned in `requirements.txt` |
| every linter | **absent** — no `shellcheck`, `hadolint`, `yamllint`, `markdownlint`, `vale`, `codespell` | `pre-commit`, pinned by revision in `.pre-commit-config.yaml` |
| `node`, `npm` | **absent** (an `nvm` shell function exists but loads nothing) | nothing yet — a hook needing node makes `pre-commit` fetch its own |
| `uv`, `pipx` | **absent** | nothing — the venv bootstrap does not need them |

Three consequences the harness rests on:

- **Python 3.13 is a floor, not a preference.**
  `.claude/hooks/bash_guard.py` calls `PurePath.full_match`, added in 3.13,
  and declares that requirement nowhere. Measured the hard way: the first CI
  run died on `ubuntu-24.04`'s Python 3.12.3, while `just check` passed on
  the same runner, because only the guard needs it (`DECISIONS.md` D-014).
  `.github/workflows/ci.yml` therefore installs **3.14**, matching the row
  above — so **re-measuring `python3` here means checking that pin too**,
  exactly as for `just`.
- **`just` is a prerequisite, not a pinned dependency.** It is the runner
  that invokes the setup command, so it cannot be installed by it. Everything
  downstream of it *is* pinned. **On CI it has no operator to provide it**, so
  `.github/workflows/ci.yml` pins the version *and* its published SHA-256 and
  fetches it from the just project's release (`DECISIONS.md` D-015). That
  pin's version is the one in the table above: **re-measuring `just` here
  means updating the workflow's `JUST_VERSION` and `JUST_SHA256` too**, or CI
  and this machine run different `just` versions — which matters, because
  `just --fmt` is an unstable feature the check family invokes.
- **`bash` 5.3 is available**, which is what lets `just check` read a
  NUL-delimited file list with `mapfile -d ''`. A machine with bash older
  than 4.4 would need a different reader.

## 2. Capacity

Measured **2026-08-17** (`step-000`).

- **Disk:** 948 GB free of 1007 GB on `/`. Ample for the multi-gigabyte
  Project Zomboid download `step-pz-001` needs — this is the measurement
  `PLAN.md`'s prerequisite table refers to.
- **CPU:** 20 logical cores. **Memory:** 15 GiB total, ~9.7 GiB available.
- **OS:** Ubuntu 26.04 LTS on kernel 6.18.33.2-microsoft-standard-WSL2 —
  **this is WSL2**, not a bare Linux host. Anything that depends on the host
  being a real machine (systemd units, host networking behaviour, the docker
  daemon's own lifecycle) is measured here rather than assumed.
- **Network:** reachable — PyPI and GitHub both fetched during `step-000`.

Measured **2026-08-18** (`step-005`), from a fresh `--no-hardlinks` clone with
`XDG_CACHE_HOME` pointed at an empty directory, so pip's, virtualenv's, Go's
and pre-commit's caches were all cold:

- **A cold `just setup` takes ~37 s**, and `just verify` after it ~2 s.
- **It leaves ~474 MB in `~/.cache/pre-commit`**, of which ~317 MB is the Go
  toolchain pre-commit fetches to build `actionlint` (there is no system `go`
  here), plus ~130 MB of Go build cache outside that path.

Re-measure with section 4's recipe when the hook set changes. **These two
figures are why `.github/workflows/ci.yml` caches nothing**: 474 MB through
GitHub's cache service to save 37 s is at best break-even, so every CI run
builds the toolchain cold (`DECISIONS.md` D-014). A future run whose setup
times argue otherwise is what would reopen it. **Isolate `XDG_CACHE_HOME`,
not just `PRE_COMMIT_HOME`** — a first attempt did the latter and came out
14 s too fast.

## 3. Docker on this host carries other work

Measured **2026-08-17** (`step-000`). At bootstrap the daemon already held
**9 images (4.5 GB), 1 running container, 4 volumes and 7.5 GB of build
cache**, none of it this project's.

This is the measured ground under rule 9's split between removing this
project's own artifacts by name — free — and an unscoped sweep. On this
machine `docker system prune` or `docker volume prune` would destroy another
project's running work, and the daemon is shared with Docker Desktop (a
second context, `desktop-linux`, exists alongside the default socket).

## 4. Re-measure recipe

Re-run after a distribution upgrade, a Docker upgrade, or whenever a figure
above is about to be relied on and looks old. Update the figures **and their
date**; a stale measurement presented as current is worse than none.

```sh
# Section 1 — toolchain
for t in python3 pip just git gh docker bash pre-commit shellcheck \
         hadolint yamllint markdownlint vale codespell node npm uv pipx; do
    printf '%-14s ' "$t"
    command -v "$t" >/dev/null 2>&1 && "$t" --version 2>&1 | head -1 || echo ABSENT
done
python3 -c 'import venv, ensurepip; print("venv+ensurepip OK")'

# Section 2 — capacity
df -h / | tail -1; nproc; free -h | head -2; uname -r
. /etc/os-release && echo "$PRETTY_NAME"

# Section 3 — what else lives on this daemon
docker system df; docker context ls

# Section 2 — a cold toolchain build, from a clone and an empty cache root
tmp=$(mktemp -d); git clone --no-hardlinks . "$tmp/fresh"
export XDG_CACHE_HOME="$tmp/cache"
( cd "$tmp/fresh" && time just setup && time just verify )
du -sh "$tmp"/cache/*; rm -rf "$tmp"
```
