# Review 003 — Cold read, 2026-08-12

Spawn: general-purpose, worktree isolation, session model (Fable 5).
Inputs: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md (commit 31e56c1).

---

## Cross-reference check

Every `§N.M` reference in both documents resolves: root-internal references (§2.1–§2.7, §3.2, §3.4, §5.1–§5.8, §6, §7, §8, §10.4, §11), the per-game document's `root §N` references, and its internal `§1–§8` references (including the §2→§3/§6 forward references) all point at existing sections with matching content. No finding here.

## 1. Summary-back

A public repo of Docker images for Steam dedicated game servers, published on GHCR, linux/amd64 only, Debian trixie-slim base throughout. Two tiers: a steamcmd **builder** image (dated-snapshot tags, since steamcmd has no versions and self-updates), and per-game **runtime** images built multi-stage from it, with the game baked in at build time — steamcmd never ships in a game image, but the Steam client libraries the game dlopens must. Game images are uid-agnostic, single-instance, secretless in layers, driven by native config files with a small optional env-override surface, and are obligated above all to turn the container stop signal into a confirmed save-and-exit (the doctrine's flagship silent failure), with honest exit codes and an A2S-based healthcheck. Versioning: immutable `<version>-rN` tags plus moving pointers; CI does on-demand builds, scheduled buildid-based update detection, base-refresh rebuilds, and a smoke test gating every publish. Each game carries its own specification bound by the same contract; the first is Project Zomboid Build 42: Java server shipping its own JRE, single state root pinned via the game's cache-dir option (not `$HOME`), two advertised UDP ports, optional RCON, no native SIGTERM handling (entrypoint mediates `save`+`quit` via the server console), a first-boot admin-password decision table, and a native-backup-first backup recipe.

## 2. Findings

**1. Important — root §8 vs root §7: the scheduled job's trigger is ambiguous for same-version buildid changes.**
Evidence: §8 says the job "compares each game's current Steam buildid (§2.3) against the newest published image and, **on a new game version**, builds and publishes"; §7 explicitly defines a buildid change without a version change as a revision bump. The comparison detects same-version buildid changes; the trigger clause covers only version changes. Two reasonable implementations diverge observably: one auto-publishes `-rN` bumps on every buildid change, the other publishes nothing until the version string moves — meaning content updates Steam ships without a version bump either flow automatically or sit unpublished indefinitely. Direction: state explicitly whether a same-version buildid change triggers an automatic revision-bump publish, and why.

**2. Important — PZ §2/§5/§3: the load-bearing mediation channel is an unverified fact not on the open-facts list, and its failure mode has no sanctioned fallback.**
Evidence: PZ §5 requires shutdown mediation "through a channel that exists regardless of operator configuration (the server console; RCON only as an alternative when configured)", satisfying root §5.6's must. But whether the Build 42 server console accepts commands over a non-interactive stdin pipe inside a container (no TTY) is exactly the kind of expensive-to-guess fact the document elsewhere flags — §2 gives the port questions explicit "open item" status, yet the console channel gets stated as settled. If it resolves unfavorably, there is no compliant design: RCON cannot be the mediation path (root §5.6 forbids depending on optional config), and the env table's "RCON stays off without `RCON_PASSWORD`" forecloses the obvious escape hatch of an entrypoint-managed internal RCON. Direction: add console-over-pipe viability to §2's open facts, and name the fallback if it fails (e.g., sanction an image-internal, localhost-only RCON and reconcile the env table's wording).

**3. Important — PZ §4, last table row: the preferred branch ("apply the password") creates a silent-revert the document's own doctrine condemns, and the reasoning covers only the other branch.**
Evidence: "apply the password to the existing account if the game supports it non-interactively, otherwise emit a prominent warning at every start". The reasoning paragraph justifies the warning branch thoroughly; the apply branch gets none — yet under it, a compose file that keeps `ADMIN_PASSWORD` set forever resets the admin password on every restart, silently reverting any in-game password change. That is precisely the class of failure root §5.3 warns about ("silently revert every setting changed in-game — a baffling failure when it is not written down"). Env-wins may well be the right precedence, but it is currently an undecided, unreasoned side effect. Direction: decide the precedence explicitly, attach reasoning, and require the documentation to state it prominently.

**4. Minor — root §5.3 first bullet vs PZ §3: the letter of "fully operable with a mounted configuration and not a single game-specific environment variable set" is violated by PZ's first boot.**
Evidence: PZ's admin credential lives in the game-created database, not in any mountable config file, so a fresh state root cannot be booted without `ADMIN_PASSWORD` — a game-specific env var. Root §5.3's second bullet anticipates mandatory vars ("values without which the game cannot start safely"), so the intent is inferable, but the two bullets conflict textually for the flagship game. Direction: scope the operability must (e.g., "for every value the game itself can take from files") or carve out first boot explicitly.

**5. Minor — PZ §6/§2: no direction if the healthcheck's open fact resolves unfavorably.**
Evidence: §6 assumes "the port the §2 verification confirms (expected: the main game port)"; §2 admits community documentation is not authoritative. Root §5.5 makes a game-protocol probe a must. If Build 42 answers A2S on no port (game port no, SteamPort1/2 gone), the implementer has a must with no satisfiable target and no stated alternative. Direction: name the fallback order (SteamPort listeners if present, RCON handshake, or a reasoned documented deviation).

**6. Minor — root §8: "a chosen branch/version" overstates what a steamcmd install can deliver.**
Evidence: steamcmd installs whatever a branch currently holds; installing an arbitrary historical version requires depot-manifest machinery the document nowhere contemplates. An implementer could burn time trying to honor "chosen version" literally. Direction: phrase it as "a chosen branch (whose current content determines the version tag)".

**7. Minor — PZ document vs root §5 preamble: two conventions are not addressed.**
Evidence: root §5 preamble says the per-game section "documents how each convention is honored"; the PZ document never mentions the read-only-root-filesystem should (root §5.1) or the two shipped static clients (root §5.5) — the latter matters because PZ's RCON-off-by-default interacts with the RCON client's stated purpose. Direction: one line each in the PZ document, even if only "applies unchanged".

**8. Minor — root §5.5: "must fail once the server no longer accepts players" is the wrong predicate.**
Evidence: a full server rejects joins yet is perfectly healthy; the phrase invites a probe that flaps on full servers. Context makes clear "hung / no longer answering queries" is meant. Direction: rephrase to the query-answering predicate the rest of the bullet already uses.

## 3. Questions for the operator

1. Should the scheduled update job auto-publish revision bumps when the buildid changes but the version string does not (finding 1)?
2. Has anyone confirmed that the B42 server console accepts `save`/`quit` over a non-interactive stdin pipe in a container — and if it does not, is an image-internal RCON an acceptable mediation channel (finding 2)?
3. When the database exists and `ADMIN_PASSWORD` is set, is "environment wins on every start" the intended precedence, accepting that in-game password changes are reverted on restart (finding 3)?
4. If Build 42 answers A2S on no port at all, what should the healthcheck probe (finding 5)?
5. Is first boot on a fresh state root intended as an exception to "operable with zero game-specific env vars" (finding 4)?

## 4. Verdict

0 blocking, 3 important (plus 5 minor) — not a quiet round, but nothing blocks: the important findings are ambiguities and an unflagged load-bearing fact, all resolvable with targeted edits rather than redesign.
