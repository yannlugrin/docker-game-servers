# Review 008 — Cold read, Opus, 2026-08-12

Spawn: general-purpose, worktree isolation, model: Opus, staleness guard.
Inputs: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md at 48adad4.

---
## Cross-reference verification

Mechanical check of every `§N`/`§N.M` reference in both documents against the actual headings:

- Root document: references to §1, §2.1–2.4, §2.6–2.8, §3, §3.1, §3.2, §3.4, §4.1, §4.3, §5, §5.1–5.8, §6, §7, §8, §9, §10.1, §10.4, §11 — **all resolve.**
- `project-zomboid/SPECIFICATIONS.md` `root §…` references (§2.7, §3.2, §3.4, §5, §5.1–5.7, §7, §11) — **all resolve.**
- PZ local references (§1–§7) resolve **except one**: see Finding 11.

## 1. Summary-back

A public GitHub repository publishing Docker images for dedicated game servers on GHCR. Two tiers: one **builder image** carrying a pre-warmed steamcmd (Debian 13 slim, amd64 only, because steamcmd is a 32-bit glibc binary that cannot run on musl), usable standalone as a generic "install a Steam app" stage; and **per-game runtime images** built multi-stage from a *pinned* builder reference, with the game baked in at build time and steamcmd absent — so a tag honestly names what is inside, containers start in seconds, and every game update becomes a rebuild rather than a runtime download.

Game images are uid-agnostic: no default user, world-readable content, a loud fatal on uid 0 with a single documented `ALLOW_UID0` opt-out for rootless/userns runtimes, and an enumerated writable-path set so a read-only rootfs is checkable. A thin entrypoint validates startup state, applies optional environment overrides onto the game's own (authoritative) config files, guarantees signal delivery, and — for games that ignore `SIGTERM` — translates the stop into the game's own save/quit sequence, bounded by an operator-settable timeout that must sit under the runtime's grace period. Exit 0 means, and only means, a confirmed clean stop.

The whole document is organized around two silent failures: a stop that never reaches the game (a `SIGKILL` mid-save), and a secret that leaks into a layer, a log, or a backup. Health is a game-protocol probe (Steam A2S), never a process check. CI must offer on-demand builds, buildid-driven update detection, and a self-sustaining scheduled base refresh (GitHub disables idle scheduled workflows), with immutable tags never reused and a smoke test — non-root uid, read-only rootfs, stop-and-exit-0 — gating every publish. Backup, orchestration and fleet management are explicit non-goals; the image owns the *knowledge* (a consistent-backup recipe and a save-migration warning) but never the mechanism. Project Zomboid Build 42 is the first game: Java, fixed state root via cache-dir, mandatory first-boot admin credential, mediated shutdown, workshop mods downloaded by the game itself, with ten named facts still to verify at implementation.

## 2. Findings

### Finding 1 — important — root §2.5, §5.5; PZ §2, §6
**The entire healthcheck design rests on an unverified premise, and PZ's own open-item list does not contain it.**

Root §2.5 asserts: "It is the correct liveness probe either way: a hung server keeps its process alive but stops answering queries." PZ §6 turns this into a requirement: "The liveness predicate must be one that **can go false on a hung server**". But PZ is a Java server using the Steamworks game-server API, where the A2S responder commonly lives outside the game's main loop. The document never verifies, for this game, either half of the premise:

- that A2S responses **stop** when the simulation hangs (if the SDK thread keeps answering, the healthcheck is worthless for exactly the failure it exists to catch), and
- that A2S responses **have not yet started** while the world is loading (root §5.5: "The check must not report healthy while the world is still loading" — if the responder comes up at Steam init, the check goes healthy minutes before the server serves, and §8's smoke test passes on a server that never finished loading).

PZ §2's open items (a)–(j) include *where* the query is answered (item a) but not *whether the answer tracks serving state*. §2.9's admitted blind spots don't mention it either.

*Direction:* add an open item to PZ §2 requiring measurement of A2S behavior at both ends (during world load, and against an artificially hung/deadlocked server), with the stated consequence if it fails — the fallback order of PZ §6 already exists and can absorb it, but only if the question is asked.

### Finding 2 — important — root §5.2; PZ §2, §3, §5
**The RCON bind address is decided two incompatible ways, and one reading yields a documented port that is silently unreachable.**

Root §5.2: "**Admin interfaces are the opposite case**: they bind loopback where the game allows it, and are opened wider only by the operator's deliberate choice". PZ §2 records RCON as "**RCON on TCP (default 27015)**, enabled only when an RCON password is configured, freely remappable", PZ §3 exposes `RCON_PORT`, and PZ §5 says "Operator RCON over the network remains what `RCON_PASSWORD` enables". "Freely remappable" and "over the network" require a `0.0.0.0` listener; root §5.2 requires loopback until the operator deliberately opens it wider — and no PZ variable expresses that deliberate choice. An implementer who follows root §5.2 literally ships an image where `-p 27015:27015` publishes a port with nothing reachable behind it: connection refused, no log line, the operator concludes RCON is broken.

Two consequences of the same unanswered question:

(a) **Operator RCON**: is setting `RCON_PASSWORD` itself the "deliberate choice" that opens the listener wide, or is a separate bind-address control needed?

(b) **Internal RCON**: PZ §5 states as a hard constraint that "the listener binds **loopback only**" — dropping root §5.2's "where the game allows it" escape — but PZ §2's facts never establish that the game *offers* an RCON bind-address setting, and it is not an open item. If it does not, the sanctioned fallback for the document's flagship silent failure (stop mediation) either cannot be implemented or opens a generated-password admin listener on all interfaces, which is precisely what the constraint exists to prevent, and no branch is provided.

*Direction:* add an open item for PZ's RCON bind-address configurability; state explicitly whether `RCON_PASSWORD` implies a wide bind; and give the internal-RCON constraint a stated fallback for the case where the game cannot bind loopback (e.g. refuse the fallback and fail loudly at start, rather than open it wide).

### Finding 3 — important — root §5.3, §5.6; PZ §3
**No rule for a variable that is set but unparseable — the default silently wins.**

The only value-validation rule anywhere in the document is `ALLOW_UID0`'s (root §3.4). Root §5.3 says only that "when set, the entrypoint must apply them to the effective configuration at startup", and the §5.6 table's row "Startup validation fails (§5.3, §5.4)" refers to a validation whose content is never defined beyond mandatory/optional. So `STOP_TIMEOUT=9O` (letter O), `MAX_HEAP=4gb`, `GAME_PORT=` are undefined: one implementation fatals, another falls back to the documented default. The `STOP_TIMEOUT` case is the document's own failure shape — an operator who believes they granted 300 seconds gets 80, and the save dies to a timeout they thought they had eliminated. `MAX_HEAP` is worse: the §3 heap guard is only as good as the parse feeding it.

*Direction:* a general rule in §5.3 — any variable set to a value the entrypoint cannot parse or apply is a fatal start naming the variable and the value, never a silent revert to default — with `ALLOW_UID0`'s existing clause becoming an instance of it rather than a special case.

### Finding 4 — important — PZ §4
**"Server database exists" is a proxy for "an admin account exists", and the gap produces the adminless public server the table calls unacceptable.**

The table keys on "Server database exists". Row 1 declares the fatal because "a hang or an adminless public server are both unacceptable". Row 3 says: "| Yes | Only `INITIAL_ADMIN_PASSWORD` set | Start; the variable is ignored **by definition**". But the database and the admin account are not created atomically: a first start interrupted after the DB file appears and before account creation (OOM kill, operator `^C`, a failed mod download per open item h) leaves a populated-looking state root with no admin. On the next start the entrypoint sees "database exists", ignores the credential it was given, and starts a public server with no admin — silently, and with the operator's `INITIAL_ADMIN_PASSWORD` still set in their compose file, which is exactly the state that reads as "handled".

*Direction:* define the predicate as "an admin account exists for the effective `SERVER_NAME`" where the game makes that observable, or make the non-interactive creation step idempotent (always run it when a credential is supplied and the account is absent). Either resolution is a stated behavior; the current text lets two implementations differ on whether an interrupted first boot heals or silently degrades.

### Finding 5 — important — root §6; PZ §2, §8
**PZ omits a fact root §6 mandates, and does not flag it as an open item.**

Root §6 requires the per-game facts to include "**what a game-version upgrade does to existing saves** (§5.7) — dated, and re-verified at implementation". PZ §2 contains no such fact. PZ §8 carries only the generic warning ("a newer game version may migrate the world irreversibly"), which is the root §5.7 obligation restated, not the researched answer. Because it is absent from both the facts list and the (a)–(j) open items, an implementer walking the open items will never notice the hole — and this is the one fact behind the document's most expensive failure mode, on a game whose Build 42 line is known for save-format churn.

*Direction:* either state the researched fact (does a B42 point release migrate, invalidate, or silently regenerate a world?) or add it as an explicit open item with the documentation consequence attached, the way items (g) and (h) are handled.

### Finding 6 — important — root §8; PZ §1, §4, §6
**The smoke test's "minimal configuration" is undefined against PZ's own requirements, so the publish gate's strictness is an implementer's guess.**

Root §8: "the built image must start with a minimal configuration, report healthy (§5.5), stop on the stop signal, and exit 0". For PZ, "minimal" is not minimal: it must supply `INITIAL_ADMIN_PASSWORD` (PZ §4 row 1 is otherwise a fatal), it must reach "healthy" through a probe whose `start_period` PZ §6 sizes to absorb world generation that "takes minutes", and — if Finding 1 resolves unfavorably — reaching healthy may depend on Steam reachability from the CI runner. Nothing states whether the smoke test runs the default Steam configuration or the non-Steam configuration PZ §6 also supports (which switches the healthcheck onto a different channel and therefore tests a different code path). Two reasonable implementations gate publishes on materially different assertions; a weak one passes images the strong one would reject.

*Direction:* state what the smoke test must exercise in behavioral terms — the configuration profile(s), whether external Steam connectivity is a permitted dependency of the gate, and an upper bound on wait-for-healthy after which the gate fails rather than hangs.

### Finding 7 — minor — root §5.5
**`start_period` is credited with a behavior Docker's healthcheck does not have.**

"The check must not report healthy while the world is still loading (the `start_period` must absorb worst-case load time)". `start_period` suppresses *unhealthy* transitions; it does not suppress *healthy* — a probe that succeeds during the start period marks the container healthy immediately (and on Docker 25+ ends the start period there and then). The protection against "healthy while loading" comes entirely from the probe not answering yet, which is Finding 1's unverified premise. As written, an implementer can satisfy the parenthetical, believe the requirement is met, and ship a container that reports healthy mid-load.

*Direction:* separate the two clauses — the probe is what must not answer before the server serves; `start_period` exists only so a slow start is not marked unhealthy — and keep the (correct) hang-detection-blinding trade-off attached to `start_period` alone.

### Finding 8 — minor — PZ §4
**The decision table is missing its most common row.**

Rows cover (No, neither), (No, either), (Yes, only `INITIAL_`), (Yes, `ADMIN_PASSWORD`). There is no row for **database exists, neither variable set** — the ordinary steady-state restart of a configured server. The intended behavior (start normally) is inferable, but a table introduced as covering the branch where "an implementer testing 'any database in the state root' reproduces exactly the hang this table exists to prevent" invites literal reading, and the adjacent row 1 fatal makes "neither set" look categorically dangerous.

*Direction:* add the row explicitly.

### Finding 9 — minor — root §3.4; PZ §3
**The uid-0 opt-out's rejection message misfires on the obvious negative values.**

"Any other value does not skip it, and the fatal message must then say the variable was set but not recognized". An operator writing `ALLOW_UID0=0` or `ALLOW_UID0=false` — the natural way to express "no" — is told their value was *not recognized*, which reads as a typo report for a deliberate, correct instruction. The outcome is right and loud; the diagnosis is wrong.

*Direction:* recognize the standard negatives as an explicit "off" and reserve the not-recognized wording for genuinely unparseable values (this also becomes free if Finding 3's general rule is adopted).

### Finding 10 — minor — PZ §3, §4
**The declarative override's target account is undefined when `ADMIN_USERNAME` changes.**

`ADMIN_USERNAME` is optional with a default, and `ADMIN_PASSWORD` is "applied at every start". If an operator changes `ADMIN_USERNAME` on a populated state root while `ADMIN_PASSWORD` is set, the document does not say whether the entrypoint creates a second admin, renames, applies to the existing account, or fails. Root §5.4's rule — "Setting an override the image cannot honor is a **fatal start**" — arguably covers it, but only if the implementer connects the two, and the failure otherwise is the one §5.4 names: "believed and effective credentials silently diverge".

*Direction:* state the behavior when the named account does not exist on a non-first boot.

### Finding 11 — minor — PZ §7
**Dangling local cross-reference.**

PZ §7 ends "…only if that proves impossible does the image document a narrowed read-only claim as a reasoned §5.1 deviation." Per the PZ preamble, "References written `§N` point to this document" — and this document has no §5.1 (its §5 is Shutdown). The intended target is root §5.1. This is the only reference in either document that does not resolve.

*Direction:* `root §5.1`.

### Finding 12 — minor — root §2.4, §5.6
**PID 1's second duty is never mentioned.**

§2.4 covers signal delivery exhaustively and §5.6 requires that "either the game binary is PID 1 (exec'd, exec-form), or the entrypoint remains PID 1 with explicit handlers and reliably relays the stop." For PZ the second branch is mandatory (mediation requires a live parent), which makes a script PID 1 for the container's whole life — and PID 1 also inherits orphaned processes and must reap them. Unreaped zombies are a slow, silent resource leak on long-lived servers, the same failure class the document targets everywhere else.

*Direction:* one clause in §5.6 — where the entrypoint stays PID 1, it must reap orphaned children — stated as behavior, not mechanism.

### Finding 13 — minor — PZ §1
**Setting `HOME` may not control the JVM's idea of home, and the smoke test cannot catch the difference.**

PZ §1 sets `$HOME` "unconditionally" inside the state root to complete the writable-path set. On Linux, OpenJDK resolves `user.home` from the passwd database first and falls back to `$HOME`, so the guarantee holds precisely in the case CI exercises (root §8's "arbitrary non-root uid", i.e. no passwd entry) and can fail in an operator environment where the uid *does* resolve (user-mapped runtimes, a mounted `/etc/passwd`) — JVM-side paths then land outside the writable set under `--read-only`. The blast radius is residue rather than saves, but the document treats the writable-path claim as proven by the smoke test.

*Direction:* note in PZ §2's open items that the `$HOME`-override guarantee covers native/`steamclient.so` paths and must be verified separately for JVM-resolved paths.

### Finding 14 — minor — root §2.8, §8
**The deactivation-resistance requirement offers two options that are not equivalent, and "visible" has no surface.**

"the refresh must keep itself alive (producing repository activity counts) or run outside the repository's activity clock, and a refresh that has not run within its cadence must become visible rather than stay a green absence." The first option depends on whether GitHub counts commits pushed by the workflow's own default token as repository activity for the 60-day clock — a detail with a history of surprising people, and one §2.8 does not assert. More importantly, once the workflow *is* disabled, nothing inside it can report anything, so "must become visible" is only achievable by the second option or by an out-of-band check; and "visible" names no observable (a failing job, a dated badge, and an email are all "visible" and differ entirely in whether anyone sees them).

*Direction:* say what visibility means observably (a job that fails, and where), and either assert the activity-counting fact in §2.8 with its source or drop the first option to a "should" beneath the out-of-band one.

## 3. Questions for the operator

1. Is there a measurement, or an intent to measure, that a hung PZ server stops answering A2S — and that it does not answer *before* the world is loaded? Everything in §5.5 and PZ §6 depends on it (Finding 1).
2. For PZ, is operator RCON meant to be reachable from the host via a published port, or only via `docker exec`? The answer decides Finding 2 and whether `RCON_PORT` belongs in the env table at all.
3. Does PZ's RCON support a bind address? If not, what should the entrypoint do when console-over-pipe (open item c) also fails — refuse to start, or open a wide listener with a generated password?
4. Is a set-but-unparseable environment variable intended to be fatal across the board, or is silent fallback to the default acceptable for some of them?
5. Should the smoke test run the default Steam configuration, the non-Steam configuration, or both — and is external Steam reachability an acceptable dependency for a publish gate?
6. Is the absence of any build/validate step on ordinary pushes and pull requests deliberate? As written, an entrypoint regression is caught only at the next on-demand or scheduled publish attempt.
7. `STOP_TIMEOUT` "default ~80s": is the tilde deliberate latitude, or should a single number be fixed so the documented pairing rule cites something exact?
8. PZ open item (e) leaves the version-string source unresolved, which means the tag naming of the first image is undetermined until implementation. Is the buildid-derived fallback of root §7 an acceptable outcome for PZ, or must the human-readable string be found?

## 4. Verdict

**6 important, 0 blocking.** Not a quiet round: the healthcheck's core premise and the RCON bind address are both load-bearing and unresolved, and two mandated items (a root §6 fact, a general value-validation rule) are missing rather than deferred. The document is otherwise unusually disciplined — reasoning is attached where it matters, tiers are clean, the facts I could check independently (app id 380870, PZ's ports, cache-dir relocation, the non-interactive admin arguments, `lib32gcc-s1`, GHCR/Docker Hub, Docker's 10-second default) all hold, and the ten PZ open items each carry a stated consequence.
