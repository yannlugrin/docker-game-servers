# Implementation plan — `pz` track (Project Zomboid)

The `pz` track owns the Project Zomboid Build 42 dedicated-server image: its
Dockerfile, entrypoint, healthcheck, shipped tooling and README.
Repository-wide work — the harness, the builder image, CI, the repository
README and the contributor guide — is the root track's (`../PLAN.md`).

`§N` references point to `SPECIFICATIONS.md` in this directory; `root §N` to
the repository-root specification. **The root specification is never
"another track's document"** (rule 3): root §3 and §5 are standing reading
for every step here. The step-entry shape, the status vocabulary and the
compaction-on-approval rule live in `../.claude/docs/workflow.md` §1.

## How to read this plan

- Steps are ordered by dependency; the numbers are identifiers, frozen on
  entering `in progress`, never reused. **A step's dependency line, not its
  position, is what sequences it.**
- Exactly one step is in progress repository-wide, whichever track it
  belongs to.
- **Deliverables state what a step decides or builds beyond the
  specification, and cite the sections for the rest** — the session routine
  reads those sections anyway, and a copy of a read-only document can only
  go stale.
- **The first step pays a multi-gigabyte Steam download.** It is
  front-loaded because dependency forces it: almost every open fact this
  specification ordered settled at implementation can only be observed
  against a real, running Build 42 server. Everything after it is local
  iteration on an image that already exists.
- Each test states whether it crosses the rule-9 boundary, what it costs and
  how to clean up. Steam downloads, workshop-mod downloads, local builds,
  local container runs and the incidental Steam master-server registration a
  locally started server performs are all **free** per rule 9 — slow and
  bandwidth-heavy, not gated.
- **Observation steps use host-side inspection**, not in-container tooling:
  the runtime image carries the game, its runtime dependencies and root
  §5.5's small tooling and **nothing else**, so it has no `ps` and no `kill`.
  `docker top`, `docker inspect --format '{{.State.Pid}}'` with a host-side
  signal, and `docker pause`/`unpause` (a cgroup freeze — a truer hang than a
  stopped process anyway) are the instruments. Nothing is added to the image
  for a test's convenience.

---

## Milestone PZ-1 — The image exists, and its facts are settled

Six steps. The first builds the image; the next five settle §2's open facts
by observing the shipped build, because the specification ordered them
settled here and several decide what the entrypoint can be. Three can stop or
degrade the project, which is why they precede any entrypoint code resting on
them. Closing this milestone triggers the whole-state review and the
memory-compaction pass (rule 3) — both keyed on **this** track, named
explicitly at spawn, never on the already-advanced `Current state` pointer.

### step-pz-001 — The image skeleton, and the install facts — `pending`

- **Objective.** A Project Zomboid Build 42 server baked into an image by a
  multi-stage build, startable by hand — no entrypoint intelligence yet.
- **Spec sections implemented.** §1 (scope; Build 41 non-goal; the fixed
  state root pinned via the game's cache-dir option, independent of `$HOME`),
  §2 (the install facts), root §3.1, root §3.2, root §3.4 (world-readable
  shipped content, no default user), root §2.7.
- **Depends on.** `step-006` done (the builder image exists locally). The
  builder reference is a **locally built tag** here; it becomes a published
  digest at `step-pz-013`.
- **Deliverables.**
  - The multi-stage Dockerfile: builder stage installs the app id from the
    branch §2 declares, with validation; runtime stage from the base §3.1
    names, copying the game in with only its runtime dependencies,
    `steamclient.so` included. **steamcmd never appears in the game image**
    (root §3.1).
  - The state root: a **fixed, documented absolute path** set through the
    game's cache-dir option, and `$HOME` set by the image to a documented
    location **inside the state root**, unconditionally — an
    operator-provided `HOME` is overridden (§1). The path itself is this
    implementation's choice under §1 and becomes a documented fact operators
    mount against, so it is proposed with its reasoning rather than picked
    silently.
  - Recorded facts and measurements in `.claude/docs/pz-facts.md`, each with
    the build it was taken against, the method, and a re-observe recipe: the
    image and game sizes, the base-size evidence root §2.9 asked for, the
    installed layout, and §2's dated facts re-verified against the build
    actually shipped (branch and version string, that the server ships its
    own JRE, that all persistent state lives under one game-managed
    directory).
  - **Premise to verify, not assume:** that the base tag root §3.1 names
    resolves as written.
- **Open facts settled here.** §2's `steamclient.so` question (the `~/.steam`
  link farm versus the game's own shipped directories — root §2.7, root
  §2.9's per-game measurement item; the libraries ship either way); item
  **(e)** where the human-readable version string is authoritatively read
  from, which names the image tags (root §7); and §2's header duty to
  re-verify its dated facts against the shipped build — the four this step
  covers being the branch, the version string, the JRE, and the state layout.
- **How I test it.** Free and local, and **slow**: the build pulls the
  dedicated server from Steam — **multiple gigabytes**. Run the documented
  build recipe and read the reported image size; then start the container by
  hand with the state root mounted and watch the server start and reach the
  point where it wants an admin password — a hang, expected here, and the
  direct confirmation of §2's interactive-prompt fact. Cleanup: remove this
  project's own image, containers and test state directory **by name**
  (free); never a prune.
- **Status.** `pending`

### step-pz-002 — The mediation channel: viability, and the ship decision — `pending`

- **Objective.** Settle whether a safe stop-mediation channel exists and what
  it is. This step can stop the project, which is why it comes second.
- **Spec sections implemented.** §2 (the channel facts), §5 (which channel
  mediation uses), root §5.6, root §5.4 (the credential-echo question decides
  whether redaction is needed).
- **Depends on.** `step-pz-001`.
- **Deliverables.**
  - Observations recorded in `.claude/docs/pz-facts.md` with the build, the
    method and a re-observe recipe; the consequences amended into
    `SPECIFICATIONS.md` per rule 1 — decision entry and specification text in
    **one commit**, code excluded.
  - The **RCON client** of root §5.5 entering the tree **pinned**, with its
    version or digest recorded — for a third-party binary, which no linter
    can read, that pin and record is the whole coverage obligation (rule 2) —
    and its size measured (root §2.9).
- **Open facts settled here.**
  - **(c)** whether the server console accepts `save`/`quit` over a
    non-interactive stdin pipe (no TTY). Unfavourable → §5's internal-RCON
    fallback.
  - **(l)** whether the game's RCON offers a **bind-address setting** — the
    fallback requires loopback.
  - **(d)** whether the game supports a **non-interactive admin password
    change** on an existing account — it decides whether `ADMIN_PASSWORD`
    (§3) is offered at all.
  - **(i)** whether the channel answers a **status and player-count query
    non-destructively**.
  - §2's **non-interactive account-creation path**, the mechanism §4 rests
    on. Absent → the fallback is a fatal, never the hang.
  - §2's **credential echo**: whether the server writes password values into
    its startup output.
  - §2's **SIGTERM fact**, re-verified rather than inherited: with mediation
    absent, send a bare `SIGTERM` (host-side, to the container's main
    process) and observe that the server does **not** act on it. If Build 42
    has learned to handle it, every later mediation decision changes.
  - While the first admin account is created here anyway: **the admin-account
    table and the per-`SERVER_NAME` database naming**, which `step-pz-010`'s
    observable predicate needs and which nothing else is scheduled to
    discover.
- **Escalations — these come back to the operator before anything is
  amended, pre-committed or not.** **(l)** and **(c)** both unfavourable is
  the specification's **must-not-ship combination** (no safe channel for stop
  mediation, which every deployment needs; a wide ephemeral admin listener is
  not an acceptable substitute). **(d)** or **(i)** unfavourable changes a
  variable's tier or a documented capability, so both are operator decisions
  too. Only a resolution leaving requirements, tiers, documented capabilities
  and the ship decision untouched is autonomous.
- **How I test it.** Free and local. Read the recorded observations, then
  reproduce two or three from the re-observe recipe: pipe `save` into the
  running server's stdin and see whether it acts; start the server with RCON
  bound to loopback and query it from inside the container and from outside;
  grep the startup output for a credential value; send the bare `SIGTERM` and
  watch nothing happen. Cleanup: remove containers and test state directories
  by name.
- **Status.** `pending`

### step-pz-003 — The query protocol, and the health facts — `pending`

- **Objective.** Settle what the healthcheck can actually probe, and whether
  it can go false on a hung server.
- **Spec sections implemented.** §6, §2 (the query facts), root §5.5 (the
  three healthcheck predicates), root §2.5, root §5.2 (the player-facing bind
  rule).
- **Depends on.** `step-pz-002` (its resolution decides whether the fallback
  channel exists at all).
- **Deliverables.** Observations recorded and amended as in `step-pz-002`;
  the **Steam-query client** of root §5.5 entering the tree **pinned**, with
  version or digest recorded and its size measured (root §2.9).
- **Open facts settled here.**
  - **(a)** whether the Steam query protocol is answered on the **main game
    port** — the healthcheck target and the `GAME_PORT` description inherit
    the answer.
  - **(b)** whether the legacy `SteamPort1`/`SteamPort2` settings still open
    listeners on Build 42 — if present they belong in the port table, since
    root §5.2 documents *every* port.
  - **(k)** whether the A2S answer **tracks serving state at both ends** —
    the entire healthcheck premise.
  - **(f)** how a **non-Steam configuration** is detected from the effective
    settings. Unfavourable → a documented image-behaviour variable selects
    the probe mode (root §5.3's behaviour-knob category, never a
    game-settings mirror).
  - **(n)** whether the **player-facing UDP listeners bind `0.0.0.0`** by
    default or can be told to.
  - §2's port facts re-verified against the shipped build (the defaults and
    which are advertised).
- **Escalation.** **(k)** and **(l)** unfavourable while the console works is
  the **documented-degraded default healthcheck** — a ship decision, so it
  comes back to the operator: the honest remainder of A2S with its blind spot
  stated plainly, stop mediation intact, the wide listener still forbidden.
  **(f)** unfavourable adds a documented variable — a surface change, also
  the operator's.
- **How I test it.** Free and local, and it covers each claim rather than
  only the query itself:
  - **(a)/(k):** query with the pinned client at three moments —
    mid-world-load (must not answer), serving (must answer, with a player
    count), and frozen via `docker pause` (the answer must stop), then
    `docker unpause`.
  - **(b):** enumerate the container's actual listeners from the host
    (`ss -lunp` inside the network namespace via `docker inspect` for the
    PID, or `nmap -sU` against the published ports) and see whether 8766/8767
    are live.
  - **(f):** start the server once with Steam integration disabled and
    confirm the detection rule reads the effective configuration correctly.
  - **(n):** check the bind addresses of the player-facing UDP sockets in the
    same listener enumeration.
  The container registers with the Steam master server on its default
  profile — a transient listing for an ephemeral test server, ruled free
  deliberately, delisted on stop. Cleanup: stop and remove the container and
  state directory by name.
- **Status.** `pending`

### step-pz-004 — Workshop mods: where they land, and what a failure does — `pending`

- **Objective.** Settle the mod facts, and secure the requirement that
  nothing writes into the shipped game directory.
- **Spec sections implemented.** §7, root §3.4 (nothing writes into the
  shipped game directory — **never the thing that bends**), root §5.1, §1.
- **Depends on.** `step-pz-001`, and `step-pz-002` — the test needs a server
  that actually starts, which on a fresh state root requires the
  non-interactive account-creation mechanism that step settles.
- **Deliverables.** Observations recorded and amended as above, plus — if the
  mod target sits outside the state root — the **fixed required response** of
  §7: the target is brought **inside** the documented state root, by the
  game's own configuration where it offers one, otherwise by relocation or a
  link prepared at build time.
- **Open facts settled here.** **(g)** where the server writes downloaded
  workshop mods; **(h)** what it does when a workshop download fails at
  startup — refuses to start, starts without the mod, or hangs (§7 carries
  the documentation consequence, because a map-mod world loaded without its
  mod can regenerate or discard cells).
- **Escalation.** **(g)**'s impossible branch — where the target cannot be
  brought inside the state root, so the image documents a **narrowed
  read-only claim as a reasoned root §5.1 deviation** — comes back to the
  operator before it is taken.
- **How I test it.** Free and local, and slow: start the server with a small
  workshop mod configured and let it download (free per rule 9). Inspect
  where the files landed relative to the state root and the shipped game
  directory. Then force the failure case — an invalid mod id, and again with
  the container's network disabled — and observe which of the three
  behaviours occurs. Cleanup: remove the container and test state directory
  by name.
- **Status.** `pending`

### step-pz-005 — The complete writable-path set, logs, and read-only rootfs — `pending`

- **Objective.** Prove the writable-path claim the specification makes, or
  correct it.
- **Spec sections implemented.** §1 (the complete writable-path set;
  "nothing else may need write access, verified at implementation"), root
  §3.4 (the enumeration that makes root §5.1's read-only recommendation
  checkable rather than aspirational), root §5.1, root §5.5 (log destinations
  and **who rotates which file**).
- **Depends on.** `step-pz-004` (mods write, so the set is not complete
  before their target is known) and `step-pz-002` (the test needs a server
  that starts).
- **Deliverables.** The enumerated writable-path set, verified by running the
  container `--read-only` with writable mounts at exactly the documented
  paths; the log inventory — what reaches stdout, what exists only in files,
  and who rotates each; observations recorded and amended as above.
- **Open facts settled here.** **(o)** whether the `$HOME` override fully
  controls the game's idea of home — it covers native and `steamclient.so`
  paths, but the JVM resolves `user.home` from the passwd database first
  where the uid resolves, so **JVM-side paths (crash dumps) are verified
  separately**; **(j)** whether the server rotates or caps its own log files;
  §2's stdout fact re-verified (console output to stdout in the foreground
  **and** log files under the state root, so root §5.5's relay is not
  needed); and §1's "nothing else may need write access".
- **How I test it.** Free and local. Run `--read-only` with writable mounts
  only at the state root and `/tmp`, under an arbitrary non-root uid that
  exists in no `/etc/passwd` (root §3.4), and see the server start, serve and
  stop. Then run under a uid that *does* resolve and compare where JVM crash
  dumps land. Read the recorded log inventory. Cleanup: remove the container
  and test state directories by name.
- **Status.** `pending`

### step-pz-006 — Backup, save confirmation, and the upgrade fact — `pending`

- **Objective.** Settle what an operator can be told about taking a
  consistent backup, and what a version change does to a world.
- **Spec sections implemented.** §8 (the recipe's factual basis), §2 (the
  native backup feature), root §5.7.
- **Depends on.** `step-pz-002` (the channel a `save` would ride).
- **Deliverables.** Observations recorded and amended as above: the native
  backup feature's settings, what it writes and where, and **whether its
  completion is confirmable** — root §5.7 requires that stated, because a
  save command returning before data is flushed makes a hot copy no better
  than no save at all; plus the game's default backup settings and how to cap
  archive count and frequency.
- **Open facts settled here.** §2's **native backup feature**; §8's
  requirement that **RCON `save` completion confirmation be verified before
  documenting hot copies as safe** — unconfirmable → the documented safe
  procedure is stop / copy / start, said plainly; **(m)** what a Build 42
  point release does to an existing world. Research inconclusive → the
  documented answer is "unknown — assume irreversible; back up before any
  version change".
- **How I test it.** Free and local. Enable the native backup settings on a
  test world, restart, and see the archives appear inside the state root;
  issue a `save` through the mediation channel and observe whether anything
  confirms completion. The **(m)** observation is research plus, where two
  Build 42 point releases are reachable from the branch, an actual upgrade of
  a throwaway world — if not reachable, the pre-committed "unknown" answer
  stands and the step says so. Cleanup: remove the test state directory by
  name.
- **Status.** `pending`

---

## Milestone PZ-2 — The entrypoint

The adapter of root §3.5, built on facts rather than expectations. Every step
here has fixture tests in the *test* entry point; the entrypoint's language
is chosen at `step-pz-007` and its lint family arrives with its first file
(rule 2, never-ahead).

### step-pz-007 — Entrypoint skeleton, uid and state-root validation — `pending`

- **Objective.** A process that owns PID 1 correctly and refuses to start on
  anything unsafe about *identity and state*.
- **Spec sections implemented.** root §3.5, root §2.4, root §5.6 (the PID 1
  and orphan-reaping duties, and the tini-class option), root §3.4 (no
  default user; the uid-0 fatal naming `--user` and compose `user:`;
  `ALLOW_UID0`'s accepted values, with **any other value unparseable and
  fatal per root §5.3, parsed unconditionally whatever uid the container runs
  as**, naming the variable and the rejected value), §1 (a missing or
  unwritable state root is a **loud fatal before the game starts, never a
  fallback path**), root §5.6's table row for startup-validation failure.
- **Depends on.** `step-pz-005` (the writable set it validates).
- **Deliverables.** The entrypoint's language, logged with the alternatives
  rejected (rule 4 — the specification deliberately does not choose one); its
  lint family and the fixture-test harness; the PID 1 and signal model; the
  uid-0 fatal and `ALLOW_UID0` parsing; state-root validation; `$HOME` set
  per §1. Fixtures include **the cases that must fail**.
- **How I test it.** Free and local. Run the image as root and see the fatal
  naming `--user`; run it with an unparseable `ALLOW_UID0` value as a
  **non-root** uid and see the fatal naming the variable and the value —
  proving it is parsed unconditionally; run it with `ALLOW_UID0` truthy as
  root and see it proceed; run with the state root unmounted, then mounted
  read-only, and see the loud fatal each time; then `docker top` the
  container and confirm what PID 1 is. Cleanup: remove containers by name.
- **Status.** `pending`

### step-pz-008 — Configuration overrides and validation — `pending`

- **Objective.** Every variable of §3 applied to the effective
  configuration, including on the very first start, with one validation rule
  and no silent defaults.
- **Spec sections implemented.** §3 (the environment surface, and its stated
  consequence that credentials applied from the environment **persist into
  the mounted INI**, root §5.4's non-persistence "should" being unhonourable
  here), root §5.3 in full, root §5.4 (redaction where §2's echo fact
  requires it; the crash-dump limit documented), root §5.2 (`0.0.0.0` for
  player-facing ports, loopback for admin interfaces).
- **Depends on.** `step-pz-007`; the facts of `step-pz-002` (echo) and
  `step-pz-003` (bind addresses, non-Steam detection).
- **Deliverables.** The override mechanism — launch arguments, a pre-written
  INI, or a combination, this implementation's choice, **verified against the
  game's actual behaviour** per §3; every §3 variable parsed and applied,
  including on the first start of a fresh state root; the one validation rule
  (unparseable value → fatal naming variable and value); redaction if §2's
  echo fact requires it. The heap guard is deliberately **not** here — it
  shares no code path and no failure mode with override application, and has
  its own step.
- **Open facts settled here.** §3's requirement that the first-start override
  mechanism be **verified against the game's actual behaviour** — a first run
  on generated defaults would register with Steam on the wrong port and then
  silently change on restart.
- **How I test it.** Free and local. On a **fresh** state root, start with
  the game port and server name overridden and confirm from the very first
  run that the server uses them, not after a restart; set a nonsense stop
  timeout and see the fatal naming variable and value; start with a mounted
  INI and **no** game-specific variables and see it work. If §2's echo fact
  required redaction, grep the startup output for the credential values and
  find them redacted. Cleanup: remove containers and test state roots by
  name.
- **Status.** `pending`

### step-pz-009 — The heap guard — `pending`

- **Objective.** Prevent the most silent failure in this specification: a
  kernel OOM kill, which has no log line, lands mid-write, and is hidden by a
  restart policy.
- **Spec sections implemented.** §3 (the heap guard paragraph), root §5.3
  (the fatal-on-unparseable rule it obeys).
- **Depends on.** `step-pz-008` (it validates the effective heap that step
  computes).
- **Deliverables.** The entrypoint reads the container memory limit where the
  cgroup exposes one and **fails loudly before the game starts** when the
  effective maximum heap plus a **documented, deterministic non-heap
  allowance** exceeds it. The **must** is that the allowance is a number two
  implementations compute identically, never an adjective; the value itself is
  a recommended default (§3 names the larger of 512 MB or 25% of the heap).
  "Unlimited" reads differently per cgroup version and **both readings count
  as no limit** — a near-maximum number under v1, the literal string `max`
  under v2 — so **a non-numeric read is "no limit", never a parse error**.
  Where no limit is readable the game starts, and the documentation states
  what the default heap assumes of the container. Fixtures cover both cgroup
  readings, the no-limit path, and the over-limit fatal. The cgroup version
  in force on the development machine is recorded in
  `.claude/docs/environment.md`, not here; the fixtures cover both regardless
  of what this machine runs.
- **How I test it.** Free and local. Set the heap above a `--memory` limit
  and see the loud fatal naming both numbers; set it just below and see it
  start; run with no memory limit and see it start; and run the fixtures for
  the cgroup reading this machine cannot exercise. Cleanup: remove containers
  by name.
- **Status.** `pending`

### step-pz-010 — First boot and the admin account — `pending`

- **Objective.** The dangerous branch of a fresh state directory resolved
  before the game starts — never a hang, never an adminless public server.
- **Spec sections implemented.** §4 in full (both pre-table rules and the
  five-row table), root §5.4 (the `INITIAL_<NAME>` / `<NAME>` pattern and its
  fatal cases), root §5.3 (the mandatory-variable clause).
- **Depends on.** `step-pz-008`; `step-pz-002`'s resolution of **(d)** (it
  decides whether `ADMIN_PASSWORD` exists at all) and its discovery of the
  account table and per-`SERVER_NAME` database naming.
- **Deliverables.** The observable predicate — "an admin account exists for
  the effective `SERVER_NAME` and `ADMIN_USERNAME`" — implemented as a
  **query against the per-`SERVER_NAME` SQLite database**, never a
  file-existence guess, with the one valid shortcut in the absent direction
  only (a **missing** database proves the account absent with no query). §4's
  minimal **SQLite client** joins the image's tooling if the entrypoint needs
  one, entering the tree pinned with version or digest recorded (rule 2). The
  five table rows, including the pre-table rule that a set-but-unsupported
  `ADMIN_PASSWORD` is **fatal regardless of anything else, validated before
  the rows**. Fixtures for every row, the fatal rows included.
- **How I test it.** Free and local. On a fresh state root: start with
  neither credential variable set and see the fatal naming **both**; start
  with the initial-password variable set and see the account created and the
  server start; restart with it still set and see it ignored **without a
  warning** — its documented contract; change `SERVER_NAME` on the populated
  state root and see a first boot for that name rather than an adminless
  start; interrupt a first boot (`docker kill` mid-creation), restart, and
  see the entrypoint still treat the account as absent — the case a
  file-keyed implementation gets wrong. Cleanup: remove containers and test
  state roots by name.
- **Status.** `pending`

### step-pz-011 — Shutdown mediation — `pending`

- **Objective.** The convention whose violation is silent, made to work: a
  stop signal that saves and exits, with an honest exit code.
- **Spec sections implemented.** §5 in full, root §5.6 in full including the
  exit-code table, root §2.4, root §5.2 (the internal listener appears in the
  **port table** as an admin interface with its bind address).
- **Depends on.** `step-pz-007` (the signal model), `step-pz-002` (the
  channel).
- **Deliverables.**
  - `save` then `quit` through a channel that **exists regardless of operator
    configuration**, then a bounded wait for the process to exit
    **successfully, on its own** — root §5.6's confirmed clean stop, the only
    thing that exits 0. A stop arriving **while the world is still loading**
    follows the same rules and lands, deliberately, on the timeout row's
    non-zero exit.
  - `STOP_TIMEOUT` with §3's default under the recommended grace floor, the
    pairing rule documented, and the **effective timeout printed at start and
    again on receipt of the stop signal**.
  - Where §5's fallback applies: **reuse** operator-configured RCON — by §3's
    variables **or directly in the INI, which counts equally**, discovered
    from the effective INI the entrypoint already manages — never a second
    listener, never overwriting the operator's password. When the entrypoint
    enables RCON itself: **loopback only**, ephemeral generated password with
    enough entropy that brute force over loopback is impractical, not
    persisted into any backed-up file beyond what the game's own INI
    rewriting forces — and where it is forced, the residue is **never
    mistaken for operator configuration**: a password the entrypoint
    generated is rotated or scrubbed at each start rather than "reused". The
    recognition mechanism is this implementation's choice, logged. The
    generated listener does **not** inherit the wide-bind treatment operator
    RCON gets.
  - The **operator's `docker exec` path** to save and announce, working
    **regardless of `RCON_PASSWORD`** (root §5.5's exec capability, §5).
  - Orphan reaping if the entrypoint stays PID 1 (root §5.6).
  - Fixtures for every row of root §5.6's table.
- **How I test it.** Free and local. `docker stop --timeout 120` a serving
  server: observe the printed effective timeout at start and on the signal,
  the save, the clean exit, and **exit code 0** (`docker inspect`). Then stop
  one **mid-world-load** and see a non-zero exit. Then contrive timeout
  expiry with a very short `STOP_TIMEOUT` and see the game terminated with a
  non-zero exit and an attributable message. Then quit the game through its
  own admin channel and see its exit code propagated verbatim. Then, on a
  deployment with **no** `RCON_PASSWORD`, run the documented `docker exec`
  save and announce and see them work. Cleanup: remove containers and test
  state roots by name.
- **Status.** `pending`

### step-pz-012 — Health — `pending`

- **Objective.** A HEALTHCHECK that probes the game protocol, targets the
  effective configuration, and can go false on a hung server.
- **Spec sections implemented.** §6 in full, root §5.5 (the HEALTHCHECK
  requirement, its three predicates, and the two must-have operator
  capabilities without exposing any admin port outside the container), root
  §2.5, root §5.3 (a behaviour knob rather than a game-settings mirror, if
  **(f)** required one).
- **Depends on.** `step-pz-003` (what can be probed), `step-pz-011` (the
  channel the fallback rides).
- **Deliverables.** The HEALTHCHECK against the **effective** port
  configuration; the three predicates of root §5.5 honoured, with a liveness
  predicate that **can go false on a hung server** — a log-line match may
  serve only as *readiness*, never liveness, and a process-level check never;
  a `start_period` whose **value and reasoning the image documents**,
  accepting §6's stated trade-off. The **non-Steam configuration** detected
  from the effective configuration and switched to §6's fallback order
  automatically. Both root §5.5 clients ship. The operator's own probe — "is
  it serving, and how many players" — with the player count coming through
  the mediation channel when the query protocol is off, documented.
- **How I test it.** Free and local. Watch `docker inspect` health go from
  `starting` to `healthy` and confirm it was **not** healthy during world
  load; freeze the server with `docker pause` and watch health go
  `unhealthy`, then `docker unpause`; run the same image in the **non-Steam
  profile** and confirm it reports healthy through the fallback rather than
  permanently unhealthy; run the operator probe from the host and read the
  player count. Cleanup: remove containers by name.
- **Status.** `pending`

---

## Milestone PZ-3 — Publication readiness and documentation

### step-pz-013 — Labels, the builder digest pin, and a development build — `pending`

- **Objective.** The image carries what §8's automation and root §7's tags
  read, and its builder reference is a published digest.
- **Spec sections implemented.** root §5.8 (the full label set, the buildid
  label being the machine-readable side of §8's comparison), root §3.1 (the
  builder stage referenced by a pinned tag or digest, recorded in the
  labels), root §7.
- **Depends on.** `step-pz-012`; **`step-008` done** (the builder is
  published, so a digest exists to pin). The decision for the pin switch is
  logged in **this track's** `DECISIONS.md` — it governs a `pz`-track file —
  cross-cited from the root log where `step-008` records the publication.
- **Deliverables.** The label set computed at build time; the builder
  reference switched from `step-pz-001`'s local tag to the **published
  digest**; a local build proving the labels are right.
- **How I test it.** Free and local, but **not cheap: changing the builder
  stage's `FROM` invalidates that stage's cache, so the multi-gigabyte Steam
  download runs again** — budget for a full rebuild, not an incremental one.
  (If the published builder is byte-identical to the local one, some layers
  may survive; do not count on it, and say which happened.) Then
  `docker inspect --format '{{json .Config.Labels}}'` and check every
  required label against the game actually inside: version, buildid, branch,
  builder digest, source, description, licence. Confirm the builder digest
  resolves (`docker buildx imagetools inspect` — a registry read, free).
  Cleanup: `docker image rm` by name.
- **Status.** `pending`

### step-pz-014 — The Project Zomboid README — `pending`

- **Objective.** The image's per-image documentation, which is also its GHCR
  page: everything an operator needs, and every caveat the specification
  insists be visible. It ships **before** the first release tag
  (`step-011`), because a pinnable public image whose GHCR page is empty
  withholds exactly the knowledge root §5.7 exists to deliver before a pull.
- **Spec sections implemented.** root §9 (the per-image README's content
  requirements in full), §8 (the backup recipe), §1–§7 as resolved, root
  §5.1–§5.7, root §6.
- **Depends on.** every step above.
- **Deliverables.** A README covering: the environment-variable table with
  **mandatory/optional flags**; ports and roles with the
  **advertised-or-remappable flag**, admin interfaces documented separately
  with the never-expose-publicly warning; writable paths and the state root
  **including the mount-ownership preparation step** — a fresh named volume
  is created root-owned while the container runs under the operator's uid,
  the most common first-contact failure, and root §3.4's loud fatal needs its
  documented cure; configuration behaviour including the **rewrite** and
  **env-override** caveats and §3's credential-persists-into-the-INI
  consequence; shutdown semantics with the recommended grace period, the stop
  timeout and the pairing rule; the healthcheck, its `start_period` and
  reasoning, and how to probe, save and announce from outside; the backing-up
  section with the version-upgrade warning and the archive-capping advice;
  the workshop-mod section including the slow first start, the
  Steam-connectivity need, and **what a failed mod download does**; the tag
  policy including that **moving tags cross game versions on pull**; the
  `ALLOW_UID0` opt-out and exactly when it is legitimate; the
  crash-dumps-may-contain-secrets warning; and a minimal `docker run` and
  compose example. **Platform-neutral throughout** (root §1, root §9). It
  links to the repository README for the shared conventions rather than
  restating them.
- **How I test it.** Free and local, and this is the real test of the whole
  track — in two halves, so the long one is optional:
  - **Mechanical half:** check the variable, port and path tables against
    `docker inspect` output and the entrypoint's own validation, and confirm
    every documented default matches the shipped image.
  - **Follow-it-verbatim half:** from a clean machine state, prepare the
    mount as the README says, run the `docker run` example verbatim, then the
    compose example, and confirm every documented claim — ports, paths,
    health, stop, exec save — behaves as written. Any divergence is a
    documentation defect, not an operator error. Budget half an hour or more.
  Cleanup: as the README's own instructions say — itself part of the test.
- **Status.** `pending`

---

## Cross-track dependencies

| This track | needs | for |
|---|---|---|
| `step-pz-001` | `step-006` done | the builder image to build against |
| `step-pz-013` | `step-008` done | a published builder digest to pin |
| **The root track needs from here** | | |
| `step-009` | `step-pz-011`, `step-pz-012` done | stop mediation and health, before the smoke gate can assert them |
| `step-010` | `step-pz-013` done | labels and the digest pin, before CI builds and publishes |
| `step-011` | `step-pz-014` done | the per-image README that is the GHCR page, before the first pinnable release |
| `step-014` | `step-pz-014` done | a per-image README that links to the repository README |
| `step-015` | this whole track | a path actually walked, before the guide describes it |

## Coverage map — `project-zomboid/SPECIFICATIONS.md`

| Section | Step(s) |
|---|---|
| §1 Scope (Build 42; Build 41 non-goal; fixed state root; writable-path set) | `step-pz-001`, `step-pz-005`, `step-pz-007` |
| §2 Facts about the PZ dedicated server | `step-pz-001` through `step-pz-006`; the open-facts register below maps each item |
| §3 Environment surface | `step-pz-008`; `step-pz-009` (the heap guard); `step-pz-010` (the credential variables); `step-pz-011` (`STOP_TIMEOUT`); `step-pz-007` (`ALLOW_UID0`) |
| §4 First boot | `step-pz-010` |
| §5 Shutdown | `step-pz-011` (mediation), `step-pz-002` (the channel it uses) |
| §6 Health | `step-pz-012` (implementation), `step-pz-003` (its factual basis) |
| §7 Workshop mods | `step-pz-004` (facts and the required response), `step-pz-014` (documentation) |
| §8 Backup recipe | `step-pz-006` (facts), `step-pz-014` (the documented recipe) |

**Deliberately not implemented:** §1's **Build 41 non-goal** — `legacy41`
communities are unsupported by this image; they use the many existing B41
images. Nothing is built for it, and the README says so.

## Open facts register

Every open fact of §2 and of the sections carrying one in prose, with the
step that settles it. **E** marks the ones that come back to the operator
before the amendment lands, whatever the pre-committed response says — a
pre-committed response fixes what will happen, not who watches it land.

| Item | Fact | Settled at | |
|---|---|---|---|
| (a) | Steam query answered on the main game port | `step-pz-003` | |
| (b) | legacy `SteamPort1`/`SteamPort2` listeners on Build 42 | `step-pz-003` | |
| (c) | console accepts `save`/`quit` over a non-interactive stdin pipe | `step-pz-002` | **E** with (l) |
| (d) | non-interactive admin password change on an existing account | `step-pz-002` | **E** |
| (e) | where the human-readable version string is authoritatively read from | `step-pz-001` | **E** if it changes the tag scheme to buildid-derived |
| (f) | how a non-Steam configuration is detected from the effective settings | `step-pz-003` | **E** if it adds a documented variable |
| (g) | where the server writes downloaded workshop mods | `step-pz-004` | **E** on the impossible branch |
| (h) | what the server does when a workshop download fails | `step-pz-004` | |
| (i) | whether the mediation channel answers status and player count non-destructively | `step-pz-002` | **E** |
| (j) | whether the server rotates or caps its own log files | `step-pz-005` | |
| (k) | whether the A2S answer tracks serving state at both ends | `step-pz-003` | **E** with (l) |
| (l) | whether RCON offers a bind-address setting | `step-pz-002` | **E** |
| (m) | what a Build 42 point release does to an existing world | `step-pz-006` | |
| (n) | whether player-facing UDP listeners bind `0.0.0.0` | `step-pz-003` | |
| (o) | whether the `$HOME` override fully controls the game's idea of home (JVM `user.home` separately) | `step-pz-005` | |
| §2 prose | `steamclient.so` resolution: `~/.steam` link farm or the game's own directories (also root §2.9) | `step-pz-001` | |
| §2 prose | the non-interactive account-creation path §4 rests on | `step-pz-002` | **E** if absent (the fallback is a fatal, and §4's table changes) |
| §2 prose | whether the server echoes credential values into startup output | `step-pz-002` | |
| §2 prose | the native backup feature (settings, archives, location) | `step-pz-006` | |
| §1 prose | "nothing else may need write access" | `step-pz-005` | |
| §3 prose | the first-start override mechanism verified against the game's actual behaviour | `step-pz-008` | |
| §8 prose | whether RCON `save` completion is confirmable | `step-pz-006` | |
| root §2.9 | the §5.5 client sizes (RCON, Steam-query) | `step-pz-002`, `step-pz-003` | |
| **§2 header — the dated facts, one by one** | | | |
| | the branch, the version string, the JRE, the state layout | `step-pz-001` | **E** where a change moves a requirement or a tier |
| | the INI is per-server-name and **the game rewrites it** | `step-pz-008` | **E** if the rewriting behaviour changed |
| | the port numbers and which are advertised | `step-pz-003` | |
| | console output to stdout **and** log files under the state root | `step-pz-005` | |
| | **the server does not act on `SIGTERM` natively** | `step-pz-002` | **E** if it now does — every mediation decision rests on this |
| | the admin-account table and per-`SERVER_NAME` database naming (§4's predicate needs it) | `step-pz-002` | |

## Open questions for the operator

1. **Five fact-finding steps before any entrypoint code.** `step-pz-002`
   through `step-pz-006` are observation work with no product code beyond the
   pinned clients, and each takes one of your gates. I chose that split
   because three of them can stop or degrade the project — (c)+(l), (k)+(l),
   (g)'s impossible branch — and finding that out after the entrypoint is
   written wastes the entrypoint. If you would rather spend fewer gates,
   `step-pz-004`, `step-pz-005` and `step-pz-006` can merge into one "state,
   mods and backup facts" step; `step-pz-002` and `step-pz-003` should not
   merge, because `step-pz-002`'s answer decides what `step-pz-003` can even
   test.
2. **The image's state-root path is mine to choose** (§1 says so), and it
   becomes a documented fact operators mount against. I will propose one at
   `step-pz-001` with its reasoning; if you have a preference, it is cheaper
   to say before that step than after.
3. **The entrypoint language is a workflow choice this workflow leaves to
   me** (rule 4's third kind), so I will log it rather than ask — but it
   decides which lint and test tooling the repository grows, so if you have a
   preference, `step-pz-007` is where it binds and before it is free.
4. **(m) may be unanswerable by observation.** Whether two Build 42 point
   releases are reachable from the stable branch when `step-pz-006` runs is
   not in my control; Steam serves what the branch holds *now*. The
   pre-committed "unknown — assume irreversible" answer is the
   specification's own, so this is a note rather than a question — unless you
   have a saved world from an older point release, which would make the
   observation possible.
