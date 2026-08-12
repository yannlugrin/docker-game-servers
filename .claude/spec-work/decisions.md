# Decision log

## Open questions

User review round in progress (2026-08-12) — points below are recorded for
batch integration once the user finishes reviewing; do not apply piecemeal.

- Add the steamclient.so fact to the spec (§4 and/or §6.1): many Linux
  dedicated servers dlopen `steamclient.so` via `~/.steam/sdk64/` (or
  `sdk32/`), a path normally provided by a steamcmd installation — baked
  images must ship/symlink these libraries from the builder stage; the
  binary itself is never needed at runtime.
- Rework §5.2 ports (user challenge, accepted in principle): "every port
  must be configurable" is unsatisfiable by an image — configurability is a
  game property. Replace with: (a) must document every port's role, default,
  and whether it is *advertised* (must match the published number — Steam
  browser registration) or freely remappable; (b) advertised ports must be
  settable where the game supports it, else the fixed number and its
  consequence (publish 1:1, one instance per host) are documented as a
  limitation; (c) non-advertised ports need no configurability — Docker
  remapping suffices. Nuance kept: a fixed advertised port breaks
  flexibility (multi-instance, port moves), not single-instance deploys.
- Extend D-002's premises: games can fetch their own runtime content
  (workshop mods) or need none; steamcmd's `workshop_download_item` is the
  one runtime-relevant feature, only for games whose server cannot
  self-download mods, and it often refuses anonymous login — if such a game
  arrives, runtime steamcmd is a reasoned per-image deviation, not a
  convention change.

---

## D-001 (2026-08-12) — Monorepo for all images

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001)
- **Foundational:** yes
- **Decision:** one repository holds the steamcmd base image and every
  per-game image (this repository).
- **Why:** shared conventions and shared CI beat per-image repositories at
  this scale; a game image is mostly convention plus a small delta, and
  keeping them together keeps the conventions enforceable. Per-game
  repositories rejected as overhead with no isolation benefit while a single
  team owns everything.
- **Premises:** a single owner maintains all images; the images share one
  contract, one base and one pipeline; no game image needs a divergent
  release cadence that would fight a monorepo.

## D-002 (2026-08-12) — steamcmd image is a build stage, not a runtime base

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001, rationale
  re-grounded)
- **Foundational:** yes
- **Decision:** the steamcmd base image exists to be used as a multi-stage
  *builder*: it downloads/installs the game at build time. Final game images
  start from a slim runtime base and contain the game files plus runtime
  dependencies only — no steamcmd.
- **Why:** the project goal is the lightest possible images; steamcmd
  (~130 MB with its 32-bit deps and cached runtime) serves no purpose in a
  container whose game is already installed, and removing it shrinks both
  size and attack surface. Keeping steamcmd at runtime was rejected: its only
  benefit is runtime game updates, which the versioning model (game baked in,
  tag = game version, immutable revision tags, §7) deliberately forbids for
  every consumer.
- **Premises:** games are installed at build time (D-003); the versioning
  model forbids in-place updates — consumers needing reproducibility pin
  immutable tags or digests (§7); CI can rebuild on demand or on schedule
  when a game updates (D-006). Corroborating, not load-bearing: the hosting
  platform that motivated the project pins digests and never updates in
  place — the decision holds without it (challenge 001).

## D-003 (2026-08-12) — Game files baked into the image at build time

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001, rationale
  re-grounded)
- **Foundational:** yes
- **Decision:** each game image contains the game server files, installed
  via steamcmd during the image build. The image never downloads the game at
  container start; the only runtime downloads are game-managed content such
  as workshop mods (D-010, §6.6).
- **Why:** an image that installs the game at runtime has a meaningless tag,
  unreproducible content, minutes-long cold starts, and a Steam dependency
  at every deploy — for any consumer. Baked images start in seconds and
  their tags honestly say which game version is inside, which is what lets
  consumers pin by digest and what makes §7 and §8 coherent. Runtime
  installation rejected: it optimizes registry storage, which is cheap, at
  the cost of reproducibility and start latency, which are not.
- **Premises:** target games are installable anonymously via steamcmd
  (Project Zomboid appid 380870 is); registry storage for multi-GB public
  images is acceptable on GHCR; game updates are handled by publishing a new
  tag, not by mutating containers. Corroborating, not load-bearing: the
  hosting platform that motivated the project requires version-carrying tags
  and pins digests — the decision holds without it (challenge 001).

## D-004 (2026-08-12) — Base distribution: debian:trixie-slim

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001)
- **Foundational:** yes
- **Decision:** all images (builder and runtime stages) are based on
  debian:trixie-slim (Debian 13, stable).
- **Why:** steamcmd is a 32-bit glibc binary needing lib32gcc-s1, which
  rules out musl-based Alpine entirely; among glibc options Debian slim is
  the smallest mainstream base (~75 MB), the de-facto standard for steamcmd
  images, and has a long support horizon. Ubuntu 24.04 (Valve's tested
  platform) rejected as slightly larger with no functional gain.
- **Premises:** steamcmd requires glibc + 32-bit compatibility libraries
  (verified 2026-08-12); Debian 13 "trixie" is the current stable; the games
  targeted first run on x86-64 Linux against glibc.

## D-005 (2026-08-12) — Published to GHCR, public

- **Status:** decided
- **Foundational:** no
- **Decision:** images are published publicly on ghcr.io.
- **Why:** free for public images, credential-less pulls, native GitHub
  Actions integration (the repo lives on GitHub and CI is in scope, D-006).
  Docker Hub rejected: anonymous pull-rate limits and a separate CI
  credential for no discoverability need.
- **Premises:** image content is publicly redistributable (steamcmd and
  anonymous-login dedicated server files are distributed freely by Valve /
  the game publishers); the repository is hosted on GitHub.

## D-006 (2026-08-12) — CI build/publish is in scope, on-demand and scheduled

- **Status:** decided
- **Foundational:** no
- **Decision:** the specification covers build automation: images are built
  and published by CI, triggerable on demand, and a scheduled job detects new
  game versions and rebuilds the affected game images.
- **Why:** the versioning discipline (new content, new tag; game baked in)
  makes every game update an image rebuild — holding that by hand invites
  drift. The user explicitly asked for on-demand and/or scheduled rebuilds.
- **Premises:** game updates are observable programmatically (Steam exposes
  buildid per app/branch); GitHub Actions is available to the repository.

## D-007 (2026-08-12) — First game: Project Zomboid, Build 42

- **Status:** decided
- **Foundational:** no
- **Decision:** the first game image is the Project Zomboid dedicated server,
  Build 42 stable line (42.20+).
- **Why:** user's choice; B42 became the stable multiplayer branch on
  2026-07-29, so new servers default to it. Build 41 (legacy41 branch) not
  targeted.
- **Premises:** PZ dedicated server is appid 380870, anonymous install;
  B42.20 stable since 2026-07-29; server bundles its own JRE, uses UDP
  16261/16262, answers Steam query on the game port, supports RCON over TCP,
  writes state under ~/Zomboid.

## D-008 (2026-08-12) — Wine variant deferred

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001)
- **Foundational:** yes
- **Decision:** a wine-based image line for Windows-only Steam servers is a
  Future Consideration: nothing is built now, but the base/game image split
  and the conventions must not preclude adding it.
- **Why:** no Windows-only game is currently targeted; building the wine
  layer now is speculative weight. Deferring is safe because a wine line
  slots in as a parallel builder/runtime base pair reusing the same
  conventions — its later cost does not grow by waiting.
- **Premises:** the first games targeted have native Linux servers; the
  image conventions are game-agnostic rather than Linux-specific in ways
  that would bake out wine.

## D-009 (2026-08-12) — Tag scheme: immutable revisions plus moving pointers

- **Status:** decided
- **Foundational:** no
- **Decision:** game images publish an immutable `<game-version>-rN` tag for
  every build (starting at `-r0`), a moving `<game-version>` tag pointing at
  the latest revision of that version, and a moving `latest`. The steamcmd
  builder image publishes date-stamped tags (`YYYYMMDD`) plus `latest`.
  Published `-rN` and date tags are never reused for different content.
- **Why:** the user wants convenience pointers (`latest`, bare version)
  alongside reproducible references; consumers needing reproducibility pin
  `-rN` or a digest. Bare-version-only (no revision) rejected: rebuilds for
  base updates would either reuse a tag (dishonest) or be impossible to
  express. SemVer-of-the-image rejected: the operator could no longer read
  the game version off the tag.
- **Premises:** consumers that need immutability pin digests or `-rN`;
  Valve does not version steamcmd releases, so date stamps are the only
  honest builder tag.

## D-010 (2026-08-12) — PZ workshop mods: runtime download by the game

- **Status:** decided
- **Foundational:** no
- **Decision:** the Project Zomboid image supports Steam Workshop mods the
  way the game does it natively — the server downloads mods listed in its
  configuration at startup, into its persistent state directory. No mods are
  baked into the image.
- **Why:** mod content is server state, not image content; baking mods would
  make the version tag dishonest and force a rebuild per mod update.
  Mod-baked private variants remain possible later (Future Considerations).
- **Premises:** the PZ server downloads configured workshop mods itself at
  startup; mod files land under its state directory, which is persistent.

## D-011 (2026-08-12) — Secrets: config file authoritative, env optional

- **Status:** decided
- **Foundational:** no
- **Decision:** game images must be fully operable with secrets present only
  in the mounted configuration; env vars are optional overrides the
  entrypoint applies at startup. Documentation marks every variable
  mandatory or optional; mandatory is reserved for values without which the
  game cannot start safely (e.g. PZ first boot with no admin database).
  Where the game permits, injected secrets are not persisted to mounted
  paths.
- **Why:** different deployment environments have different constraints —
  some render secrets into config files, some only pass environment. Env-only
  (rejected) would force every config-rendering deployer to split their
  config; config-only (rejected) would force env-based deployers to write
  secrets to disk themselves.
- **Premises:** both deployment styles exist among target environments; the
  games tolerate startup-time injection of credential settings.

## D-012 (2026-08-12) — Game-level HEALTHCHECK; ship query and RCON clients

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001, rationale
  re-grounded)
- **Foundational:** no
- **Decision:** game images declare a Docker HEALTHCHECK that probes the
  game protocol (Steam query), and ship two minimal clients: a Steam-query
  client (used by the healthcheck and available to operators) and an RCON
  client (operator convenience, and a mediation alternative where RCON is
  configured).
- **Why:** process-alive is the wrong probe for game servers — hung servers
  stay "up"; the user chose a real healthcheck over minimal bytes. The RCON
  client is an operator convenience — save/announce via `docker exec`
  without exposing the RCON port — and a shutdown-mediation *alternative*
  where the operator configured RCON. It is **not** shutdown
  infrastructure: §5.6 requires stop mediation to work without any optional
  configuration, and PZ's RCON only exists when a password is set. (The
  original rationale claimed clean shutdown needed it; corrected by
  challenge 001.) Per §5.5, a game image whose game needs neither client
  may drop them with reason.
- **Premises:** target games answer the Steam query protocol; small static
  clients exist (or are trivially built) so the size cost stays in the
  low megabytes; RCON-style admin protocols are only active when the
  operator configures them.

## D-013 (2026-08-12) — Image naming: plain game name; owner placeholder

- **Status:** decided
- **Foundational:** no
- **Decision:** images are named by plain game name (`steamcmd`,
  `project-zomboid`) under `ghcr.io/<owner>`; the concrete owner is resolved
  at implementation from the repository's GitHub remote.
- **Why:** short and readable; the registry page context disambiguates.
  `-server` suffix and nested namespaces rejected as longer with no real
  ambiguity to solve.
- **Premises:** all published images in this namespace are server images;
  GHCR nests images under the repository owner.

