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
  the game's cache-dir option). This is the single state root of root §5.1.
- Server configuration is a per-server-name INI file plus sandbox-settings
  files under that state root. **The game rewrites these files** (adding
  defaults, persisting in-game admin changes) — the root §5.3 rewrite
  warning applies.
- Admin credentials live in the server database, created on first boot.
  With no database and no admin password provided, the server **prompts
  interactively** — in a container, a silent hang.
- Networking: one main **UDP game port (default 16261)** which also answers
  the Steam query protocol, plus a **second UDP port (default 16262)** for
  direct player connections. Both are **advertised** in the root §5.2
  sense (Steam server browser registration), and both are settable in the
  game's configuration. **RCON on TCP (default 27015)**, enabled only when
  an RCON password is configured, freely remappable; RCON provides `save`,
  `quit`, and server messages.
- The server **does not act on SIGTERM natively**: clean shutdown is the
  console/RCON sequence `save` then `quit`. Root §5.6 mediation is
  mandatory, and must work even when the operator configured no RCON
  password.
- The server writes its console output to stdout when run in the
  foreground **and** writes log files under the state root — the root §5.5
  relay is not needed; log-file rotation ownership must still be
  documented.
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
| `ADMIN_PASSWORD` | Admin account password | **Mandatory on first boot** (no server database yet); optional afterwards — see §4 |
| `SERVER_PASSWORD` | Join password | Optional (open server without it) |
| `RCON_PASSWORD` | Enables and protects RCON | Optional (RCON stays off without it) |
| `RCON_PORT` | RCON TCP port | Optional (default 27015) |
| `GAME_PORT` | Main UDP port (game + Steam query) | Optional (default 16261) |
| `DIRECT_PORT` | Second UDP port | Optional (default 16262) |
| `MAX_HEAP` | JVM maximum heap | Optional (documented default), with the §2 warning that it must sit below the container memory limit |

Exact names are a recommended default; whatever ships is what the
documentation states, and per root §5.3 the list does not grow to mirror
game settings — everything else is the INI's job.

## 4. First boot

The dangerous branch is a fresh state directory: the game would prompt for
an admin password and hang. The entrypoint must resolve it before the game
starts:

| Server database exists | `ADMIN_PASSWORD` set | Behavior |
|---|---|---|
| No | No | **Fatal before game start**, message naming the variable — a hang or an adminless public server are both unacceptable |
| No | Yes | Create the admin account via the game's non-interactive mechanism; start |
| Yes | No | Start; credentials already in the database |
| Yes | Yes | Start; apply the password to the existing account if the game supports it non-interactively, otherwise log a clear warning that the value was ignored — the one forbidden outcome is silently diverging env and effective credentials |

## 5. Shutdown

Per root §5.6 and the SIGTERM fact of §2: on the stop signal the entrypoint
runs the game's `save`-then-`quit` sequence through a channel that exists
regardless of operator configuration (the server console; RCON only as an
alternative when configured), waits for the Java process to exit, and exits
0 only on a confirmed clean stop. The image documentation recommends a stop
grace period of at least 90 seconds, and notes that large maps and many
players lengthen saves.

## 6. Health

The HEALTHCHECK queries the Steam query protocol on the game port
(root §5.5). World load on large Build 42 maps takes minutes: the
`start_period` must absorb that so a starting server is not reported
unhealthy, while a loaded-then-hung server is.

## 7. Workshop mods

Supported the way the game does it natively (D-010): the server downloads
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
