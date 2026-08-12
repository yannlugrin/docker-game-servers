# Project Zomboid Image — Specification

Per-game specification under §6 of the repository-root `SPECIFICATIONS.md`.
The root document's reading contract and tiers apply unchanged; the
conventions of root §5 bind this image in full. References written `§N`
point to this document; references written `root §N` point to the root
document.

## 1. Scope

The image contains the Project Zomboid dedicated server, Build 42 stable
line, installed at build time (root §3.2). One container, one server
instance. **Build 41 is a non-goal**: `legacy41` communities are
unsupported by this image — blast radius: they use the many existing B41
images.

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
unchanged. The complete writable-path set (root §3.4) is: the state root
and `/tmp` — the image sets `$HOME` itself to a documented location
**inside the state root**, unconditionally: an operator-provided `HOME`
value is overridden, and the documentation says so (root §5.1's one-rule
requirement) — honoring an inherited `HOME` under `--read-only` would
point the Steam link farm and crash dumps at a read-only path, a server
that runs but never registers (§2, open item o). Two writable targets keep
`--read-only` simple; the accepted consequence, stated in the docs, is
that home-directory residue (crash dumps included — root §5.4's warning
applies) travels into every backup of the state root. Nothing else may
need write access, verified at implementation.

## 2. Facts about the PZ dedicated server

Verified 2026-08-12; the implementation must re-verify against the build it
ships, and any correction lands in the image documentation.

- Steam app id **380870**, anonymous install. **Build 42 is the stable
  branch since 2026-07-29 (version 42.20)**, multiplayer included; Build 41
  survives as the `legacy41` beta branch and is out of scope (§1).
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
  interactively** — in a container, a silent hang. The game's launch
  arguments include a **non-interactive account-creation path**
  (admin username/password passed at startup) — this is the mechanism §4
  rests on, verified at implementation like every fact here; the
  entrypoint must never hand over to a game that may prompt, so if the
  mechanism turns out absent the fallback is a fatal, not the hang.
- Whether Build 42 is the default (stable) Steam branch was verified
  2026-08-12 against the developer's own announcement and several
  independent outlets; the branch the image builds is the per-game
  declaration root §7 requires.
- Networking: one main **UDP game port (default 16261)**, plus a **second
  UDP port (default 16262)** for direct player connections. Both are
  **advertised** in the root §5.2 sense (Steam server browser
  registration), and both are settable in the game's configuration.
  **RCON on TCP (default 27015)**, enabled only when an RCON password is
  configured, freely remappable; RCON provides `save`, `quit`, and server
  messages.
- **Open facts, to settle at implementation.** Each carries the section it
  feeds and, where the answer could resolve unfavorably, the pre-committed
  response — no open item may strand the implementation:
  - (a) whether the Steam query protocol is answered on the **main game
    port**, as community documentation reports — the healthcheck target
    (§6) and the `GAME_PORT` description (§3) inherit the answer;
  - (b) whether the legacy `SteamPort1`/`SteamPort2` settings (defaults
    8766/8767 UDP) still open listeners on Build 42 — reported unnecessary
    on modern builds, but if present they belong in the port table
    (root §5.2 documents *every* port);
  - (c) whether the server console accepts `save`/`quit` over a
    **non-interactive stdin pipe** (no TTY) — §5's mediation rests on it,
    and a Java console that works at a terminal can still refuse a pipe;
    unfavorable → the internal-RCON fallback of §5;
  - (d) whether the game supports a **non-interactive admin password
    change** on an existing account — it decides whether the
    `ADMIN_PASSWORD` override of §3 is offered at all (root §5.4 pattern);
  - (e) where the **human-readable version string** is authoritatively
    read from — game files, Steam metadata, or a build input — it names
    the image tags (root §7); unfavorable → PZ tags are buildid-derived
    per root §7's fallback, and this document is updated to say so;
  - (f) how a **non-Steam configuration** is detected from the effective
    settings; unfavorable → a documented image-behavior variable selects
    the probe mode (root §5.3's behavior-knob category, not a
    game-settings mirror);
  - (g) **where the server writes downloaded workshop mods** — community
    reports disagree between the cache directory and a `steamapps/workshop`
    tree; if the target is the shipped game directory it collides with
    root §3.4 and the read-only rootfs (§1) — §7 fixes the required
    response;
  - (h) **what the server does when a workshop download fails** at startup
    (no connectivity, delisted item, partial download) — refuses to start,
    starts without the mod, or hangs — §7 carries the documentation
    consequence;
  - (i) whether the mediation channel can answer a **status and
    player-count query non-destructively** (RCON has a player-listing
    command; the console is write-only) — load-bearing for root §5.5's
    probe capability when the query protocol is off (§6); unfavorable →
    liveness rides on the channel's request/response handshake and the
    player count is documented as unavailable in that configuration
    (root §5.5's "where the game's interfaces expose it" scoping — a
    stated limitation, never a silent zero);
  - (j) whether the server **rotates or caps its own log files** under the
    state root — the input root §5.5's rotation-ownership documentation
    needs;
  - (k) whether the A2S answer **tracks serving state at both ends** —
    measured against a server still loading its world (the probe must not
    answer yet) and against an artificially hung one (the answer must
    stop; a Steamworks responder living outside the game's main loop
    could keep answering) — the entire healthcheck premise; unfavorable →
    absorbed by §6's fallback order;
  - (l) whether the game's RCON offers a **bind-address setting** — the §5
    internal-RCON fallback requires loopback; if the game cannot bind
    loopback and the console is also unusable (item c), there is no safe
    mediation channel and the image **must not ship on that combination**
    — a wide ephemeral admin listener is not an acceptable substitute —
    and the same must-not-ship rule applies when it is the *healthcheck*
    that requires the RCON channel (items a/b/f/k resolving onto §6's
    fallback) and loopback is unavailable;
  - (m) **what a Build 42 point release does to an existing world** —
    migrate, invalidate, or regenerate — the researched answer behind §8's
    upgrade warning (root §6 requires the fact, not just the warning);
    research inconclusive → the documented answer is "unknown — assume
    irreversible; back up before any version change";
  - (n) whether the game's **player-facing UDP listeners bind `0.0.0.0`**
    by default or can be told to — the deterministic input for
    root §5.2's player-port rule;
  - (o) whether the `$HOME` override fully controls the game's idea of
    home: it covers native/`steamclient.so` paths, but the JVM resolves
    `user.home` from the passwd database first where the uid resolves, so
    JVM-side paths (crash dumps) are verified separately (§1).
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
| `RCON_PASSWORD` | Enables and protects operator RCON | Optional (operator RCON stays off without it; the entrypoint may still run an internal, loopback-bound RCON for stop mediation — §5) |
| `RCON_PORT` | RCON TCP port | Optional (default 27015) |
| `GAME_PORT` | Main UDP port (game traffic; expected to answer Steam query too — open item, §2) | Optional (default 16261) |
| `DIRECT_PORT` | Second UDP port | Optional (default 16262) |
| `MAX_HEAP` | JVM maximum heap | Optional (documented default), with the §2 warning that it must sit below the container memory limit |
| `STOP_TIMEOUT` | Entrypoint's bounded wait for the game to exit after `save`+`quit` (root §5.6) | Optional (default 80s per root §5.6, just under the recommended 90s grace floor; docs state it must sit below the runtime's stop grace period) |
| `ALLOW_UID0` | Skips the uid-0 fatal on rootless/user-namespaced runtimes (root §3.4); accepts `1` or case-insensitive `true` | Optional (unset = uid 0 refused) |

Exact names are a recommended default; whatever ships is what the
documentation states, and per root §5.3 the list does not grow to mirror
game settings — everything else is the INI's job.

Per root §5.3, every override is effective **on the very first start of a
fresh state root**, before the game has authored its INI — the game port
is advertised, and a first run on generated defaults would register with
Steam on the wrong number and then silently change on restart. The
mechanism (the game's launch arguments, a pre-written INI, or a
combination) is the implementation's choice, verified against the game's
actual behavior.

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
before the game starts** when the effective maximum heap plus a
**documented, deterministic non-heap allowance** exceeds the limit — the
must is that the allowance is a number two implementations compute
identically, never an adjective; the value itself is a recommended
default (the larger of 512 MB or 25% of the heap). "Unlimited" reads
differently per cgroup version and both readings count as **no limit**:
cgroup v1 reports a near-maximum number, cgroup v2 (the Debian 13 default)
reports the literal string `max` — a non-numeric read is "no limit",
never a parse error. Where no limit is readable, the game starts, and the
documentation states what the default heap assumes of the container.

## 4. First boot

The dangerous branch is a fresh state directory: the game would prompt for
an admin password and hang. The entrypoint must resolve it before the game
starts. Two rules precede the table:

- On an image where the game cannot honor the override (§2, open item d),
  a set `ADMIN_PASSWORD` is **fatal regardless of anything else** —
  validation runs before the rows, so no path exists where an unsupported
  override works on first boot and then kills the next restart.
- The table keys on **"an admin account exists for the effective
  `SERVER_NAME` and `ADMIN_USERNAME`"** where the game makes that
  observable — never on the mere existence of files: config, saves and
  database are all per-server-name, so changing `SERVER_NAME` on a
  populated state root is a first boot for that name; and an interrupted
  first boot (OOM kill, a `^C`) can leave a database with no admin
  account, which a file-keyed entrypoint would misread as "handled" and
  start the adminless public server row 1 calls unacceptable. The proxy is
  asymmetric, and the asymmetry is usable: a **missing** per-`SERVER_NAME`
  database proves the account absent (row 1's fatal may key on it, no
  database tooling required); a **present** one proves nothing. Where
  account existence is not observable behind a present database, creation
  is **idempotent instead**:
  whenever a credential is supplied and the named account is absent,
  create it — which also defines the behavior when an operator changes
  `ADMIN_USERNAME` on a populated state root.

| Admin account exists | Credential variables | Behavior |
|---|---|---|
| No | Neither set | **Fatal before game start**, message naming both variables — a hang or an adminless public server are both unacceptable |
| No | Either set | Create the admin account via the game's non-interactive mechanism (`ADMIN_PASSWORD` wins if both are set — it states desired state); start |
| Yes | Neither set | Start normally — the steady state of every configured server |
| Yes | Only `INITIAL_ADMIN_PASSWORD` set | Start; the variable is ignored **by definition** — first-start-only is its documented contract (root §5.4), so no warning is owed. Leaving it set forever is the normal deployment |
| Yes | `ADMIN_PASSWORD` set | Start; **the environment wins**: apply at every start (the pre-table rule already made an unsupported override fatal, so this row only exists where the game supports it). Consequence, documented prominently: an admin password changed in game reverts on the next restart — this credential is managed via the environment *or* in game, never both (the root §5.3 rewrite rule, applied to a credential) |

## 5. Shutdown

Per root §5.6 and the SIGTERM fact of §2: on the stop signal the entrypoint
runs the game's `save`-then-`quit` sequence through a channel that exists
regardless of operator configuration, waits up to `STOP_TIMEOUT` (§3) for
the Java process to exit successfully on its own — root §5.6's confirmed
clean stop, the only thing that exits 0. A stop signal arriving **while
the world is still loading**
follows the same rules and lands, deliberately, on the timeout row's
non-zero exit: terminating mid-generation leaves state as unconfirmed as
terminating mid-save, and a "fast clean abort" that guesses otherwise
would code the guess as truth. The expected channel is the
server console over stdin — an open item of §2. If verification finds the
console unusable from a pipe, the sanctioned fallback is an
**entrypoint-managed internal RCON**, under four constraints. When the
operator has configured RCON — by §3's variables **or directly in the
INI**, which counts equally — the entrypoint must **reuse it**, never run
a second listener or overwrite the operator's password; it discovers
INI-configured RCON from the effective INI it already manages (the same
file it applies overrides to), so configuration-file-only deployments are
never blind to mediation. When it
enables RCON itself, the listener binds **loopback only** — "unpublished
port" is no protection under host networking or a shared network
namespace — with an ephemeral generated password carrying enough entropy
that brute force over loopback is impractical (a shared network namespace
puts other containers on that loopback), which must not persist
into any backed-up file beyond what the game's own INI rewriting forces,
and the listener appears in the image's **port table** as an admin
interface with its bind address, like every other port (root §5.2). The
image documentation recommends a stop grace period of at least 90
seconds, and notes that large maps and many players lengthen saves.

**The mediation channel is also the operator's** (root §5.5's exec
capability): the image must give the operator a documented `docker exec`
path to save and announce that works **regardless of `RCON_PASSWORD`** —
the entrypoint demonstrably owns a working channel, and an operator on a
default deployment is entitled to the same one. Operator RCON over the
network remains what `RCON_PASSWORD` enables — and setting it **is** the
deliberate choice of root §5.2 that opens a network listener: the
variable exists for remote administration, so it binds wide when set
(documented with the never-expose-publicly warning), while the
entrypoint's own internal RCON stays loopback-bound (§2, open item l).
The exec path exists either way.

## 6. Health

The HEALTHCHECK queries the Steam query protocol on the port the §2
verification confirms (expected: the main game port), always against the
**effective** port configuration (root §5.5). If verification resolves
unfavorably, the fallback order is: the legacy Steam ports if they turn
out to hold live query listeners (§2); otherwise a **request/response
channel** — which means the internal RCON of §5 becomes mandatory in that
configuration, because the console is write-only and cannot answer a
probe (§2, open item i). The liveness predicate must be one that **can go
false on a hung server**, which is why a log-line match may serve only as
the *readiness* signal (world loaded), never as liveness: a matched line
stays matched forever, exactly the latch root §5.5 forbids. A
process-level check is never the answer.

A **non-Steam configuration is supported**: the game can run with Steam
integration disabled, which silences the query protocol entirely. The
healthcheck must detect that from the effective configuration (§2, open
item f) and switch to the same fallback order automatically — a healthy
non-Steam server reported permanently unhealthy would make the probe
worthless exactly for the operators who deviate. The same degradation
applies to the operator's own probe (root §5.5's first capability):
serving state and player count come through the mediation channel when the
query protocol is off, and the documentation says so.

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
(location: open item g of §2), where they persist. If item g resolves to
a path outside the state root, the required response is fixed now: the
mod target **must be brought inside the documented state root** — by the
game's own configuration where it offers one, otherwise by relocation or
a link prepared at build time — and only if that proves impossible does
the image document a narrowed read-only claim as a reasoned root §5.1
deviation. Root §3.4's rule (nothing writes into the shipped game
directory) is never the thing that bends. The image neither bakes
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
  disk growth; with the caveat stated: an archive is only as consistent as
  the copy that captures it, so a hot copy of the state root can catch an
  archive mid-write — archives are trustworthy in copies taken while the
  server is stopped, or taken after the archive finished;
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
