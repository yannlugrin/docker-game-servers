# Game Server Images — Specification

## How to read this document

This document states what must exist, under which constraints, and why. It
never prescribes implementation: no Dockerfile contents, no file layouts, no
tool syntax. Three tiers of statement:

- **Requirements** — written as "must". Decisions already taken, not open for
  reconsideration during implementation. Where a requirement exists because
  of a trade-off, the reasoning is given so it can be evaluated rather than
  merely obeyed.
- **Recommended defaults** — written as "should". Starting points the
  implementation may deviate from with reason.
- **Constraints of the environment** — facts about tools, protocols and
  products. Not decisions: stated, with the reason they matter, because
  discovering them mid-implementation is expensive.

Where this document says something must **not** happen, it is usually because
the failure is silent — corrupted or lost state rather than a visible error.
The two chronic silent failures of containerized game servers are a stop
signal that never reaches the game (a save-corrupting `SIGKILL` days later)
and a secret that quietly lands in a backed-up file or a log stream. Both
recur throughout this document.

## 1. Goal

A public repository of Docker images for dedicated game servers, built to be
as light as each game allows. Two kinds of image:

- a **builder image** carrying steamcmd and everything needed to install any
  Steam dedicated server at build time;
- **per-game runtime images**, one per game, containing the installed game,
  its runtime dependencies, and the small operator tooling of §5.5 —
  nothing else. The first game is the Project Zomboid dedicated server
  (Build 42).

The images are generic: they document their interface — environment
variables, ports, writable paths, configuration, shutdown behavior — the way
any well-behaved public image does, and are usable with plain `docker run`,
compose, or any orchestrator. They must not name or assume any specific
hosting platform.

A game image runs exactly one server instance per container. It never
installs or updates game content at runtime (game-managed runtime content
such as workshop mods is the one exception, stated per game, §6); it never
manages fleets, schedules backups, or supervises anything beyond its own
process.

## 2. Environment and context

Facts this design rests on. Each matters to at least one requirement below.

**2.1 steamcmd is a 32-bit glibc binary.** It requires 32-bit compatibility
libraries (`lib32gcc-s1` on Debian-family systems) and certificates for
Steam's TLS endpoints, and it does not run on musl — Alpine-class bases are
ruled out, and images are **linux/amd64 only**. The realistic size floor is
a Debian/Ubuntu slim base; Debian 13 slim (`trixie-slim`) is the smallest
mainstream option.

**2.2 steamcmd self-updates on launch and has no published versions.** Every
run may touch the network and mutate its own installation. Consequence: the
builder image cannot be pinned to a steamcmd version — its tags are dated
snapshots (§7) — and a build that runs steamcmd is only as reproducible as
Steam's depots allow.

**2.3 Steam distributes dedicated servers per app id, with branches.** Many
dedicated servers, including Project Zomboid's, install via anonymous login.
Each app/branch exposes a numeric **buildid** that changes on every game
update and is queryable without downloading — this is what makes scheduled
update detection (§8) possible.

**2.4 PID 1 signal semantics.** Inside a container the entrypoint process is
PID 1 of its namespace. The kernel delivers PID 1 only signals it has
explicitly installed handlers for — a process that would die to `SIGTERM` as
an ordinary process silently ignores it as PID 1. A shell between the
runtime and the game swallows the stop: common shells `exec` a single
simple command, so the plainest shell-form entrypoint escapes by luck — but
any compound command, `&&` chain, or wrapper script that does not `exec`
its final process leaves a shell as PID 1 that neither handles nor forwards
the signal. Either
mistake produces the same outcome: the runtime waits out the stop grace
period, then `SIGKILL`s the server mid-write, with nothing in any log. This
is why §5.6 is the strictest section of the conventions.

**2.5 Steam query protocol.** Steam-registered servers answer the A2S query
protocol (serving status, player count) — some on the game port itself,
others on a dedicated query port; which one is a per-game fact that belongs
in the game's port table (§5.2). It is the correct liveness probe either
way: a hung server keeps its process alive but stops answering queries.

**2.6 Registry.** GHCR hosts public images free of charge, with
credential-less anonymous pulls and native GitHub Actions integration
(build and push in one workflow, no extra credentials). Docker Hub
rate-limits anonymous pulls. These facts drive the registry decision in §7.

**2.7 Dedicated servers load Steam client libraries at runtime.** Many
Linux dedicated servers dlopen `steamclient.so`, typically resolved via
`~/.steam/sdk64/` (or `sdk32/`) — paths a steamcmd installation normally
provides as a side effect. A game image that excludes steamcmd must still
ship or link the Steam client libraries its game loads: images that "work
with steamcmd present, break without it" almost always break on these
libraries, never on the steamcmd binary itself. Discovering this
mid-implementation is the classic first-build failure of baked game images.

**2.8 GitHub Actions disables idle scheduled workflows.** In a public
repository, `schedule`-triggered workflows are automatically disabled
after roughly 60 days without repository activity. A finished, stable
repository is exactly the one that goes quiet for two months — at which
point a scheduled refresh (§8) silently stops running while the published
images keep pulling and passing every check. This fact is why §8 requires
the refresh to be deactivation-resistant.

**2.9 What this section is least sure of.** These facts were researched,
not measured; where one fails, the named consequence moves, not the
architecture: the exact `steamclient.so` resolution varies per game (§2.7 —
each per-game specification carries its own verification item); the size
claims (the ~megabytes cost of the §5.5 clients, Debian slim as the
smallest workable base) are expectations to be measured at implementation;
and steamcmd's undocumented behavior (self-update format, anonymous-login
scope) can shift under Valve's control at any time, which is part of why
the builder is date-stamped and pre-warmed rather than assumed stable.

## 3. Core model

**3.1 Two tiers, one build direction.** The builder image installs games;
game images contain them. Every stage of every image is based on
**Debian 13 slim (`trixie-slim`)** — a decision, resting on the facts of
§2.1: the smallest mainstream base satisfying steamcmd's glibc and 32-bit
needs, with a long support horizon; Ubuntu was rejected as slightly larger
for no functional gain, and one base across all stages keeps layers shared.
Every game image is produced by a multi-stage
build: the builder stage (from the steamcmd image) downloads the game, and
the final stage starts from the slim runtime base and copies the game in,
adding only that game's runtime dependencies — including the Steam client
libraries the game loads at runtime (§2.7), which the builder stage
provides. The builder stage must be referenced by a **pinned tag or
digest**, never a moving pointer — otherwise two builds of the same
immutable game tag can differ at their root and nothing records why — and
the builder reference used is recorded in the image's labels (§5.8).
steamcmd never appears in a game image — its only runtime use
would be in-place game updates, which the versioning model deliberately
forbids.

**3.2 The game is baked in at build time**. An image that installs
at runtime has a meaningless tag, unreproducible content, minutes-long cold
starts, and a Steam dependency at every deploy. Baked images start in
seconds, and their tags honestly say which game version is inside — which is
what lets consumers pin by digest and reason about what runs. The trade-off
is accepted: game images are multi-gigabyte, registry storage is cheap, and
every game update becomes an image rebuild, which CI absorbs (§8).

**3.3 One repository, one set of conventions.** All images live in this
repository and every game image obeys §5 in full. A game image is meant to
be mostly convention plus a small game-specific delta — captured in the
game's own specification (§6); the conventions are what an operator can
rely on across all images without rereading each one.

**3.4 Images are uid-agnostic.** A game image must run correctly under an
arbitrary `--user uid:gid`, including one that exists in no `/etc/passwd`
where the game tolerates it, and must never require root at runtime. No file
the image ships may be owned by, or readable only by, a build-time-chosen
uid: shipped content must be world-readable (0644 files, 0755 directories
and executables). The reason is multi-instance isolation: operators isolate
instances by running each under a distinct uid over owner-only state
directories, and any baked-in ownership breaks that or forces a re-chown of
gigabytes. All state is written under `$HOME` or under the image's
documented state paths — never into the shipped game directory.

Two consequences, both requirements. The image declares **no default
user**, and the entrypoint **fatally refuses to run as uid 0**, with a
message naming `--user` (and compose `user:`). The real ground is forcing
the uid choice to be deliberate: a container cannot distinguish an
operator-chosen uid from an image default, and on plain Docker a root
default additionally plants root-owned files in the operator's volume
(springing the unwritable-state-root fatal the first time `--user` is
added), while an image-invented default uid puts numbers nobody chose on
the operator's disk. One documented opt-out exists, because on rootless
and user-namespaced runtimes (rootless Podman, userns-remapped Docker,
Kubernetes pods without `runAsUser`) in-container uid 0 maps to an
unprivileged host user and is the runtime's default: setting
**`ALLOW_UID0`** to `1` or `true` (case-insensitive) skips the fatal —
setting it *is* the deliberate choice, and its documentation says exactly
when it is legitimate. `0` and case-insensitive `false` are recognized as
an explicit "off" (the fatal proceeds normally); any *other* value is
unparseable and follows §5.3's validation rule — the fatal message names
the variable and the rejected value, so an operator whose opt-out attempt
was mangled is not left staring at the generic message. And the per-game specification must enumerate the
**complete writable-path set** — the state root, `/tmp`, and what the
image sets `$HOME` to — so the read-only-rootfs recommendation of §5.1 is
checkable rather than aspirational.

**3.5 The entrypoint is the adapter.** Each game image has a thin
entrypoint whose core jobs are: validate the startup state and fail loudly
on anything unsafe (§5.3, §5.4); apply optional environment overrides to
the effective configuration (§5.3); hand PID 1 to — or reliably relay
signals to — the game (§5.6); and mediate shutdown for games that do not
handle their stop signal (§5.6). §5 assigns it narrower duties where a game
needs them (log relay, output redaction). Everything else — what to
configure, when to run — belongs to the operator.

## 4. The steamcmd builder image

**4.1 Purpose.** The build stage for every game image in this repository,
and usable on its own as a generic "install a Steam app" builder by anyone.
It is not a runtime image and its documentation must say so.

**4.2** It must be based on the project's base (§3.1) and contain a
working steamcmd, already run once at build time so its self-update is
baked into the layer — otherwise every consumer's first build step
re-downloads the steamcmd runtime, paying the cost once per game build
instead of once per base build.

**4.3** It must be able to install a given app id, from a given branch
(including password-protected beta branches) with anonymous login, and
support Steam's file validation. For non-anonymous apps, the design must
not preclude accepting credentials at build time (§10.4) — and the
guarantee, stated channel-neutrally because the obvious channel is the
trap, is that a credential **never persists in any layer or in the image's
build history**: a plain build argument or baked environment variable does
persist there, which is exactly what rules those out.

**4.4** It should contain nothing beyond steamcmd's needs (certificates,
32-bit libraries): no editors, no locale packs, no convenience tooling.
Every megabyte here is inherited by every game build's cache.

## 5. Game image conventions

Every game image must satisfy this section. Its per-game specification (§6)
adds the game's specifics and documents how each convention is honored.

### 5.1 Filesystem and state

- The image must document **every path the game persistently writes** — saves,
  worlds, databases, configuration the game rewrites, mod downloads, log
  files that cannot be redirected. Anything outside the documented paths is
  ephemeral by definition, and a save landing outside them is a data-loss
  bug in the image.
- State should be consolidated under a **single documented state root** per
  image where the game allows, so an operator persists one mount instead of
  chasing scattered paths.
- The image must state what it does with `$HOME`: either it honors the
  inherited value (and its documentation says the operator must point it
  somewhere writable), or it sets its own and that value wins over anything
  the operator passes. One rule, documented — an unstated `$HOME` policy
  surfaces as Steam link farms and crash dumps landing on a read-only path,
  which presents as a server that runs but never registers, not as an
  error.
- The image should run with a **read-only root filesystem** given writable
  mounts at the documented paths plus `/tmp` — it costs little at build time
  and proves no state hides in undeclared locations.

### 5.2 Ports

Port configurability is a property of the game, not of the image — an image
cannot promise what the game does not offer. The image's obligations are to
document honestly and to expose what the game does offer:

- The image must document **every port**: role, default number, protocol, and —
  the operationally vital flag — whether it is **advertised** or **freely
  remappable**. An advertised port is one whose number the game publishes
  outside itself (Steam server browser registration above all): it works
  only when the game's idea of its port matches the number published on the
  host, so it cannot be silently remapped. Every other port can be mapped
  to any host number by the container runtime and needs no in-game
  configurability at all.
- For **advertised ports**, the image must expose the game's own port
  setting (configuration and, where common practice, an environment
  variable) when the game supports changing it. When the game cannot, the
  image documents the fixed number and its consequence — publish it 1:1,
  and two instances of that game cannot share a host — as a stated
  limitation rather than a surprise. A fixed advertised port costs
  flexibility; it does not break a single-instance deploy.
- For **player-facing ports**, the image's shipped or effective
  configuration must make the game listen on `0.0.0.0` wherever the bind
  address is configurable; a game that binds narrower and cannot be told
  otherwise is documented as a limitation. Binding narrower breaks port
  publication for no isolation gain inside a private network namespace.
  **Admin interfaces are the opposite case**: they bind loopback where the
  game allows it, and are opened wider only by the operator's deliberate
  choice — under host networking or a shared network namespace, a
  `0.0.0.0` admin listener is exposed with no publication step at all.
- Admin interfaces (RCON and relatives) are documented separately from
  player-facing ports, with an explicit warning that they must never be
  exposed publicly. The image must not enable an admin listener with a
  default password — a guessable admin port is a silently owned server.

### 5.3 Configuration

- The game's **native configuration files are the authoritative interface**.
  For every value the game itself can take from a file, the image must be
  fully operable with a mounted configuration and no game-specific
  environment variable set. Values the game keeps only in state it creates
  itself — a first-boot admin credential living in the game's database, for
  instance — cannot come from a mountable file and are exactly what the
  mandatory-variable clause below exists for.
- Environment variables are **optional overrides**: when set, the entrypoint
  must apply them to the effective configuration at startup. When unset,
  the configuration file's values stand. The documentation must state the
  consequence for the whole env surface: an override applied at every start
  wins over the same setting changed in game or in the file — a variable
  left set in a compose file silently reverts the in-game change on every
  restart, which is the same failure the rewrite caveat below warns about,
  caused by the image instead of the operator. And one validation rule for
  the whole surface: a variable **set to a value the entrypoint cannot
  parse or apply is a fatal start naming the variable and the value** —
  never a silent fall-back to the default. A silently substituted default
  is the document's own failure shape: an operator who believes they set a
  300-second stop timeout gets 80, and the save dies to a bound they
  thought they had removed. Documentation flags every variable
  **mandatory or optional**; mandatory is reserved for values without which
  the game cannot start safely (each per-game specification shows the
  pattern, §6).
- The image must not invent environment variables for arbitrary game
  settings. The env surface stays small — identity, ports, credentials,
  resource limits, and the image's own behavior knobs (the stop timeout of
  §5.6, the uid-0 opt-out of §3.4) — because an unbounded env-to-config
  mapping is a second configuration system to maintain, forever chasing the
  game's own.
- If the game **rewrites its own configuration files** at runtime, the image
  documentation must say so prominently. An operator who re-renders the file
  on every deploy will otherwise silently revert every setting changed
  in-game — a baffling failure when it is not written down.

### 5.4 Secrets

- **No secret in any image layer, ever** — the images are public, and a
  value deleted in a later layer is still in the earlier one. No default
  values for any credential.
- Secrets arrive by the two routes of §5.3: already present in the mounted
  configuration, or via environment override. When applied from the
  environment, the injected value should not be persisted to a mounted path
  where the game permits working from an ephemeral copy — mounted paths are
  what operators back up.
- A missing mandatory secret is a **fatal start with a clear message naming
  the variable** — never a warning, never a fallback. A server that starts
  anyway starts unprotected, and nobody reads warnings on a server that
  seems to work.
- Credentials that live in **game-created state** (an account database the
  game writes at first boot, rather than a config file) follow a
  two-variable pattern, and each image documents only the forms its game
  supports: `INITIAL_<NAME>` is consumed at first start and ignored — by
  definition, not by failure — once the state exists, so leaving it set
  forever is the normal, harmless deployment; the bare `<NAME>` is a
  declarative override applied at every start, offered only where the game
  can re-apply the value non-interactively, because its contract — the
  environment wins, in-game changes revert — is exactly what its name
  promises. Setting an override the image cannot honor is a **fatal
  start**: the operator asked for a guarantee the image cannot give, and
  anything quieter lets believed and effective credentials silently
  diverge.
- No secret may ever reach stdout or stderr: where startup logs echo
  configuration, credential values must be redacted. Crash dumps are the
  honest limit of that promise — a memory dump contains whatever the
  process held, credentials included, and no image can prevent it — so the
  obligation there is documentation: the docs must warn that crash dumps
  may contain secrets and are to be treated as sensitive.

### 5.5 Observability

- The game's output must go to **stdout/stderr, unfiltered** — the container
  runtime owns collection and rotation. Unfiltered has exactly one
  exception, which takes precedence: the §5.4 redaction of credential
  values, for games that echo their configuration at startup. Log files the
  game insists on writing are declared under §5.1 so operators can deal
  with them.
- When the game cannot send its primary output to stdout/stderr, the
  entrypoint should relay the log file(s) there, following across the
  game's own rotation; a static symlink onto the stdout device is an
  acceptable cheap variant only where the game never rotates that file.
  Whatever the mechanism, the documentation must state what reaches stdout
  and what exists only in files, and **who rotates which file** — an
  unrotated log the operator does not know about fills the state disk
  slowly and silently, and a full state disk corrupts saves.
- Each image must declare a **HEALTHCHECK that probes the game protocol**
  (Steam query), not the process: a hung server is alive and
  unhealthy, and process-level checks call it healthy. Two clauses, kept
  apart because Docker's `start_period` only suppresses *unhealthy*
  transitions, never healthy ones: the **probe itself** must not answer
  positively before the server actually serves (a responder that comes up
  early marks the container healthy mid-load, and no start period prevents
  that); the `start_period` exists only so a slow start is not marked
  unhealthy, and must absorb worst-case load time. The check must stop
  reporting healthy once the
  server is no longer serving — no longer answering queries. A *full*
  server still serves: the predicate is answering, not joinable, or the
  probe flaps exactly when the server is most alive. The probe targets the
  **effective** configuration — a probe baked to the default port marks a
  correctly reconfigured server permanently unhealthy. And the
  `start_period` trade-off is stated so it is chosen deliberately: sizing
  it for the worst case (first-boot world generation) blinds hang detection
  for that long on every later restart; the image documents the value and
  the reasoning.
- Two capabilities are **must**, both without exposing any admin port
  outside the container: the operator can ask "is it serving, and how many
  players" from the host (the healthcheck's own probe doubles as the
  tool), and — where the game has an admin protocol or console — the
  operator can issue save/announce commands from inside the container via
  `docker exec`. The recommended default providing both is shipping two
  minimal static clients, a **Steam-query client** and an **RCON client**
  (the latter useful only where the game's admin protocol is enabled, and
  never the mediation a stop depends on, §5.6); expected to cost megabytes,
  not tens of megabytes — measured at implementation. A game needing a
  different mechanism documents what replaces them.

### 5.6 Lifecycle and shutdown

This is the convention whose violation is silent (§2.4): every other failure
in this document announces itself at startup; this one corrupts a save days
later with nothing in any log.

- The container's stop signal (`SIGTERM` unless the image documents
  another) must result in the game **saving and exiting cleanly** within a
  reasonable grace period. The image documents its **recommended minimum
  grace period**; 90 seconds is the floor to recommend to operators, because
  Docker's 10-second default is a save-corrupting trap for game servers.
- The entrypoint must guarantee signal delivery: either the game binary is
  PID 1 (exec'd, exec-form), or the entrypoint remains PID 1 with explicit
  handlers and reliably relays the stop. An entrypoint that stays PID 1
  also inherits PID 1's second duty: it must **reap orphaned child
  processes** — unreaped zombies are a slow silent leak on exactly the
  long-lived servers these images run.
- If the game does not act on the stop signal natively, the **entrypoint
  must translate it** into the game's own shutdown mechanism (console
  command, RCON `save`+`quit`, whatever the game provides), then wait for
  the game process to exit. The mediation path must work regardless of
  optional operator configuration — a stop that only works when the operator
  happened to enable RCON is a stop that fails silently on default setups.
- The wait is bounded by an **operator-settable stop timeout** (an
  environment variable with a documented default), documented alongside the
  grace-period recommendation with the rule that binds them: **the timeout
  must sit below the runtime's stop grace period**, because the two ends of
  the race are asymmetric — a timeout that fires first produces a logged,
  attributable failure (the entrypoint terminates the game and exits
  non-zero, save unconfirmed), while a grace period that fires first is a
  silent `SIGKILL` with generic exit 137 and no explanation in the log. No
  fixed internal number can be right for every map size and player count,
  which is why the bound is the operator's. To make the pairing visible
  where it will be seen, the entrypoint must state its effective stop
  timeout — at start, and again on receipt of the stop signal — so a
  grace period set below it turns from a mysterious exit 137 into an
  attributable one.
- **A confirmed clean stop** — the only thing that exits 0 — is defined
  observably: the shutdown sequence was delivered and the game process
  exited **successfully, on its own, within the timeout**. A game process
  the entrypoint had to terminate, or that exited with a failure status on
  the way down (a crash mid-save is still a crash), is unconfirmed. The
  game's own orderly, successful exit after its quit command is the
  strongest completion signal available from outside; demanding deeper
  save-flush evidence would be game-specific and fragile, and miscoding
  clean stops as dirty cries wolf — the failure the exit-code contract
  exists to prevent.
- The shipped **default** for the stop timeout should sit just below the
  recommended grace-period floor (80 seconds under the 90-second
  recommendation — one exact number, so the documented pairing rule cites
  something exact), erring toward the operator who followed the docs: they
  get full save time out of the box. The operator on an unmodified
  10-second `docker stop` loses the save under *any* default — a short
  timeout would merely make the image do the killing instead of the
  runtime — and the image cannot read the runtime's grace period to warn
  in advance, which is exactly why the timeout is printed at start and the
  documentation carries the pairing rule.
- Exit codes are the supervision interface: **0 for a requested stop that
  completed cleanly; non-zero for everything else**, including a stop where
  the save could not be confirmed. A supervisor restarts and alerts on
  failure; miscoding a dirty stop as clean hides exactly the corruption this
  section exists to prevent.

| Event | Required behavior |
|---|---|
| Stop signal, game exits successfully on its own within the stop timeout | Exit 0 — confirmed clean stop |
| Stop signal, game exits on its own but with a failure status | Exit non-zero — the game crashed during its own shutdown; the save is unconfirmed |
| Stop signal, game still running when the stop timeout expires | Terminate the game process; exit non-zero — the save is unconfirmed |
| Game exits by itself, no stop signal received | Propagate the game's exit code verbatim — a crash is non-zero on its own; an operator-initiated quit through the game's own admin channel (`docker exec`) yields whatever the game returns, and the documentation says so |
| Startup validation fails (§5.3, §5.4) | Exit non-zero before the game starts |

### 5.7 Backup knowledge

The image never implements or schedules backup (§11) — but it owns the
knowledge an operator needs to take a **consistent** one, and its
documentation must state the recipe. The danger it must warn against:
copying the state root of a running server produces snapshots that are
silently corrupt — databases and world files caught mid-write restore into
a broken server, discovered only on restore day. The recipe, in order of
preference:

1. the game's **native backup or save-quiescing mechanism**, where one
   exists — stating whether its completion is confirmable, because a save
   command that returns before data is flushed makes a hot copy no better
   than no save at all;
2. otherwise **stop, copy the state root, start** — safe because a clean
   stop (§5.6) guarantees flushed state on disk.

Either way the documentation names what to copy (the §5.1 state root) and
what is pointless to copy (ephemeral paths).

The same section owns the **version-upgrade warning**: moving to an image
with a newer game version may migrate the world irreversibly — the game
decides, not the image — so the documentation must tell operators to take a
backup before crossing game versions, and that the moving tags of §7 cross
them automatically on pull. Silent, discovered late, unrecoverable: the
exact shape of failure this specification exists to prevent.

### 5.8 Image metadata

Images must carry standard OCI annotations: source repository, description,
license (MIT — the repository's license, §9), and — for game images — the
game version and image revision matching the tag (§7), the **Steam buildid
and branch** the game was installed from, and the **builder image
reference** (pinned tag or digest, §3.1) the build used. The buildid label
is the machine-readable side of §8's update comparison: the human version
string in the tag cannot be compared against Steam's metadata reliably, and
buildids change without version changes. Labels are what registries and
scanners read when the tag is no longer at hand.

## 6. Per-game specifications

Each game image carries its own specification: a `SPECIFICATIONS.md` in the
game's directory (`*/SPECIFICATIONS.md` — `project-zomboid/SPECIFICATIONS.md`
for the first game). Per-game specifications are part of this specification:
the same reading contract applies, the same tiers, and §5 binds them in
full — a per-game document adds to the conventions and may deviate from a
"should" with reason, but never weakens a "must".

A per-game specification must cover, at minimum:

- the researched **facts** about the game's dedicated server — install
  source and branches, **where the human-readable version string is read
  from** (game files, distribution metadata, or a build input — it names
  the tags, §7), runtime, state layout, the complete writable-path set
  including what `$HOME` must be (§3.4), configuration behavior including
  whether the game rewrites its own files (§5.3), ports with the
  advertised-or-remappable flag (§5.2), admin/query/save mechanisms,
  **whether the game can run with its query protocol disabled** and what
  the healthcheck does then (§5.5), stop signal behavior (§5.6), and
  **what a game-version upgrade does to existing saves** (§5.7) — dated,
  and re-verified at implementation against the build actually shipped;
- the **environment surface** (§5.3): every variable, its purpose, its
  mandatory-or-optional flag;
- **first boot**: what happens on a fresh state directory, with a decision
  table wherever that branches dangerously;
- **shutdown**: how §5.6 mediation works for this game, and the recommended
  minimum grace period;
- **health**: what the healthcheck probes and how the start period was
  sized;
- **game-managed runtime content** (workshop mods and the like), if any;
- the **backup recipe** of §5.7 for this game.

## 7. Versioning and publication

- All images are published publicly on GHCR under `ghcr.io/<owner>` (§2.6),
  named by plain game name: `steamcmd`, `project-zomboid`.
- **Game images**: every build publishes an immutable
  `<game-version>-rN` tag, `N` starting at 0 and incrementing for each
  rebuild of the same game version — a base refresh, an entrypoint fix, or
  a **game content update whose version string did not change**: Steam
  ships new buildids without version changes, and such an update is a
  revision bump, with the buildid label (§5.8) telling the truth the tag
  cannot. A moving `<game-version>` tag points at that version's latest
  revision; a moving `latest` points at the newest revision of the newest
  game version.
- **Builder image**: date-stamped tags (`YYYYMMDD`, with an ordinal
  suffix — `YYYYMMDD.N` — when the same day sees more than one build, so
  no immutable tag is ever reused) plus a moving `latest` — steamcmd has no
  upstream version to carry (§2.2).
- "Newest game version" for the moving pointers is decided by **publication
  order of new-version builds**, not by parsing version strings — a string
  sort calls 42.9 newer than 42.10, and Steam branches only move forward,
  so the order builds were published in is the order versions arrived in.
- A rebuild at an **unchanged version and unchanged buildid** is a
  legitimate revision bump — that is precisely what base refreshes and
  entrypoint fixes are.
- The tag scheme carries **no branch axis**: every game image is built from
  the one Steam branch its per-game specification declares, and building
  any other branch is out of scope until this section grows a branch
  marker. The reason is the immutability rule below — two branches can
  expose the same version string, and colliding them on one immutable tag
  would republish a tag with different content.
- **A published immutable tag is never reused for different content**, and
  because the registry itself will happily move a tag, this must be
  **enforced loudly at publish time**: a publish that would overwrite an
  existing immutable tag (a lost race between two build triggers, a
  recomputed revision) must fail the job, never proceed — a silently moved
  pinned tag is this project's own flagship failure shape attached to its
  strongest promise. Consumers pin `-rN`, a date tag, or a digest for
  reproducibility; the moving tags are convenience pointers, and every
  image's documentation says exactly that — including that the moving tags
  **cross game versions on pull**, with the save-migration consequence of
  §5.7 — so nobody mistakes `latest` for a stable reference.
- Where a game exposes **no machine-readable version string**, its tags
  fall back to buildid-derived names (the buildid is always machine-
  readable, §2.3) — automation never waits on a human to name a tag — and
  the per-game specification states which naming its tags use.
- Superseded immutable tags are **retained indefinitely, deliberately**:
  §7's promise is that a pinned tag keeps resolving, so no cleanup job may
  delete them. Registry storage for public images is the cheap side of the
  §3.2 trade-off; if that ever changes, retention becomes a decision to
  revisit here, not a job to invent quietly.
- Images are linux/amd64 only (§2.1); tags carry no architecture suffix.

## 8. Build automation

CI on the repository's GitHub project must provide:

- **On-demand builds**: a manually triggered workflow that builds and
  publishes a chosen image — for the builder, a new date tag; for a game,
  the branch its per-game specification declares (§7 — no other branch is
  buildable), whose current content determines the version tag (steamcmd
  installs what a branch holds *now*; arbitrary historical versions would
  need depot-manifest machinery this project does not contemplate), with
  the revision tag computed against what the registry already holds (never
  overwriting, per §7).
- **Scheduled update detection**: a periodic job compares each game's
  current Steam buildid (§2.3) against the buildid label of the newest
  published image (§5.8) and, on **any** buildid change, builds and
  publishes automatically — a changed version string as a new version tag,
  an unchanged one as a revision bump, per §7. Both flow without human
  action, and for the same reason: tags are additive and consumers pin
  (§7), so publishing never deploys anything anywhere; leaving
  same-version content updates unpublished would silently strand servers
  on stale builds instead. A comparison that **cannot be established** —
  Steam unreachable, a newest image without a parseable buildid label —
  must fail the job loudly and is never treated as "no change": a green
  job that has stopped comparing is a detector that silently died, the
  §7-overwrite rule's twin.
- A **scheduled refresh must exist**, as one flow: it publishes a fresh
  builder date tag, **advances the pinned builder reference** the game
  builds use (§3.1 — the pin only moves by this deliberate, automated act,
  which is what makes it a pin rather than a moving pointer in disguise),
  and rebuilds every game image against the refreshed base and builder.
  The pin advance becomes final **only when the game rebuilds succeed** —
  a failed refresh must leave (or restore) the previous working pin, or a
  broken builder blocks every later on-demand build, urgent ones included.
  Each rebuilt image's tag follows §7's mapping like any other build: if
  the branch moved since the last publish, the result is the new version's
  `-r0`; if not, a revision bump. Once games are baked in, this refresh is
  the *only* path by which security patches reach game images — as an
  optional nicety it would be the first thing dropped, leaving
  multi-gigabyte public images unpatched indefinitely. The cadence is the
  implementation's choice; the mechanism is not — and it must survive the
  scheduler's own failure mode (§2.8). The requirement is stated as the
  observable: **a refresh that has not run within its cadence must surface
  as a failing check in a channel that does not share the refresh's own
  scheduler** — once a workflow is disabled, nothing inside it can report
  anything, so the watchdog must live outside the thing it watches (where
  it lives is the implementation's choice). Keeping the scheduler alive
  through repository activity is at most a should on top of that: whether
  workflow-pushed commits reset GitHub's activity clock is not asserted
  here, and a mechanism resting on it would rest on an unverified fact.
- **Superseded game versions are never re-patched**: the refresh rebuilds
  the branch's current content only. A consumer pinned to an older
  version's tag holds exactly what was published — frozen content is what
  pinning means — and moving forward is how they get patches. Stated
  because silence here would read as an oversight rather than a choice.
- **A smoke test gates every game-image publish**: the built image must
  start on the image's **default configuration profile** with only the
  documented mandatory variables supplied, report healthy (§5.5) within a
  **stated bound** (past which the gate fails rather than hangs), stop on
  the stop signal, and exit 0 — asserting exactly the silent-failure path
  of §5.6 before the image reaches anyone. Where a supported alternative
  profile switches the healthcheck onto a different code path (a non-Steam
  mode, for instance), that profile should be exercised too. External
  connectivity (Steam included) is a permitted dependency of the gate —
  the game needed it at build time anyway. The test runs under an
  **arbitrary non-root uid**, with a root filesystem as read-only as the
  image's own documentation claims (§5.1) — writable mounts exactly at the
  documented paths — so the uid-agnostic promise of §3.4 and the
  writable-path claims are exercised on every publish instead of trusted;
  an image whose per-game specification states a reasoned deviation from
  the read-only recommendation is tested against its own documented
  writable set. A build that cannot pass this does not publish.
- Pushes and pull requests that touch an image's sources should get a
  **build-and-smoke-test run without publishing** — otherwise an
  entrypoint regression waits, invisible, until the next publish attempt
  finds it.

## 9. Documentation deliverables

Deliverables of the implementation, named here so they exist; their content
requirements:

- **Per-image README** (also the GHCR page): the environment variable table
  with mandatory/optional flags, ports and their roles with the
  advertised-or-remappable flag (§5.2), writable paths and the state root
  **including the mount-ownership preparation step** (a fresh named volume
  is created root-owned while the container runs under the operator's uid —
  the most common first-contact failure, and the loud fatal of §3.4 needs
  its documented cure), configuration behavior including the rewrite and
  env-override caveats (§5.3), shutdown semantics with the recommended
  grace period and the stop timeout (§5.6), the healthcheck and how to
  probe/save/announce from outside, the backing-up section with the
  version-upgrade warning (§5.7), tag policy (§7), and a minimal
  `docker run` and compose example.
- **Repository README**: project scope, image inventory, and the shared
  conventions of §5 stated once — per-image docs link here rather than
  restating them.
- **A contributor guide for adding a game**: the §5 checklist an implementer
  walks a new game image through, including the per-game specification to
  write first (§6).
- **A LICENSE file at the repository root: MIT.** It licenses the image
  recipes and tooling — the game content inside the images is the
  publishers' and is not relicensed — and it is the value of the §5.8
  license annotation.
- All documentation must stay platform-neutral (§1): interfaces are
  described in Docker-generic terms, never in terms of any particular
  hosting environment.

## 10. Future Considerations

Not built now; nothing in the present design may preclude them.

- **10.1 Wine/Proton image line** for Windows-only Steam servers: a
  parallel builder/runtime base pair reusing the §5 conventions unchanged.
  Deferring is safe because nothing in §3–§5 assumes a native Linux binary —
  the entrypoint adapter pattern absorbs wine as it absorbs a JRE.
- **10.2 arm64 images** where a game has a native arm64 server. steamcmd
  itself is x86-only (§2.1), so this would mean emulation in the build
  stage or upstream arm64 distribution; nothing in the conventions is
  architecture-bound, so the cost does not grow by waiting.
- **10.3 Mod-baked variants**: private derived images with workshop content
  pre-installed, for operators who want reproducible modded startup. The
  tag scheme extends (a suffix) without disturbing §7.
- **10.4 Non-anonymous games**: titles whose server install needs Steam
  credentials. §4.3 already requires the builder to accept credentials
  without persisting them; what remains is CI secret handling, deferred
  until such a game is wanted.
- **10.5 More games**: the point of §5 — each is a new directory, a
  per-game specification (§6), and a small delta.
- **10.6 Non-Steam games** (a Minecraft-class server, for instance). The
  conventions of §5 are acquisition-agnostic — nothing in them assumes
  Steam. What changes per non-Steam game: the build stage (a different
  fetcher than the steamcmd builder), CI's update detection (a per-game
  version source instead of the Steam buildid, §8), the §5.8 buildid and
  branch labels (which generalize to the game's version-source identifier —
  §7's buildid-derived tag fallback already shows the shape), and the
  healthcheck's protocol (§5.5 names the Steam query because every current
  game is a Steam game; the requirement is the game-protocol probe,
  whatever that protocol is). Deferring is safe: a non-Steam game arrives as a new game
  directory with its own builder stage, touching nothing existing.

## 11. Non-Goals

Conscious renunciations, each with its blast radius.

- **No runtime game updates.** A game update requires pulling a new image.
  Blast radius: servers lag behind releases by one rebuild; CI (§8) exists
  to keep that gap short. This is the price of honest tags and reproducible
  deploys, paid deliberately.
- **No orchestration, backup, or instance management.** The images run one
  server each; scheduling, persistence strategy, restore, and fleet concerns
  belong to whatever runs the containers. Blast radius: none for the images;
  operators bring their own.
- **No Project Zomboid Build 41 image.** `legacy41` communities are
  unsupported here. Blast radius: they use the many existing B41 images.
- **No Windows containers.** The future wine line (§10.1) runs Linux
  containers; Windows-native containerization is out entirely.
- **No support for games that require root at runtime** or ship files only
  root can read (§3.4). Such a game is out until fixed upstream.
- **No general-purpose runtime steamcmd image.** The steamcmd image is a
  builder (§4.1); running persistent servers from it directly is unsupported,
  because it would reintroduce everything §3.2 rejects.
