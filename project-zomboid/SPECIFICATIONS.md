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
unchanged. The complete writable-path set (root §3.4) is: the state root,
`/tmp`, and `$HOME` — which the image sets itself to a writable documented
location (inside the state root or a dedicated mount), because the
Steam client link farm and JVM crash dumps may land under it (§2, open
item f); nothing else may need write access, verified at implementation.

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
  (root §5.4 pattern); (e) where the **human-readable version string** is
  authoritatively read from — the game's own files, Steam metadata, or a
  build input — since it names the image tags (root §7); (f) how a
  **non-Steam configuration** is detected from the effective settings, and
  whether the server writes into a `$HOME`-derived path (`~/.steam` link
  farm, JVM crash dumps) at runtime — it completes the writable-path set
  (root §3.4); (g) **where the server actually writes downloaded workshop
  mods** — community reports disagree between the cache directory and a
  `steamapps/workshop` tree, and if the target turns out to be the shipped
  game directory, it collides with the world-readable-not-writable content
  rule (root §3.4) and the read-only rootfs (§1), so the answer reshapes
  §7; (h) **what the server does when a workshop download fails** at
  startup (no connectivity, delisted item, partial download) — whether it
  refuses to start, starts without the mod, or hangs.
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
| `STOP_TIMEOUT` | Entrypoint's bounded wait for the game to exit after `save`+`quit` (root §5.6) | Optional (documented default; docs state it must sit below the runtime's stop grace period) |

Exact names are a recommended default; whatever ships is what the
documentation states, and per root §5.3 the list does not grow to mirror
game settings — everything else is the INI's job.

One consequence of the game's own behavior, stated plainly (root §5.4's
non-persistence "should" cannot be honored here): the game reads its INI
from inside the state root and rewrites it, and offers no ephemeral-copy
option — so credentials applied from the environment **persist into the
mounted INI**, and from there into whatever backups the operator takes.
The image documentation says so.

The heap deserves its own guard, because the failure it prevents is the
most silent in this document: a kernel OOM kill has no log line, lands
mid-write, and a restart policy hides it. The entrypoint must read the
container memory limit where the cgroup exposes one and **fail loudly
before the game starts** when the effective maximum heap is not below it
(leaving headroom for the JVM's non-heap memory); where no limit is
readable, it proceeds, and the documentation states what the default heap
assumes of the container.

## 4. First boot

The dangerous branch is a fresh state directory: the game would prompt for
an admin password and hang. The entrypoint must resolve it before the game
starts. "Server database exists" is evaluated **against the effective
`SERVER_NAME`** — config, saves and database are all per-server-name, so
changing `SERVER_NAME` on a populated state root is a first boot for that
name and follows the same rows (an implementer testing "any database in the
state root" reproduces exactly the hang this table exists to prevent):

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
regardless of operator configuration, waits up to `STOP_TIMEOUT` (§3) for
the Java process to exit on its own — root §5.6's definition of a confirmed
clean stop — and exits 0 only then. The expected channel is the
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
verification confirms (expected: the main game port), always against the
**effective** port configuration (root §5.5). If verification resolves
unfavorably, the fallback order is: the legacy Steam ports if they turn out
to hold live query listeners (§2); otherwise the best available game-level
signal (the internal mediation channel of §5, or a log-line readiness
match), documented as a reasoned deviation per root §5.5 — a process-level
check is never the answer.

A **non-Steam configuration is supported**: the game can run with Steam
integration disabled, which silences the query protocol entirely. The
healthcheck must detect that from the effective configuration (§2, open
item f) and switch to the same fallback order automatically — a healthy
non-Steam server reported permanently unhealthy would make the probe
worthless exactly for the operators who deviate.

World load on large Build 42 maps takes minutes: the `start_period` must
absorb that so a starting server is not reported unhealthy, while a
loaded-then-hung server is. The trade-off is accepted deliberately
(root §5.5): a `start_period` sized for worst-case first-boot world
generation blinds hang detection for that duration on every later restart;
the image documents its chosen value and this reasoning.

Both static clients of root §5.5 ship: the query client drives the
healthcheck and serves operators; the RCON client is useful to operators
only when operator RCON is enabled (§3) — stop mediation does not depend on
it (§5).

## 7. Workshop mods

Supported the way the game does it natively: the server downloads
the mods listed in its configuration at startup into its mod directory
(location: open item g of §2), where they persist. The image neither bakes
mods nor manages them; documentation must state this, including the
consequence that first start after adding mods is slow and needs Steam
connectivity — and, once open item h of §2 is settled, **what the game
does when a mod download fails** and how the operator notices, because a
map-mod world loaded without its mod can regenerate or discard cells: a
data-loss failure the operator must be able to see coming. The image
cannot intercept a download the game performs itself; owning the knowledge
and stating it is the obligation.

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
  stop / copy / start (root §5.7), and the docs say so plainly;
- that the image **leaves the native backup settings at the game's
  defaults** — the INI is the operator's interface (root §5.3) — and the
  documentation states what those defaults are and how to cap archive
  count and frequency, because unbounded archives inside the state root
  are the slow silent disk-filler of root §5.5;
- the **version-upgrade warning** of root §5.7: a newer game version may
  migrate the world irreversibly, the moving tags cross versions on pull,
  and the game's backup-on-version-change setting softens but does not
  replace a deliberate pre-upgrade backup.
