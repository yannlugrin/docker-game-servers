# Review 006 — Cold read, Opus, 2026-08-12

Spawn: general-purpose, worktree isolation, model: Opus, staleness guard (verified checkout at 103926f).
Inputs: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md at commit 103926f.

---

All cross-references resolve. I verified mechanically: root `§N`/`§N.M` references (2.1–2.8, 3.1–3.5, 4.1–4.3, 5.1–5.8, 6, 7, 8, 9, 10.1, 10.4, 11) all map to existing headings; the per-game document's `root §N` references (2.7, 3.2, 3.4, 5, 5.1–5.7, 7, 11) all resolve in the root, and its bare `§N` references (1–7) all resolve locally. No dangling or ambiguous reference found.

## 1. Summary-back

A public GitHub-hosted repository producing Docker images for dedicated game servers, published on GHCR. Two tiers: one **builder image** (Debian 13 slim + steamcmd, pre-warmed so its self-update is baked in, usable standalone to install any Steam app), and **per-game runtime images** built multi-stage from a *pinned* builder reference, with the game copied in and steamcmd left out. Everything is linux/amd64 because steamcmd is a 32-bit glibc binary.

The game is baked at build time — never installed or updated at runtime — so tags honestly name what is inside; the cost is multi-gigabyte images and a rebuild per game update, which CI absorbs. Tags: immutable `<version>-rN` plus moving `<version>` and `latest` for games, date-stamped tags for the builder; immutable tags are never reused.

Every game image obeys a shared convention set (§5): document every persistent path and every port (flagging advertised vs freely remappable); native config files are the authoritative interface with env vars as optional overrides only; no secret ever in a layer, in a log, or as a default; a Steam-query HEALTHCHECK rather than a process check; and — the strictest part — a shutdown path that guarantees the stop signal reaches the game, mediating it into the game's own save/quit where the game ignores SIGTERM, bounded by an operator-settable timeout, with exit 0 reserved for a *confirmed* clean stop. Images are uid-agnostic, ship no default user, and fatally refuse uid 0.

CI provides on-demand builds, scheduled buildid-diff update detection, a mandatory scheduled base refresh (the only patch path into baked images), and a smoke test under an arbitrary non-root uid with a read-only rootfs that gates every publish.

The first game is Project Zomboid B42: Java server with its own JRE, state pinned to a fixed path via the cache-dir option, admin credentials living in a game-created database (hence an `INITIAL_ADMIN_PASSWORD`/`ADMIN_PASSWORD` pattern and a first-boot decision table), no native SIGTERM handling (so `save`+`quit` mediation over console-stdin, falling back to an entrypoint-owned internal RCON), native workshop mod downloads at startup, and a native backup feature. Eight facts are explicitly left open for implementation-time verification.

The through-line I read as the document's spine: the two chronic silent failures are a stop signal that never reaches the game and a secret that quietly persists — and nearly every prohibition traces back to one of them.

## 2. Findings

### F1 — `read-only root filesystem` is a "should" in §5.1 but a hard publish gate in §8 (important)

§5.1: "The image **should** run with a **read-only root filesystem** given writable mounts at the documented paths plus `/tmp`". §8: "It runs under an **arbitrary non-root uid** with a **read-only root filesystem** … A build that cannot pass this does not publish."

Under the reading contract a "should" is "a starting point the implementation may deviate from with reason". Here deviating means the image can never be published. An implementer who reasonably deviates in §5.1 (say, because the game insists on writing a lockfile under `/var`) has no path forward: §8 gives no deviation clause. The PZ document compounds this by restating it as binding ("The read-only-root-filesystem recommendation of root §5.1 applies unchanged", §1) while listing an open item (g) — mods possibly landing in the shipped game directory — that would break exactly this.

*Direction:* promote §5.1 to a must (it is load-bearing for the §3.4 writable-path promise), or give §8's gate the same escape hatch, naming what a documented deviation looks like at publish time.

### F2 — §8's base-refresh rebuild is specified as a revision bump, but such a rebuild can produce a different game version (important)

§8: "Game images **must** also be rebuilt (revision bump) when the base or the builder image materially changes". But §8's own on-demand bullet establishes that a build installs "whose current content determines the version tag (steamcmd installs what a branch holds *now*…)". If the branch moved since the last publish, a base-refresh rebuild yields a *new* game version, and §7's scheme mandates `<new-version>-r0`, not a revision bump of the old tag.

Two reasonable implementations diverge in an operator-visible way: one publishes `42.20-r3` containing 42.21 content (violating §7's honest-tag premise and the buildid label's meaning), the other publishes `42.21-r0` and silently leaves 42.20 unpatched — which quietly defeats the bullet's own stated purpose ("the *only* path by which security patches reach game images"). The scheduled-update bullet handles this correctly ("a changed version string as a new version tag, an unchanged one as a revision bump, per §7"); the base-refresh bullet does not.

*Direction:* make the base-refresh bullet defer to the same §7 mapping, and state explicitly whether older published versions are ever re-patched (a stated non-goal is fine — silence is not).

### F3 — PZ §6's healthcheck fallback weakens a root must (important)

Root §5.5 requires the check "must stop reporting healthy once the server is no longer serving — no longer answering queries", and §5.6/§5.5's whole rationale is that "a hung server is alive and unhealthy". PZ §6 offers as fallback "the best available game-level signal (the internal mediation channel of §5, or **a log-line readiness match**), documented as a reasoned deviation per root §5.5".

A log-line readiness match is a one-shot latch: once the line has appeared, it appears forever, so a hung server reports healthy indefinitely. That is precisely the failure §5.5 exists to prevent — and root §6 states a per-game document "may deviate from a 'should' with reason, but **never weakens a 'must'**". The internal-mediation-channel fallback is fine; the log-line variant is not equivalent to it.

*Direction:* drop the log-line option from the fallback order, or restrict it explicitly to *readiness only* while requiring a separate liveness predicate that can go false.

### F4 — root §5.5's two operator-capability musts are unmet on PZ's default and non-Steam deployments (important)

Root §5.5: "Two capabilities are **must** … the operator can ask 'is it serving, and how many players' from the host … and — where the game has an admin protocol or console — the operator can issue save/announce commands from inside the container via `docker exec`."

PZ has both an admin protocol and a console, so the second must applies. But PZ §6 says "the RCON client is useful to operators only when operator RCON is enabled (§3)" and PZ §3 marks `RCON_PASSWORD` optional with "operator RCON stays off without it". On the default deployment the operator therefore *cannot* save or announce — while the entrypoint itself demonstrably has a working channel (console stdin, or its own internal RCON, PZ §5) that PZ never makes available to the operator. Separately, PZ §6 declares "A **non-Steam configuration is supported**", which "silences the query protocol entirely" — that also defeats the *first* must (asking "is it serving, and how many players" from the host), and PZ addresses only the healthcheck consequence, not the operator-facing one.

*Direction:* either have PZ expose the entrypoint's mediation channel as the operator's `docker exec` save/announce path regardless of `RCON_PASSWORD`, or amend root §5.5 to scope the must to "where the game's admin channel is enabled" — and say what the query capability degrades to under a non-Steam configuration.

### F5 — the fatal refusal of uid 0 has no acknowledgment of rootless/user-namespaced runtimes (important)

§3.4: "the entrypoint **fatally refuses to run as uid 0**, with a message naming `--user` … a root default plants root-owned files in the operator's volume".

Under rootless Podman (where in-container uid 0 maps to the invoking host user) and under userns-remapped Docker, the stated reason does not hold: nothing root-owned lands on the host. Yet rootless Podman's default *is* uid 0, and a Kubernetes pod with no `runAsUser` also lands on uid 0 — so on both, an image the document insists is "usable with plain `docker run`, compose, or **any orchestrator**" (§1) refuses to boot with a message pointing at a Docker flag. There is no documented opt-out and no acknowledgment of the case.

*Direction:* keep the fatal if the real reason is "force a deliberate uid choice" (say that, since the file-ownership reason is what fails here), and add either a loud, explicitly-named opt-out or an explicit statement that rootless-root deployments are unsupported with its blast radius, in §11.

### F6 — where the version string comes from is an open item whose "build input" answer contradicts unattended CI (important)

Root §6 requires each per-game spec state "**where the human-readable version string is read from** (game files, distribution metadata, **or a build input** — it names the tags, §7)". PZ leaves this unresolved (§2 open item e). Root §8 requires scheduled detection to "build and publish **automatically** … Both flow **without human action**".

If (e) resolves to "a build input", the two are incompatible: the scheduled job cannot name its tag without a human supplying the version. Nothing in the document says what CI does then. Since (e) is unresolved for the *only* game in scope, an implementer building CI today must guess.

*Direction:* state in §7 or §8 what the tag scheme falls back to when no machine-readable version string exists (buildid-named tags are the obvious candidate, and the buildid label already exists), so the answer to (e) cannot strand CI.

### F7 — how the pinned builder reference advances is unspecified, and §8's trigger depends on it (important)

§3.1: "The builder stage must be referenced by a **pinned tag or digest**, never a moving pointer". §8: game images "must also be rebuilt (revision bump) when the base or **the builder image materially changes**".

With a hard pin, the builder reference *cannot* change on its own, so the trigger never fires unless something advances the pin — and nothing in the document says what, when, or whether the advance is automatic. Two reasonable implementations diverge visibly: one resolves the builder's `latest` to a digest at build time (arguably satisfying the label requirement while defeating the pin's stated purpose — "two builds of the same immutable game tag can differ at their root"), the other keeps a checked-in pin that a human must bump, in which case the scheduled base refresh refreshes the runtime base but silently never the builder stage. The asymmetry with the base (`trixie-slim`, an unpinned moving tag) is also unexplained.

*Direction:* state the observable rule — whether a builder publish obliges a game rebuild, and by what act the pin moves — without prescribing the mechanism.

### F8 — PZ's first-boot table and §3 disagree for `ADMIN_PASSWORD`-only on a game that cannot honor the override (important)

PZ §3: `ADMIN_PASSWORD` is "offered **only if** the game supports non-interactive password changes (open item, §2) — set on an image that cannot honor it, it is a fatal start (root §5.4)". PZ §4 row 2: "| No | Either set | Create the admin account via the game's non-interactive mechanism … start |" — unconditioned on whether the game supports the override. Row 5's fatal is conditioned on "Server database exists = **Yes**".

So on an image where open item (d) resolved negatively, an operator who sets only `ADMIN_PASSWORD` on a fresh state root gets a server that starts fine — and then refuses to start on the *next* restart (row 5). "Works once, fatal on restart" is the worst of both behaviors, and it is reachable by reading the table literally.

*Direction:* make the unsupported-override fatal unconditional on database existence (validation precedes the table), or add the missing row explicitly.

### F9 — the internal-RCON fallback introduces an undocumented listener, and its safety claim does not hold under host networking (important)

PZ §5: "the entrypoint generates an ephemeral password and enables RCON itself, solely for mediation — **safe because an unpublished container port is unreachable from outside**".

Three problems. (a) The claim is false under `--network host`, under a shared network namespace, and under any pod-level sidecar — all reachable via plain `docker run`/compose, which §1 says the images must serve. (b) Root §5.2 requires the image to document "**every port**" and to document admin interfaces separately "with an explicit warning that they must never be exposed publicly"; the internal mediation listener is a port and PZ never places it in the port table. (c) PZ's own env surface has a single `RCON_PORT` and a single `RCON_PASSWORD`, and PZ says the internal RCON is "distinct from *operator* RCON" without saying how they coexist — whether the ephemeral password overwrites the operator's `RCONPassword` in the rewritten INI (silently breaking the operator's own RCON access, and persisting an entrypoint-generated secret into the mounted, backed-up INI, contra root §5.4), or whether the entrypoint reuses the operator's password when one is set. Two implementations diverge in what the operator can still do and in what ends up in their backup.

*Direction:* if the fallback is taken, require the internal listener to be in the port table with its bind address stated, and state the coexistence rule with operator RCON explicitly.

### F10 — "an immutable tag is never reused" has no loud enforcement, and CI has two triggers that can race (important)

§7: "**A published immutable tag is never reused for different content.** Consumers pin `-rN`, a date tag, or a digest for reproducibility". §8 computes the revision "against what the registry already holds (never overwriting, per §7)" — a compute-then-push sequence with no stated check at push time. GHCR will happily move a tag. A manual on-demand build and a scheduled update-detection build firing in the same window both read `r2` and both publish `r3`; the second silently overwrites the first, and everyone who pinned `-r3` by tag now has different content with nothing in any log. The same applies to the builder's `YYYYMMDD.N` ordinal.

This is the document's own flagship failure shape — silent, discovered late — attached to one of its strongest promises, with no named loud path.

*Direction:* require that a publish which would overwrite an existing immutable tag fails loudly rather than proceeding, and say so as a requirement rather than leaving it inside a parenthetical.

### F11 — §3.5's "exactly four jobs" omits entrypoint duties assigned elsewhere (minor)

§3.5 enumerates "a thin entrypoint owning **exactly four jobs**", but §5.5 assigns it a fifth ("the entrypoint **should** relay the log file(s) there, following across the game's own rotation") and §5.4/§5.5 a sixth (the redaction that "takes precedence" over unfiltered stdout, which requires the entrypoint to interpose on the game's output — PZ §2 explicitly frames it that way: "whether the entrypoint may hand the game straight to stdout or must interpose the root §5.4 redaction"). "Exactly four" reads as a closed list and is not one.

*Direction:* either widen the enumeration or drop "exactly".

### F12 — the MAX_HEAP guard's threshold is unspecified in a way that changes whether a start is fatal (minor)

PZ §3: the entrypoint "must read the container memory limit where the cgroup exposes one and **fail loudly before the game starts** when the effective maximum heap is not below it (**leaving headroom for the JVM's non-heap memory**)".

"Leaving headroom" is unquantified, so the same operator configuration fatals on one implementation and boots on another — and since the guard exists precisely to prevent a silent OOM kill, a too-generous reading makes the guard decorative. Also unstated: what "where no limit is readable" means on cgroup v1, where an unlimited container reports a near-`INT64_MAX` value rather than nothing, which an implementer will read as a limit and pass trivially.

*Direction:* name the predicate at the altitude that matters (a stated fraction, or "heap plus a documented non-heap allowance"), and say that an implausibly large reported limit counts as "no limit".

### F13 — "No secret may ever reach … a crash dump" is a must the image cannot deliver (minor)

§5.4's absolute is followed only by a stdout remedy ("Where startup logs echo configuration, credential values are redacted"). For a JVM game a heap dump contains every string in memory, including the admin password; PZ §1 explicitly anticipates "JVM crash dumps" landing under `$HOME`. The image has no mechanism to satisfy the crash-dump half, and an implementer cannot verify it.

*Direction:* keep the stdout/stderr prohibition as a must and restate the crash-dump half as what it is — a warning the documentation owes operators (crash dumps may contain secrets; treat them as sensitive) — so the must stays checkable.

### F14 — the most likely real instance of the flagship silent failure is defended only by documentation (minor)

§5.6 identifies the trap precisely ("Docker's 10-second default is a save-corrupting trap for game servers") and mandates a documented 90-second floor. But nothing is emitted at runtime: an operator who never reads the README gets exactly the §2.4 outcome — SIGKILL, exit 137, "with nothing in any log". The entrypoint genuinely cannot read the runtime's grace period, but it can make the requirement visible where it will be seen: a line at start, or a line on receipt of the stop signal stating the wait it is about to perform and the grace period that must exceed it, which at least turns a mysterious 137 into an attributable one.

*Direction:* consider requiring the entrypoint to state its effective `STOP_TIMEOUT` and the grace period it implies, once per start or on stop.

### F15 — smaller precision points (minor)

- §2.4: "A shell-form entrypoint makes the shell PID 1, and it neither handles nor forwards the signal." Both `dash` and `bash` exec the final simple command of `sh -c`, so for the common single-command shell form the game *does* become PID 1. The claim errs in the safe direction, but an implementer who tests it and finds it false may discount the surrounding section, which is the one section the document calls its strictest.
- §5.3 enumerates the permitted env surface as "identity, ports, credentials, resource limits", but §5.6 mandates an operator-settable stop timeout and PZ ships `STOP_TIMEOUT`, which is none of the four. The list reads as closed.
- PZ §1 leaves `$HOME`'s location open ("inside the state root or a dedicated mount"). Both satisfy §3.4's enumeration requirement, but they differ for the operator: inside the state root, JVM crash dumps and the Steam link farm land in every backup the operator takes per PZ §8 ("what to copy: the state root"); as a dedicated mount, `docker run --read-only` needs a third writable target. Worth stating which consequence the image accepts.

## 3. Questions for the operator

1. **F1:** is the read-only rootfs an absolute gate, or may a game deviate with reason? If it may, what does a publish look like for such a game?
2. **F2:** when a scheduled base refresh finds the branch has moved to a new game version, which tag is published — and does the previous version ever get re-patched?
3. **F6:** if PZ's version string turns out not to be machine-readable, what does CI tag with? Is buildid-named tagging acceptable, or does the game drop out of scheduled publishing?
4. **F7:** is bumping the pinned builder reference a human act or an automated one, and does publishing a new builder oblige a rebuild of every game image?
5. **F4:** on a PZ deployment with no `RCON_PASSWORD`, is the operator expected to be able to save/announce? If yes, through what channel — and does that mean exposing the entrypoint's mediation channel?
6. **F5:** are rootless Podman and default-`runAsUser` Kubernetes deployments in scope? If yes, the uid-0 fatal needs an opt-out; if no, it belongs in §11 with its blast radius.
7. **F9:** is the internal mediation RCON allowed to reuse (or overwrite) the operator's configured RCON password and port, or must it be independent — and does it get a row in the port table?
8. **F10:** should a publish that would overwrite an existing immutable tag fail the CI job, or is compute-then-push considered sufficient?
9. **F12:** what headroom does the MAX_HEAP guard leave, expressed as something two implementers would compute identically?
10. PZ §2 asserts "Build 42 is the stable branch since 2026-07-29 (version 42.20)". I have no way to verify this and it is dated with a re-verification obligation — but the whole tag scheme rests on it. Was this confirmed against Steam directly, or from community sources?

## 4. Verdict

10 important findings, 0 blocking. Not a quiet round: F1–F4 are cross-section contradictions rather than gaps, and F5–F10 each leave an operator-visible behavior for the implementer to guess. The document is unusually disciplined — the reasoning-attached-to-musts standard is met almost everywhere, and the open-items list in PZ §2 is a model of honest scope — but several of those open items are load-bearing for musts, and two conventions (read-only rootfs, the builder pin) are stated at a tier their downstream use does not match.
