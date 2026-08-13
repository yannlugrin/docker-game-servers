# project-zomboid track — implementation plan

Track: Project Zomboid dedicated server image (Build 42). Step prefix:
`step-pz-NNN`. Specification: `project-zomboid/SPECIFICATIONS.md` (PZ
§N below), under root §5 in full; root §3 and §5 are standing reading.
Plan conventions: root `PLAN.md` header.

## Milestone PZ1 — Facts

### step-pz-001 — Server exploration and fact verification

- **Objective**: settle the PZ §2 facts that gate every design step,
  against the build actually shipped — before the Dockerfile, entrypoint
  or healthcheck is designed.
- **Spec sections**: PZ §2 (all facts and open items except (h) →
  step-pz-006 and (m) → step-pz-008), PZ §1 (state-root relocation via
  cache-dir), root §2.7, §2.9.
- **Deliverables**: for each item, the verified answer recorded through
  rule 1's channel — plain fact recordings autonomously (one commit
  each: decision entry + spec amendment); **items (d), (e), (g), (k),
  (l) and anything changing a requirement, tier, documented limitation
  or ship decision come back to the operator first**. Covers: query
  protocol on the game port (a); legacy Steam ports (b); console over a
  non-TTY stdin pipe (c); non-interactive admin password change (d);
  authoritative version-string source (e); non-Steam detection (f);
  workshop mod location (g); status/player query over the mediation
  channel (i); log rotation ownership (j); A2S tracking of serving state
  both ends (k); RCON bind-address setting (l); UDP bind addresses (n);
  `$HOME` vs JVM `user.home` (o); plus the unlabeled facts: B42 stable
  branch confirmation, `steamclient.so` resolution, SIGTERM inaction,
  credential echo in console output, stdout+logfile behavior, native
  backup settings. Working notes land in `.claude/docs/pz-facts.md`.
- **Dependencies**: needs `step-sc-001` done (the builder installs the
  server — its first real exercise).
- **How to test**: free (rule 9 carve-out) but slow — the install
  downloads several gigabytes from Steam. I hand over the exact
  run/probe commands per item so any answer can be reproduced. Cleanup:
  `docker rmi` / `docker volume rm` by name.
- **Status**: pending.

## Milestone PZ2 — Image

### step-pz-002 — Dockerfile

- **Objective**: the PZ image builds: game baked in, runtime-lean,
  uid-agnostic, honestly labeled.
- **Spec sections**: PZ §1 (fixed state root, writable-path set), PZ §2
  (JRE shipped, app id/branch), root §3.1–§3.4 (multi-stage, pinned
  builder reference, baked game, uid-agnostic file modes), §2.7
  (`steamclient.so` per step-pz-001's finding), §5.8 (labels: source,
  description, license, game version, revision, Steam buildid + branch,
  builder reference), §7 (version-string → tag naming per item (e)'s
  resolution).
- **Deliverables**: `project-zomboid/Dockerfile` (builder stage pinned
  by tag/digest; final stage from `trixie-slim` + runtime deps only;
  world-readable modes: 0644/0755; no default user; state root at the
  fixed documented path; steamcmd absent); version/buildid extraction
  feeding tags and labels; tests in the harness (label assertions, file
  modes, no steamcmd, image builds).
- **Dependencies**: needs `step-sc-001` done and `step-pz-001` done
  (items (e), (g), `steamclient.so`).
- **How to test**: local `docker build` (multi-gigabyte download —
  free, slow); `docker inspect` shows the §5.8 labels; a filesystem
  spot-check confirms modes and absence of steamcmd. Cleanup: `docker
  rmi` by name (keep the image if proceeding straight to pz-003).
- **Status**: pending.

### step-pz-003 — Entrypoint: validation, configuration, first boot

- **Objective**: the adapter of root §3.5 up to a running server:
  startup validation, environment overrides, first-boot handling.
- **Spec sections**: PZ §3 (environment surface, heap guard, INI
  persistence caveat), PZ §4 (first-boot decision table, admin-account
  predicate), root §3.4 (uid-0 fatal, `ALLOW_UID0` parsing), §3.5,
  §5.3 (overrides effective on very first start; fatal on unparseable
  values; env surface stays small), §5.4 (missing mandatory secret
  fatal; `INITIAL_*`/override pattern; redaction per step-pz-001's echo
  finding), §5.1 ($HOME set inside state root).
- **Deliverables**: the entrypoint (language chosen here — its check
  family joins the harness per rule 2): uid-0 refusal with `ALLOW_UID0`
  opt-out parsed unconditionally; state-root writability fatal; heap
  guard against the cgroup limit (v1/v2, non-numeric = no limit) with
  the documented deterministic allowance; every §3 variable applied on
  first start before the game authors its INI; the §4 table exactly,
  keyed on the SQLite admin-account predicate (missing DB = absent
  shortcut; the SQLite client joins the image tooling if needed —
  pinned, checked per rule 2); `ADMIN_PASSWORD` offered/fatal per item
  (d)'s resolution. Tests: every table row, every fatal, the
  first-start override effectiveness (fresh volume → INI carries the
  override before first game write).
- **Dependencies**: needs `step-pz-002` done. Reads
  `.claude/refs/image-contract.md` (rule 3 trigger: operator-interface
  design; information only).
- **How to test**: free local runs. I hand over one command per §4 table
  row and per fatal (wrong uid-0 value, unwritable state root, oversized
  heap, missing credentials on fresh volume), each with its expected
  message/exit. Cleanup: named volumes, `docker volume rm`.
- **Status**: pending.

### step-pz-004 — Shutdown mediation

- **Objective**: the flagship guarantee: stop signal → `save` + `quit` →
  confirmed clean exit 0, on every configuration.
- **Spec sections**: PZ §5 (channel selection per items (c)/(l);
  internal-RCON constraints: reuse operator RCON from env **or INI**,
  loopback-only, high-entropy ephemeral password, generated-password
  rotation/scrub, port-table entry; operator exec path regardless of
  `RCON_PASSWORD`), root §5.6 in full (PID 1/signal delivery, reaping,
  `STOP_TIMEOUT` below grace period, timeout printed at start and on
  signal, exit-code table, stop during world load = timeout row), §2.4.
- **Deliverables**: mediation in the entrypoint; the documented
  `docker exec` save/announce path; exit-code behavior per root §5.6's
  table verbatim. Tests: each table row (clean stop, crash during
  shutdown, timeout expiry, self-exit propagation, validation failure),
  with and without operator RCON, INI-configured RCON reuse, stop during
  load.
- **Dependencies**: needs `step-pz-003` done.
- **How to test**: free local runs: `docker stop` (generous
  `--time`) → exit 0 and save confirmed in logs; `docker stop --time 5`
  under a longer `STOP_TIMEOUT` → the attributable non-zero path;
  `docker exec` save works with no `RCON_PASSWORD` set. Cleanup: named
  volumes.
- **Status**: pending.

### step-pz-005 — Healthcheck and operator probes

- **Objective**: honest liveness on every supported profile, and the
  operator's "is it serving, how many players" from the host.
- **Spec sections**: PZ §6 (probe target per item (a); fallback order;
  non-Steam detection per item (f); degraded-profile documentation per
  items (k)/(l); `start_period` sizing and its documented trade-off),
  root §5.5 in full (protocol probe, no early-positive, no latch, the
  two must capabilities, the two shipped clients — size measured), §2.5.
- **Deliverables**: HEALTHCHECK against the **effective** port; the
  pinned static query and RCON clients shipped and covered by the
  harness; documented host-side probe; non-Steam profile switching to
  the fallback automatically. Tests: healthy only after world load
  (no early positive); unhealthy on a hung/stopped responder as far as
  item (k)'s resolution allows; probe follows a remapped `GAME_PORT`;
  non-Steam profile probes via fallback.
- **Dependencies**: needs `step-pz-003` done (effective configuration),
  `step-pz-004` done where the fallback rides the internal RCON.
- **How to test**: free local runs: `docker inspect` health transitions
  on a normal start, a remapped port, and a non-Steam configuration.
  Cleanup: named volumes.
- **Status**: pending.

### step-pz-006 — Workshop mods

- **Objective**: native workshop-mod support verified honest: mods land
  inside the state root, failure behavior known and documented.
- **Spec sections**: PZ §7 (mod target inside the state root — item (g)
  already resolved in step-pz-001, enforced here; item (h): download-
  failure behavior, verified here; slow first start and Steam
  connectivity documented), root §3.4 (nothing writes into the shipped
  game directory), §5.1.
- **Deliverables**: whatever item (g)'s resolution requires (game
  option, relocation, or build-time link); item (h) settled through
  rule 1's channel; read-only-rootfs claim re-verified with mods active;
  documentation notes feeding step-pz-008.
- **Dependencies**: needs `step-pz-003` done; needs step-pz-001's item
  (g) resolution.
- **How to test**: free local run with a small public workshop mod
  configured: mod downloads into the state root, server starts, rootfs
  stays read-only; a deliberately invalid mod id demonstrates the
  documented failure behavior. Cleanup: named volumes.
- **Status**: pending.

### step-pz-007 — Smoke suite (the CI gate, runnable locally)

- **Objective**: root §8's publish gate as a local, repeatable suite —
  the same script CI will run.
- **Spec sections**: root §8 (smoke test: default profile, mandatory
  vars only, healthy within a stated bound else fail, stop, exit 0;
  arbitrary non-root uid; rootfs as read-only as documented, writable
  mounts exactly at the documented paths; alternative profile exercised
  where it switches the healthcheck code path), PZ §1 (writable set:
  state root + `/tmp`), PZ §6 (non-Steam profile).
- **Deliverables**: the smoke script under the harness's *test* entry
  point, exit-code-honest, bounded (fails rather than hangs), covering
  the default profile and the non-Steam profile.
- **Dependencies**: needs `step-pz-005` done (and transitively
  pz-002..004).
- **How to test**: run the documented test command twice (repeatability)
  — free, slow on first image build only. Cleanup: the script cleans its
  own containers/volumes by name.
- **Status**: pending.

## Milestone PZ3 — Delivery

### step-pz-008 — Per-image README

- **Objective**: the consumer documentation root §9 requires, PZ §8's
  backup recipe included — the GHCR page.
- **Spec sections**: root §9 (per-image README, every listed element:
  env table with flags, port table with advertised/remappable and the
  internal listener, writable paths + **mount-ownership preparation**,
  rewrite and override caveats, shutdown semantics + grace period +
  `STOP_TIMEOUT`, healthcheck + probe/save/announce, backup + upgrade
  warning, tag policy, `docker run` and compose examples), PZ §8 (native
  backup settings, archive caveats, hot-copy verdict per the RCON-save
  confirmation verification), PZ §2 item (m) (point-release world
  effect — researched here; inconclusive → "unknown, assume
  irreversible"), PZ §7 (mods documentation), §5.4 (crash-dump warning,
  INI credential persistence), §5.7, §1 (platform-neutral).
- **Deliverables**: `project-zomboid/README.md`; item (m) settled
  through rule 1's channel; compose example validated by the harness.
- **Dependencies**: needs `step-pz-007` done (documents verified
  behavior, not intent).
- **How to test**: read it; docs lint green; run the README's own
  `docker run` and compose examples as written — they must work
  verbatim. Free. Cleanup: named volumes.
- **Status**: pending.

## Coverage

PZ §1 → pz-002 (B41 non-goal excluded by specification); §2 → pz-001
(item (h) → pz-006, item (m) → pz-008); §3, §4 → pz-003; §5 → pz-004;
§6 → pz-005; §7 → pz-006 (+ pz-008 docs); §8 → pz-008.
