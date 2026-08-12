# Project Zomboid Image — Specification

Per-game specification under §6 of the repository-root `SPECIFICATIONS.md`.
The root document's reading contract and tiers apply unchanged; the
conventions of root §5 bind this image in full. References written `§N`
point to this document; references written `root §N` point to the root
document.

## 1. Scope

The image contains the Project Zomboid dedicated server, Build 42 stable
line, installed at build time (root §3.2). One container, one server
instance.

The image pins the game's state root to a **fixed, documented absolute
path**, using the game's cache-dir option, independent of `$HOME`. The
reason: under root §3.4 the container may run as a uid with no passwd entry
and no usable `$HOME`, exactly where Java's home-directory resolution is
fragile — a `$HOME`-derived state root would move or silently land
somewhere unmounted in that case, while a fixed path gives operators one
stable mount point. The concrete path is the implementation's choice and
becomes a documented fact of the image. A missing or unwritable state root
is a loud fatal before the game starts, never a fallback path.

The read-only-root-filesystem recommendation of root §5.1 applies
unchanged: all writes are expected to land in the state root and `/tmp`,
verified at implementation.

## 2. Facts about the PZ dedicated server

Verified 2026-08-12; the implementation must re-verify against the build it
ships, and any correction lands in the image documentation.

- Steam app id **380870**, anonymous install. **Build 42 is the stable
  branch since 2026-07-29 (version 42.20)**, multiplayer included; Build 41
  survives as the `legacy41` beta branch and is out of scope (root §11).
- The server is Java-based and **ships its own JRE** — the image needs no
  system Java. Its maximum heap is set through its launch configuration and
  must stay below the container memory limit: a heap equal to the limit
  makes the kernel OOM-kill the server at exactly the allocation the GC
  would have recovered.
- Whether the server loads `steamclient.so` via the `~/.steam` link farm
  (root §2.7) or from its own shipped directories is to be verified at
  implementation; either way the libraries ship with the image.
- All persistent state — saves, the server's SQLite databases (including
  admin accounts), configuration, logs, downloaded workshop mods — lives
  under one game-managed directory (`~/Zomboid` by default; relocatable via
  the game's cache-dir option, which is how the image pins it, §1). This is
  the single state root of root §5.1.
- Server configuration is a per-server-name INI file plus sandbox-settings
  files under that state root. **The game rewrites these files** (adding
  defaults, persisting in-game admin changes) — the root §5.3 rewrite
  warning applies.
- Admin credentials live in the server database, created on first boot.
  With no database and no admin password provided, the server **prompts
  interactively** — in a container, a silent hang.
- Networking: one main **UDP game port (default 16261)**, plus a **second
  UDP port (default 16262)** for direct player connections. Both are
  **advertised** in the root §5.2 sense (Steam server browser
  registration), and both are settable in the game's configuration.
  **RCON on TCP (default 27015)**, enabled only when an RCON password is
  configured, freely remappable; RCON provides `save`, `quit`, and server
  messages.
- **Open port facts, to settle before the port table and healthcheck are
  final** (community documentation says both resolve favorably, but it is
  not authoritative): (a) whether the Steam query protocol is answered on
  the main game port, as reported for current builds — the healthcheck
  target (§6) and the `GAME_PORT` description (§3) inherit the answer;
  (b) whether the legacy `SteamPort1`/`SteamPort2` settings (defaults
  8766/8767 UDP) still open listeners on Build 42 — reported unnecessary
  on modern builds, but if present they belong in the port table
  (root §5.2 documents *every* port); (c) whether the server console
  accepts `save`/`quit` over a non-interactive stdin pipe (no TTY) — the
  shutdown mediation of §5 rests on it, and a Java console that works at a
  terminal can still refuse a pipe; (d) whether the game supports a
  **non-interactive admin password change** on an existing account — it
  decides whether the `ADMIN_PASSWORD` override of §3 is offered at all
  (root §5.4 pattern).
- The server **does not act on SIGTERM natively**: clean shutdown is the
  console/RCON sequence `save` then `quit`. Root §5.6 mediation is
  mandatory, and must work even when the operator configured no RCON
  password.
- The server writes its console output to stdout when run in the
  foreground **and** writes log files under the state root — the root §5.5
  relay is not needed; log-file rotation ownership must still be
  documented.
- Whether the server **echoes credential values** (join, RCON or admin
  password) into its startup console output is to be verified at
  implementation: it decides whether the entrypoint may hand the game
  straight to stdout or must interpose the root §5.4 redaction.
- The game has a **native backup feature**: INI settings for backups on
  start, periodically, and on version change, written as archives inside
  the state root. To verify at implementation, like every fact above.

## 3. Environment surface

The image honors every convention of root §5. The environment surface
should be:

| Variable | Purpose | Mandatory? |
|---|---|---|
| `SERVER_NAME` | Server identity; selects the config/save set under the state root | Optional (game default: `servertest`) |
| `ADMIN_USERNAME` | Admin account created on first boot | Optional (default `admin`) |
| `INITIAL_ADMIN_PASSWORD` | Admin password consumed at account creation (first boot); ignored by definition once the database exists (root §5.4 pattern) | **Mandatory on first boot** unless `ADMIN_PASSWORD` is set — see §4 |
| `ADMIN_PASSWORD` | Declarative admin-password override, applied at every start; offered **only if** the game supports non-interactive password changes (open item, §2) — set on an image that cannot honor it, it is a fatal start (root §5.4) | Optional |
| `SERVER_PASSWORD` | Join password | Optional (open server without it) |
| `RCON_PASSWORD` | Enables and protects operator RCON | Optional (operator RCON stays off without it; the entrypoint may still run an internal, unpublished RCON for stop mediation — §5) |
| `RCON_PORT` | RCON TCP port | Optional (default 27015) |
| `GAME_PORT` | Main UDP port (game traffic; expected to answer Steam query too — open item, §2) | Optional (default 16261) |
| `DIRECT_PORT` | Second UDP port | Optional (default 16262) |
| `MAX_HEAP` | JVM maximum heap | Optional (documented default), with the §2 warning that it must sit below the container memory limit |

Exact names are a recommended default; whatever ships is what the
documentation states, and per root §5.3 the list does not grow to mirror
game settings — everything else is the INI's job.

One consequence of the game's own behavior, stated plainly (root §5.4's
non-persistence "should" cannot be honored here): the game reads its INI
from inside the state root and rewrites it, and offers no ephemeral-copy
option — so credentials applied from the environment **persist into the
mounted INI**, and from there into whatever backups the operator takes.
The image documentation says so.

## 4. First boot

The dangerous branch is a fresh state directory: the game would prompt for
an admin password and hang. The entrypoint must resolve it before the game
starts:

| Server database exists | Credential variables | Behavior |
|---|---|---|
| No | Neither set | **Fatal before game start**, message naming both variables — a hang or an adminless public server are both unacceptable |
| No | Either set | Create the admin account via the game's non-interactive mechanism (`ADMIN_PASSWORD` wins if both are set — it states desired state); start |
| Yes | Only `INITIAL_ADMIN_PASSWORD` set | Start; the variable is ignored **by definition** — first-start-only is its documented contract (root §5.4), so no warning is owed. Leaving it set forever is the normal deployment |
| Yes | `ADMIN_PASSWORD` set, game supports non-interactive change | Start; **the environment wins**: apply at every start. Consequence, documented prominently: an admin password changed in game reverts on the next restart — this credential is managed via the environment *or* in game, never both (the root §5.3 rewrite rule, applied to a credential) |
| Yes | `ADMIN_PASSWORD` set, game does not support it | **Fatal before game start** (root §5.4): the image cannot honor the override contract; the message directs the operator to `INITIAL_ADMIN_PASSWORD`. Safe to be fatal because the docs never offer `ADMIN_PASSWORD` on such an image — only an explicit misconfiguration hits this row |

## 5. Shutdown

Per root §5.6 and the SIGTERM fact of §2: on the stop signal the entrypoint
runs the game's `save`-then-`quit` sequence through a channel that exists
regardless of operator configuration, waits for the Java process to exit,
and exits 0 only on a confirmed clean stop. The expected channel is the
server console over stdin — an open item of §2. If verification finds the
console unusable from a pipe, the sanctioned fallback is an
**entrypoint-managed internal RCON**: the entrypoint generates an ephemeral
password and enables RCON itself, solely for mediation — safe because an
unpublished container port is unreachable from outside, and independent of
operator configuration because the entrypoint owns it (this is distinct
from *operator* RCON, §3). The image documentation recommends a stop grace
period of at least 90 seconds, and notes that large maps and many players
lengthen saves.

## 6. Health

The HEALTHCHECK queries the Steam query protocol on the port the §2
verification confirms (expected: the main game port). If verification
resolves unfavorably, the fallback order is: the legacy Steam ports if they
turn out to hold live query listeners (§2); otherwise the best available
game-level signal (the internal mediation channel of §5, or a log-line
readiness match), documented as a reasoned deviation per root §5.5 — a
process-level check is never the answer. World load on large Build 42 maps
takes minutes: the `start_period` must absorb that so a starting server is
not reported unhealthy, while a loaded-then-hung server is.

Both static clients of root §5.5 ship: the query client drives the
healthcheck and serves operators; the RCON client is useful to operators
only when operator RCON is enabled (§3) — stop mediation does not depend on
it (§5).

## 7. Workshop mods

Supported the way the game does it natively: the server downloads
the mods listed in its configuration at startup into the state root, where
they persist. The image neither bakes mods nor manages them; documentation
states this, including the consequence that first start after adding mods
is slow and needs Steam connectivity.

## 8. Backup recipe

Per root §5.7, the image documentation must state:

- what to copy: the state root (§2) — it holds saves, databases,
  configuration and mods together;
- the preferred consistent path: the game's **native backup settings**
  (§2), whose archives land inside the state root — so an operator copying
  the state root gets them for free, and must cap their count to bound
  disk growth;
- that RCON `save` quiesces to a point but its completion confirmation
  must be verified at implementation before documenting hot copies as
  safe — if it cannot be confirmed, the documented safe procedure is
  stop / copy / start (root §5.7), and the docs say so plainly.
