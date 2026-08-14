# project-zomboid track — implementation plan

Owns the Project Zomboid (Build 42) dedicated-server image. Its
specification is `project-zomboid/SPECIFICATIONS.md` (§N below);
root §5 binds in full, root §3 and §5 are standing reading (rule 3).
Step entry shape, status values and cost taxonomy: `CLAUDE.md` (Plan
conventions). CI coverage and publication are root-track work
(`PLAN.md` steps 005 and 007–010).

**Open facts** (§2 items a–o) are assigned to the step that first needs
each; every resolution follows rule 1's channel — pre-committed paths
are autonomous amendments, anything touching a requirement, tier,
operator surface, documented limitation or the decision to ship comes
back to the operator first (unfavorable (d), (e), (f), (g), (k), (l)
always do).

## Milestone PZ1 — Image and facts

### step-pz-001 — Build definition

- **Objective:** the game is baked into a runnable image; the facts a
  build can settle are settled.
- **Spec sections:** §1 (scope, B42 stable branch), §2 (app id 380870,
  anonymous, JRE shipped); root §3.1, §3.2, §2.7, §5.8, §2.3.
- **Dependencies:** `step-sc-001` (builder image). Cross-track.
- **Deliverables:**
  - `project-zomboid/Dockerfile`: builder stage from the locally built
    builder — referenced by a pinned tag or digest, never a moving
    pointer (root §3.1; during local development the pin is the local
    build's digest, recorded; the published pin discipline arrives
    with root step-007) — installing app id 380870 from the declared
    stable branch with validation; final stage from `trixie-slim`
    copying the game in, adding only runtime dependencies including
    the Steam client libraries the game loads (root §2.7; §2's
    steamclient-resolution question gets its first evidence here,
    settled fully in step-pz-002). Shipped content world-readable
    (0644/0755, root §3.4). steamcmd never in the final image.
  - Buildid and version-string capture at build time (root §2.3),
    wired into the OCI labels of root §5.8: game version, revision,
    Steam buildid and branch, builder reference (version/revision
    values are build inputs; CI computes them at publish, local builds
    pass dev values).
  - `just` build recipe; Dockerfile lint green.
- **How the operator tests it:** run the documented build recipe;
  inspect labels; confirm the game directory and JRE are present in
  the image. Free but **slow**: the builder stage downloads
  multi-gigabyte game content from Steam — sequenced deliberately
  here, once, and Docker layer cache amortizes later steps. Cleanup:
  `docker rmi` by name; scoped build-cache prune only.
- **Status:** pending.

### step-pz-002 — Server bring-up and core fact verification

- **Objective:** the server runs by hand inside the container; the
  facts that shape the entrypoint design are verified against the
  shipped build, and the spec amendments land per rule 1.
- **Spec sections:** §2 (the facts block and open items **a, b, c, e,
  n, o**, the steamclient-resolution bullet, the credential-echo
  bullet, the SIGTERM fact, the non-interactive account-creation
  mechanism); root §2.9.
- **Dependencies:** step-pz-001.
- **Deliverables:**
  - A manual (temporary, documented) server invocation inside the
    container; the non-Steam profile preferred wherever it suffices,
    default-profile runs used deliberately where a fact is
    Steam-dependent (rule 9's profile rule — registration on the
    public browser is the accepted side effect).
  - Verified and recorded, with reproduction commands in
    `.claude/docs/pz-facts.md`: (a) query protocol on the main game
    port or not; (b) legacy `SteamPort1`/`SteamPort2` listeners on
    B42; (c) console `save`/`quit` over a non-TTY stdin pipe; (e)
    authoritative source of the human-readable version string; (n)
    default bind addresses of the player-facing UDP listeners; (o)
    `$HOME` override coverage vs JVM `user.home`; where
    `steamclient.so` is resolved from; whether startup output echoes
    credential values; that SIGTERM is not acted on natively; that the
    non-interactive admin-account creation path exists (if absent:
    fatal-not-hang is the pre-committed response, and the finding
    comes to the operator — it touches the ship decision).
  - Spec amendments + decision entries for each resolution per
    rule 1's split; unfavorable (e) (buildid-derived tags) or any
    requirement-touching outcome goes to the operator before
    amendment.
- **How the operator tests it:** re-run the reproduction commands in
  `.claude/docs/pz-facts.md` for any item and observe the recorded
  outcome. Free local (default-profile runs briefly register on the
  Steam browser; stopped immediately after; no cleanup persists).
- **Status:** pending.

**Milestone close:** compaction + state review (rule 3), keyed to this
track.

## Milestone PZ2 — Entrypoint: startup

### step-pz-003 — Entrypoint skeleton and startup validation

- **Objective:** the container refuses every unsafe start loudly and
  runs correctly under an arbitrary uid.
- **Spec sections:** §1 (fixed state root, `$HOME` inside it, fatal on
  missing/unwritable root); root §3.4 (uid-agnostic, uid-0 fatal,
  `ALLOW_UID0` parsing incl. the unparseable-value fatal), §3.5, §5.1.
- **Dependencies:** step-pz-002. Read `.claude/refs/image-contract.md`
  before this step (operator-interface design begins here).
- **Deliverables:**
  - Entrypoint language chosen (logged, rule 4) — its syntax+lint
    family joins the harness in this same step (rule 2), and `just
    test` gains its first real fixtures: entrypoint helpers testable
    outside a container.
  - Entrypoint behaviors: fatal as uid 0 naming `--user`/compose
    `user:`, honoring `ALLOW_UID0` (`1`/`true` skip, `0`/`false`
    explicit off, anything else a fatal naming variable and value,
    parsed unconditionally); fixed documented absolute state-root path
    via the game's cache-dir option; missing/unwritable state root a
    loud fatal before the game starts; `$HOME` set unconditionally to
    a documented location inside the state root, overriding any
    operator value.
  - Adoption of the `code-reviewer` template (first code exists) and,
    with the first test fixtures, `test-reviewer` — after which no
    template remains and the assets directory, `CLAUDE.md`'s template
    block and rule 1's carve-out are deleted in one commit (rule 3).
- **How the operator tests it:** documented `docker run` matrix — as
  uid 0 (fatal), with `ALLOW_UID0=true` (proceeds), garbage value
  (fatal naming it), arbitrary uid without mount (fatal), with mount
  (proceeds to the not-yet-implemented next stage or starts the game
  with pz-002's manual invocation); `just test` green. Free local.
- **Status:** pending.

### step-pz-004 — Configuration overrides

- **Objective:** every environment override is effective from the very
  first start on a fresh state root; every unusable value is a fatal.
- **Spec sections:** §3 (environment surface table, first-start
  effectiveness, INI persistence consequence); root §5.3 (overrides,
  validation rule, no invented variables, rewrite caveat), §5.4
  (redaction if pz-002 found credential echo; INI persistence of
  env-applied credentials documented), §5.2 (port variables reach the
  game's advertised-port settings).
- **Dependencies:** step-pz-003.
- **Deliverables:** the §3 variable set applied to the effective
  configuration at startup (mechanism per pz-002's findings: launch
  arguments, pre-written INI, or both) — `SERVER_NAME`,
  `SERVER_PASSWORD`, `RCON_PASSWORD`/`RCON_PORT`, `GAME_PORT`,
  `DIRECT_PORT` (admin credentials are pz-006's); unset variables
  leave file values standing; unparseable/unappliable values are
  fatal naming variable and value; stdout redaction interposed if
  needed; docs-facing caveats (override-wins, INI persistence)
  recorded for pz-012.
- **How the operator tests it:** fresh state root, set ports +
  `SERVER_NAME`, first start: game's effective INI/args show the
  values before/at first run; restart with a variable unset: file
  value stands; set a garbage port: fatal naming it. Free local
  (non-Steam profile suffices).
- **Status:** pending.

### step-pz-005 — Heap guard

- **Objective:** the most silent failure in the spec (kernel OOM kill
  mid-write) is preempted loudly.
- **Spec sections:** §3 (`MAX_HEAP`, cgroup reading, deterministic
  non-heap allowance, v1/v2 "no limit" readings); §2 (heap-below-limit
  fact).
- **Dependencies:** step-pz-003 (can run parallel to pz-004 in
  content, but steps are serial by rule 2).
- **Deliverables:** `MAX_HEAP` applied to the launch configuration
  (documented default); cgroup memory limit read (v2 `max` and v1
  near-maximum both read as "no limit", never a parse error); fatal
  before game start when effective heap + documented allowance
  (default: larger of 512 MB or 25% of heap) exceeds the limit; when
  no limit is readable the game starts and the documented assumption
  stands.
- **How the operator tests it:** run with `--memory` below
  heap+allowance: fatal naming the numbers; with adequate limit:
  starts; with no limit: starts. `just test` covers the allowance
  arithmetic. Free local.
- **Status:** pending.

**Milestone close:** compaction + state review.

## Milestone PZ3 — Lifecycle

### step-pz-006 — First boot and admin credentials

- **Objective:** a fresh state root never hangs and never yields an
  adminless public server; §4's table implemented exactly.
- **Spec sections:** §4 (both pre-table rules and all five rows), §2
  (open item **d**), §3 (`ADMIN_USERNAME`, `INITIAL_ADMIN_PASSWORD`,
  `ADMIN_PASSWORD`); root §5.4 (two-variable pattern, fatal on
  missing mandatory secret, no defaults).
- **Dependencies:** step-pz-004.
- **Deliverables:** item (d) settled (non-interactive password change
  — decides whether `ADMIN_PASSWORD` is offered; unfavorable → to the
  operator, it drops a documented variable); the observable
  admin-account predicate (SQLite query against the per-`SERVER_NAME`
  database; missing database short-circuits to "absent"; a pinned
  static SQLite client joins the image only if the entrypoint needs
  one — §4, root §5.5's tooling class, pin recorded per rule 2); the
  §4 decision table implemented, including fatal-before-rows on an
  unsupported `ADMIN_PASSWORD` and fatal when no account exists and
  neither variable is set.
- **How the operator tests it:** documented matrix over fresh and
  populated state roots × credential combinations, matching §4's
  table row by row; interrupted-first-boot case (kill during first
  boot, restart) re-creates instead of misreading. Free local,
  non-Steam profile.
- **Status:** pending.

### step-pz-007 — Shutdown mediation

- **Objective:** the flagship guarantee: stop signal → save → clean
  exit, correct exit codes, on every deployment shape.
- **Spec sections:** §5 (channel, internal-RCON fallback and its four
  constraints, operator exec path, mid-load stop), §2 (items **c**
  consumed, **l**), §3 (`STOP_TIMEOUT`); root §5.6 (entire section:
  signal chain, reaping/tini decision, bounded wait, exit-code table,
  timeout printed at start and on signal), §2.4.
- **Dependencies:** step-pz-006.
- **Deliverables:** signal delivery guaranteed (exec/PID 1 or
  init+relay — mechanism logged); stop translated to `save`+`quit`
  over the channel pz-002/item (l) selects: console pipe if usable,
  else entrypoint-managed internal RCON (loopback-only bind — item
  (l) unfavorable with console also unusable **blocks shipping** and
  goes to the operator; reuse of operator RCON incl. INI-configured;
  generated ephemeral password, never mistaken for operator config);
  `STOP_TIMEOUT` bounded wait (default 80 s), stated at start and on
  signal; the root §5.6 exit-code table implemented verbatim,
  mid-load stops landing on the timeout row; the documented
  `docker exec` save/announce path working regardless of
  `RCON_PASSWORD`.
- **How the operator tests it:** `docker stop --time 120` on a running
  server → save observed, exit 0; `STOP_TIMEOUT` above grace period →
  exit 137 demonstration of the documented pairing rule; kill the
  game process → non-zero propagated; `docker exec` save and announce
  with and without `RCON_PASSWORD`. Free local, non-Steam profile
  (one default-profile stop exercised too — Steam-dependent behavior).
- **Status:** pending.

### step-pz-008 — Healthcheck and observability clients

- **Objective:** a hung server is unhealthy, a loading server is not
  healthy-early, a non-Steam server is not condemned; operators can
  probe from the host.
- **Spec sections:** §6 (entire), §2 (items **a** consumed, **f**,
  **i**, **k**), §3 (probe targets effective ports); root §5.5
  (entire: stdout policy already held, HEALTHCHECK predicates,
  start_period reasoning, the two must-capabilities, the two static
  clients).
- **Dependencies:** step-pz-007 (the fallback probe channel is the
  mediation channel).
- **Deliverables:** items (f), (i), (k) settled per their pre-committed
  paths (unfavorable (f)/(k)/(l)-interactions go to the operator —
  they add a variable or ship a documented-degraded profile); both
  pinned static clients shipped (query client drives the HEALTHCHECK;
  RCON client for operators — pins recorded, which per rule 2 is the
  whole coverage obligation for third-party binaries); HEALTHCHECK
  against effective configuration, predicates per root §5.5 (no
  early-healthy, goes-false-on-hang, documented start_period sized
  with the stated trade-off); non-Steam profile auto-detected and
  switched to the fallback order; player-count and serving-state
  probe documented for both profiles.
- **How the operator tests it:** start; observe `starting` →
  `healthy` only after the world serves; hang the process (SIGSTOP)
  → `unhealthy`; non-Steam profile → same lifecycle via fallback;
  documented host-side probe returns serving+player count. Free
  local; one default-profile run for the Steam-query path.
- **Status:** pending.

**Milestone close:** compaction + state review.

## Milestone PZ4 — Content, hardening, release readiness

### step-pz-009 — Workshop mods

- **Objective:** native mod support works within the image's promises;
  the operator can see mod-failure data loss coming.
- **Spec sections:** §7 (entire), §2 (items **g**, **h**); root §3.4
  (nothing writes into the shipped game directory — never bends).
- **Dependencies:** step-pz-008.
- **Deliverables:** items (g), (h) settled (g's fixed response: mod
  target brought inside the state root by config, relocation or
  build-time link; a narrowed read-only claim is the last resort and
  goes to the operator); a mod-configured server verified end to end;
  documentation content for pz-012: first-start-after-adding-mods
  cost, Steam connectivity need, failure behavior and how the
  operator notices.
- **How the operator tests it:** configure a small workshop mod; first
  start downloads into the state root; restart is fast; simulate a
  failed download (no connectivity) and observe the recorded behavior.
  Free local but needs Steam connectivity for the download; cleanup:
  delete the test state root.
- **Status:** pending.

### step-pz-010 — Hardening verification and local smoke script

- **Objective:** the image's promises (uid-agnostic, read-only rootfs,
  complete writable set) hold under test, and one script asserts the
  publish-gate behavior locally.
- **Spec sections:** §1 (writable set: state root + `/tmp`, nothing
  else, verified); root §3.4, §5.1, §8 (the smoke gate's content,
  exercised locally — the CI wrapper is root step-005).
- **Dependencies:** step-pz-009.
- **Deliverables:** verification that nothing outside state root and
  `/tmp` needs write access (fix or escalate anything found); a smoke
  script under the harness (`just` recipe): default profile, only
  documented mandatory variables, arbitrary non-root uid, `--read-only`
  with writable mounts exactly at documented paths, healthy within a
  stated bound (else fail, never hang), stop signal, exit 0; the
  supported non-Steam profile exercised on its own healthcheck path
  (root §8 "should").
- **How the operator tests it:** run the smoke recipe twice (default
  and non-Steam profile) — green; deliberately break a mount and see
  it fail loudly. Free local; the default-profile run registers
  briefly on the Steam browser (accepted, rule 9). Cleanup: script
  removes its own containers/state.
- **Status:** pending.

### step-pz-011 — Logs and backup knowledge

- **Objective:** the disk-filling and restore-day failures are owned
  as documentation backed by verified facts.
- **Spec sections:** §8 (entire), §2 (items **j**, **m**; native
  backup feature verification); root §5.7 (entire), §5.5 (rotation
  ownership).
- **Dependencies:** step-pz-010.
- **Deliverables:** items (j), (m) settled ((m) inconclusive → the
  pre-committed "unknown — assume irreversible" documentation); native
  backup settings verified (defaults, cap/frequency controls, archive
  location); RCON `save` completion-confirmability verified — not
  confirmable → stop/copy/start documented as the safe procedure;
  backup-recipe and version-upgrade-warning content finalized for
  pz-012, including log-rotation ownership.
- **How the operator tests it:** re-run the documented verification
  commands (trigger a native backup, inspect archives; inspect log
  growth/rotation); review the drafted documentation content. Free
  local.
- **Status:** pending.

### step-pz-012 — Per-image README

- **Objective:** the complete operator-facing contract in one
  document — the root §9 per-image list with nothing missing.
- **Spec sections:** root §9 (per-image README list in full: env
  table with mandatory/optional flags, port table with
  advertised-or-remappable flags and the internal listener, writable
  paths + state root + mount-ownership preparation step,
  configuration rewrite and override caveats, shutdown semantics with
  grace period and stop timeout and pairing rule, healthcheck and
  probe/save/announce how-to, backup section with upgrade warning,
  tag policy, minimal `docker run` and compose examples), §1
  (platform-neutral); consolidates documentation content from every
  prior pz step (§1–§8 as documented facts).
- **Dependencies:** step-pz-011.
- **Deliverables:** `project-zomboid/README.md` (also the GHCR page).
  Placeholders only for values that exist at first publish (owner
  namespace) — flagged for root step-008 to resolve.
- **How the operator tests it:** follow the quickstart examples
  verbatim against the locally built image — they must work as
  written; `just check` (prose lint) green. Free local.
- **Status:** pending.

**Milestone close:** compaction + state review. The track then waits on
root steps 005 and 008 for CI coverage and publication.

## Specification coverage (project-zomboid document)

| Section | Where |
|---|---|
| §1 Scope (B42, state root, `$HOME`, writable set) | pz-001 (branch), pz-003 (state root/HOME), pz-010 (writable-set verification); **Build 41 excluded** — declared non-goal, blast radius stated in §1 |
| §2 Facts | pz-001 (install facts), pz-002 (core verification); open items: a,b,c,e,n,o → pz-002; d → pz-006; l → pz-007; f,i,k → pz-008; g,h → pz-009; j,m → pz-011 |
| §3 Environment surface | pz-004 (general), pz-005 (`MAX_HEAP`), pz-006 (admin credentials), pz-007 (`STOP_TIMEOUT`), pz-003 (`ALLOW_UID0`); table finalized in pz-012 |
| §4 First boot | pz-006 |
| §5 Shutdown | pz-007 |
| §6 Health | pz-008 |
| §7 Workshop mods | pz-009 |
| §8 Backup recipe | pz-011 (facts), pz-012 (published documentation) |
