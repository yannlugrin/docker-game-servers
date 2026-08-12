# Decision log

## Open questions

(none)

---

## D-001 (2026-08-12) — Monorepo for all images

- **Status:** decided
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

- **Status:** decided
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
  tag = game version, digest pinned) deliberately forbids.
- **Premises:** games are installed at build time (D-003); the deployment
  platform pins digests and never updates in place; CI can rebuild on demand
  or on schedule when a game updates (D-006).

## D-003 (2026-08-12) — Game files baked into the image at build time

- **Status:** decided
- **Foundational:** yes
- **Decision:** each game image contains the game server files, installed
  via steamcmd during the image build. Nothing is downloaded at container
  start.
- **Why:** the target platform's contract requires the tag to say which game
  version is inside and pins images by digest — an image that installs at
  runtime has a meaningless tag and unreproducible content. Baked images also
  start in seconds instead of minutes and need no Steam connectivity at run
  time. Runtime installation rejected: it optimizes registry storage, which
  is cheap, at the cost of reproducibility and start latency, which are not.
- **Premises:** target games are installable anonymously via steamcmd
  (Project Zomboid appid 380870 is); registry storage for multi-GB public
  images is acceptable on GHCR; game updates are handled by publishing a new
  tag, not by mutating containers.

## D-004 (2026-08-12) — Base distribution: debian:trixie-slim

- **Status:** decided
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

- **Status:** decided
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
