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
- **per-game runtime images**, one per game, containing the installed game
  and its runtime dependencies — nothing else. The first game is the
  Project Zomboid dedicated server (Build 42).

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
mainstream option and the project's chosen base for every stage.

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
an ordinary process silently ignores it as PID 1. A shell-form entrypoint
makes the shell PID 1, and it neither handles nor forwards the signal. Either
mistake produces the same outcome: the runtime waits out the stop grace
period, then `SIGKILL`s the server mid-write, with nothing in any log. This
is why §5.6 is the strictest section of the conventions.

**2.5 Steam query protocol.** Steam-registered servers answer the A2S query
protocol (serving status, player count) — some on the game port itself,
others on a dedicated query port; which one is a per-game fact that belongs
in the game's port table (§5.2). It is the correct liveness probe either
way: a hung server keeps its process alive but stops answering queries.

**2.6 Registry.** Images are published publicly on GHCR under
`ghcr.io/<owner>` — free for public images, credential-less pulls, native
CI integration. The concrete owner is resolved at implementation time from
the repository's GitHub remote.

**2.7 Dedicated servers load Steam client libraries at runtime.** Many
Linux dedicated servers dlopen `steamclient.so`, typically resolved via
`~/.steam/sdk64/` (or `sdk32/`) — paths a steamcmd installation normally
provides as a side effect. A game image that excludes steamcmd must still
ship or link the Steam client libraries its game loads: images that "work
with steamcmd present, break without it" almost always break on these
libraries, never on the steamcmd binary itself. Discovering this
mid-implementation is the classic first-build failure of baked game images.

## 3. Core model

**3.1 Two tiers, one build direction.** The builder image installs games;
game images contain them. Every game image is produced by a multi-stage
build: the builder stage (from the steamcmd image) downloads the game, and
the final stage starts from the slim runtime base and copies the game in,
adding only that game's runtime dependencies — including the Steam client
libraries the game loads at runtime (§2.7), which the builder stage
provides. steamcmd never appears in a game image — its only runtime use
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

**3.5 The entrypoint is the adapter.** Each game image has a thin entrypoint
owning exactly four jobs: validate the startup state and fail loudly on
anything unsafe (§5.3, §5.4); apply optional environment overrides to the
effective configuration (§5.3); hand PID 1 to — or reliably relay signals
to — the game (§5.6); and mediate shutdown for games that do not handle
their stop signal (§5.6). Everything else — what to configure, when to run —
belongs to the operator.

## 4. The steamcmd builder image

**4.1 Purpose.** The build stage for every game image in this repository,
and usable on its own as a generic "install a Steam app" builder by anyone.
It is not a runtime image and its documentation must say so.

**4.2** It must be based on the project's runtime base (§2.1) and contain a
working steamcmd, already run once at build time so its self-update is
baked into the layer — otherwise every consumer's first build step
re-downloads the steamcmd runtime, paying the cost once per game build
instead of once per base build.

**4.3** It must be able to install a given app id, from a given branch
(including password-protected beta branches) with anonymous login, and
support Steam's file validation. Credentials for non-anonymous apps must be
acceptable via the environment at build time without ever being written to
a layer — not needed for the first games, but the design must not preclude
it (§10.4).

**4.4** It should contain nothing beyond steamcmd's needs (certificates,
32-bit libraries): no editors, no locale packs, no convenience tooling.
Every megabyte here is inherited by every game build's cache.

## 5. Game image conventions

Every game image must satisfy this section. Its per-game section (§6 for
Project Zomboid) adds the game's specifics and documents how each convention
is honored.

### 5.1 Filesystem and state

- The image documents **every path the game persistently writes** — saves,
  worlds, databases, configuration the game rewrites, mod downloads, log
  files that cannot be redirected. Anything outside the documented paths is
  ephemeral by definition, and a save landing outside them is a data-loss
  bug in the image.
- State should be consolidated under a **single documented state root** per
  image where the game allows, so an operator persists one mount instead of
  chasing scattered paths.
- The image must honor `$HOME` when the game derives paths from it, and must
  document whether it does.
- The image should run with a **read-only root filesystem** given writable
  mounts at the documented paths plus `/tmp` — it costs little at build time
  and proves no state hides in undeclared locations.

### 5.2 Ports

Port configurability is a property of the game, not of the image — an image
cannot promise what the game does not offer. The image's obligations are to
document honestly and to expose what the game does offer:

- The image documents **every port**: role, default number, protocol, and —
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
- The image's shipped or effective configuration must make the game listen
  on `0.0.0.0` wherever the bind address is configurable; a game that
  binds narrower and cannot be told otherwise is documented as a
  limitation. Binding narrower breaks port publication for no isolation
  gain inside a private network namespace.
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
  applies them to the effective configuration at startup. When unset, the
  configuration file's values stand. Documentation flags every variable
  **mandatory or optional**; mandatory is reserved for values without which
  the game cannot start safely (each per-game specification shows the
  pattern, §6).
- The image must not invent environment variables for arbitrary game
  settings. The env surface stays small — identity, ports, credentials,
  resource limits — because an unbounded env-to-config mapping is a second
  configuration system to maintain, forever chasing the game's own.
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
- No secret may ever reach stdout, stderr, or a crash dump. Where startup
  logs echo configuration, credential values are redacted.

### 5.5 Observability

- The game's output goes to **stdout/stderr, unfiltered** — the container
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
- Each image declares a **HEALTHCHECK that probes the game protocol**
  (Steam query), not the process: a hung server is alive and
  unhealthy, and process-level checks call it healthy. The check must not
  report healthy while the world is still loading (the `start_period` must
  absorb worst-case load time), and must stop reporting healthy once the
  server is no longer serving — no longer answering queries. A *full*
  server still serves: the predicate is answering, not joinable, or the
  probe flaps exactly when the server is most alive.
- Game images ship two minimal static clients, both documented for operator
  use: a **Steam-query client** (drives the healthcheck; answers "serving?"
  and player count) and an **RCON client** (operator save/announce via
  `docker exec` without exposing the RCON port, and a shutdown-mediation
  *alternative* where RCON is configured — never the mediation the stop
  depends on, per §5.6). Together they add megabytes, not tens of
  megabytes; images whose game needs neither may drop them with reason.

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
  handlers and reliably relays the stop.
- If the game does not act on the stop signal natively, the **entrypoint
  must translate it** into the game's own shutdown mechanism (console
  command, RCON `save`+`quit`, whatever the game provides), then wait for
  the game process to exit. The mediation path must work regardless of
  optional operator configuration — a stop that only works when the operator
  happened to enable RCON is a stop that fails silently on default setups.
- Exit codes are the supervision interface: **0 for a requested stop that
  completed cleanly; non-zero for everything else**, including a stop where
  the save could not be confirmed. A supervisor restarts and alerts on
  failure; miscoding a dirty stop as clean hides exactly the corruption this
  section exists to prevent.

| Event | Required behavior |
|---|---|
| Stop signal, game saves and exits in time | Exit 0 |
| Stop signal, game unresponsive to mediation | Bounded wait, then terminate the game process; exit non-zero — the save is unconfirmed |
| Game crashes or exits by itself | Propagate a non-zero exit |
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

### 5.8 Image metadata

Images carry standard OCI annotations: source repository, description,
license, and — for game images — the game version and image revision
matching the tag (§7), plus the **Steam buildid and branch** the game was
installed from. The buildid label is the machine-readable side of §8's
update comparison: the human version string in the tag cannot be compared
against Steam's metadata reliably, and buildids change without version
changes. Labels are what registries and scanners read when the tag is no
longer at hand.

## 6. Per-game specifications

Each game image carries its own specification: a `SPECIFICATIONS.md` in the
game's directory (`*/SPECIFICATIONS.md` — `project-zomboid/SPECIFICATIONS.md`
for the first game). Per-game specifications are part of this specification:
the same reading contract applies, the same tiers, and §5 binds them in
full — a per-game document adds to the conventions and may deviate from a
"should" with reason, but never weakens a "must".

A per-game specification must cover, at minimum:

- the researched **facts** about the game's dedicated server — install
  source and branches, runtime, state layout, configuration behavior
  including whether the game rewrites its own files (§5.3), ports with the
  advertised-or-remappable flag (§5.2), admin/query/save mechanisms, stop
  signal behavior (§5.6) — dated, and re-verified at implementation against
  the build actually shipped;
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
- **A published immutable tag is never reused for different content.**
  Consumers pin `-rN`, a date tag, or a digest for reproducibility; the
  moving tags are convenience pointers, and every image's documentation says
  exactly that, so nobody mistakes `latest` for a stable reference.
- Images are linux/amd64 only (§2.1); tags carry no architecture suffix.

## 8. Build automation

CI on the repository's GitHub project must provide:

- **On-demand builds**: a manually triggered workflow that builds and
  publishes a chosen image — for the builder, a new date tag; for a game, a
  chosen branch, whose current content determines the version tag (steamcmd
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
  on stale builds instead.
- Game images should also be rebuilt (revision bump) when the base or the
  builder image materially changes — security patches reach game images no
  other way once games are baked in. A scheduled base refresh should exist
  for the same reason.
- **A smoke test gates every game-image publish**: the built image must
  start with a minimal configuration, report healthy (§5.5), stop on the
  stop signal, and exit 0 — asserting exactly the silent-failure path of
  §5.6 before the image reaches anyone. A build that cannot pass this does
  not publish.

## 9. Documentation deliverables

Deliverables of the implementation, named here so they exist; their content
requirements:

- **Per-image README** (also the GHCR page): the environment variable table
  with mandatory/optional flags, ports and their roles with the
  advertised-or-remappable flag (§5.2), writable paths and the state root,
  configuration behavior including the rewrite caveat (§5.3), shutdown
  semantics with the recommended grace period, the healthcheck and how to
  probe/save/announce from outside, the backing-up section (§5.7), tag
  policy (§7), and a minimal `docker run` and compose example.
- **Repository README**: project scope, image inventory, and the shared
  conventions of §5 stated once — per-image docs link here rather than
  restating them.
- **A contributor guide for adding a game**: the §5 checklist an implementer
  walks a new game image through, including the per-game specification to
  write first (§6).
- All documentation stays platform-neutral (§1): interfaces are described in
  Docker-generic terms, never in terms of any particular hosting
  environment.

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
- **10.5 More games**: the point of §5 — each is a new directory, a §6-style
  section, and a small delta.

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
