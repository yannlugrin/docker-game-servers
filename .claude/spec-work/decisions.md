# Decision log

## Open questions

(none)

---

## D-001 (2026-08-12) — Monorepo for all images

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001); reaffirmed 2026-08-12 (challenge 009)
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
  re-grounded); reaffirmed 2026-08-12 (challenge 009)
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
  when a game updates (D-006); target games fetch their own runtime content
  (workshop mods) or need none — steamcmd's one runtime-relevant feature,
  `workshop_download_item`, matters only for games whose server cannot
  self-download mods, often refuses anonymous login, and would be a
  reasoned per-image deviation if such a game arrives, not a convention
  change (user challenge, 2026-08-12). Corroborating, not load-bearing: the
  hosting platform that motivated the project pins digests and never
  updates in place — the decision holds without it (challenge 001).

## D-003 (2026-08-12) — Game files baked into the image at build time

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001, rationale
  re-grounded); reaffirmed 2026-08-12 (challenge 009)
- **Foundational:** yes
- **Decision:** each game image contains the game server files, installed
  via steamcmd during the image build. The image never downloads the game at
  container start; the only runtime downloads are game-managed content such
  as workshop mods (D-010; PZ specification §7).
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

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001); reaffirmed 2026-08-12 (challenge 009)
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

- **Status:** decided; reaffirmed 2026-08-12 (challenge 001); reaffirmed 2026-08-12 (challenge 009)
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
  Amended per review 002 (F2, F8): a game content update whose version
  string is unchanged (buildid-only) is a `-rN` revision bump, with the
  Steam buildid carried as an image label; a second same-day builder build
  takes an ordinal suffix (`YYYYMMDD.N`). Amended per review 004 (F2):
  "newest version" for moving pointers is publication order of new-version
  builds (no version-string parsing); a rebuild at unchanged
  version+buildid is a legitimate revision bump; the version-string source
  is a required per-game fact. Amended per user final read (2026-08-12):
  the `-rN` counter counts **releases only** — development iterations
  publish under a separate non-release namespace (mutable, prunable,
  promise-free), so a game's first public image is `-r0` regardless of
  development history.
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
- Amended per review 004 (F11): the two *capabilities* (host-side
  serving/player-count probe; exec-based save/announce where the game has
  an admin channel) are the musts; shipping the two specific clients is the
  recommended default (should).
- Amended per challenge 009: the RCON client's strongest current
  justification is its **contingent fallback role** — if console-over-pipe
  fails, stop mediation runs on entrypoint-managed internal RCON (PZ §5),
  and if the query protocol is off or A2S fails to track serving state,
  the healthcheck itself falls back onto that channel (PZ §6) — with
  operator exec convenience secondary. Until PZ open items c/f/i/k/l
  resolve, the image cannot know whether the client is a convenience or
  the backbone of its flagship guarantees; dropping it under §5.5's
  drop-with-reason clause would be wrong exactly in the configurations
  that need it.

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

## D-014 (2026-08-12) — Per-game specifications in the game's directory

- **Status:** decided
- **Foundational:** no
- **Decision:** each game image's specification lives as `SPECIFICATIONS.md`
  in the game's directory (`*/SPECIFICATIONS.md`; the first is
  `project-zomboid/SPECIFICATIONS.md`). The root `SPECIFICATIONS.md` keeps
  the conventions and states (§6) what every per-game document must cover;
  per-game documents inherit the reading contract and may never weaken a
  root "must".
- **Why:** user's ruling at the close of their review round. Structure
  deviation from the single-document doctrine, argued: game sections grow
  with every game while the conventions stay stable, and the game directory
  is where an implementer works on that image. Risk accepted: cross-file
  references need a convention (`root §N` from per-game documents) and the
  consistency pass covers all `*/SPECIFICATIONS.md` files.
- **Premises:** the monorepo has one directory per game image (D-001); the
  conventions (root §5) carry everything game-independent, so per-game
  documents stay small.

## D-015 (2026-08-12) — No default user; the entrypoint refuses uid 0

- **Status:** decided; amended 2026-08-12 (review 006 F5, user ruling);
  reaffirmed 2026-08-12 (challenge 009, as amended)
- **Foundational:** no
- **Decision:** game images declare no default user; the entrypoint exits
  fatally when running as uid 0, with a message naming `--user` / compose
  `user:` — with **one documented opt-out**, `ALLOW_UID0` (`1` or
  case-insensitive `true`; `0`/`false` are an explicit "off"; anything else
  is unparseable and fatal per root §5.3), for rootless and
  user-namespaced runtimes where in-container uid 0 maps to an
  unprivileged host user and is the runtime's default.
- **Why:** the user's ruling on review 004 F12, amended by their ruling on
  review 006 F5. The real ground is forcing the uid choice to be
  deliberate: a container cannot distinguish an operator-chosen uid from
  an image default. A root default plants root-owned files in the volume;
  an image-invented default uid puts numbers nobody chose on the
  operator's disk. On rootless Podman / userns Docker / K8s without
  `runAsUser`, uid 0 is harmless and the default, so a flat refusal made
  the image unbootable on runtimes §1 promises to support — setting the
  opt-out *is* the deliberate choice there. Rejected: non-root default uid
  (the invented-number problem), root default with docs (the trap), and an
  **undocumented or default-on** escape (the cargo-cult risk the original
  entry feared; the shipped opt-out is scoped, documented, and
  strict-parsed instead).
- **Premises:** operators mount owner-only state directories and care about
  file ownership on the host; a loud, explanatory first-run fatal is an
  acceptable cost for a public image (no zero-flag quickstart); rootless
  and user-namespaced runtimes default to in-container uid 0 with no
  host-side root ownership.

## D-016 (2026-08-12) — Non-Steam games are a Future Consideration

- **Status:** decided
- **Foundational:** yes
- **Decision:** games not distributed through Steam (Minecraft-class
  servers) are in the project's future scope: nothing built now, nothing in
  the conventions may assume Steam. Recorded as root §10.6.
- **Why:** user's request (2026-08-12). The §5 conventions are
  acquisition-agnostic already; the Steam-specific pieces are the builder
  tier, CI's buildid-based update detection, and the healthcheck's named
  protocol — each swaps per game without touching the rest. Deferring is
  safe: a non-Steam game arrives as a new game directory with its own
  builder stage.
- **Premises:** the first games are Steam games; §5 names no Steam
  mechanism that §10.6's swap list does not account for (amended per
  challenge 009: the §5.8 buildid/branch label joined the swap list — it
  generalizes to a per-game version-source identifier, as §7's
  buildid-derived tag fallback already shows).
- Reaffirmed 2026-08-12 (challenge 009).
