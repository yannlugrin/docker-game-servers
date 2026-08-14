# Review 005 — Cold read, Opus, 2026-08-12

Spawn: general-purpose, worktree isolation, model: Opus.
Intended input: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md at 974afdf.

Editor's note (main session, during triage): the reviewer's worktree held a
STALE snapshot — findings F1, F2, F3a, F4, F8, F16, F18 quote text already
replaced by commits d617dc5/974adf (review 003/004 applications) and were
verified already-fixed in the current files. F3b was already ruled (non-Steam
supported with fallback). The remaining findings (F5, F6, F7, F9, F10, F11,
F12, F13, F14, F15, F17) are fresh and were triaged normally. Future spawns
carry the expected HEAD hash and a checkout-verify instruction.

---
All §N.M cross-references resolve: every `§N`/`§N.M` in the root document points at an existing root section (§1–§11, subsections 2.1–2.7, 3.1–3.5, 4.1–4.4, 5.1–5.8, 10.1–10.5), and every reference in `project-zomboid/SPECIFICATIONS.md` resolves too — internal `§1–§6` to its own sections, `root §…` (and one sentence-initial `Root §5.6`) to existing root sections. No dangling or misdirected reference found.

## 1. Summary-back

A public GitHub/GHCR repository publishing Docker images for dedicated game servers, linux/amd64 only because steamcmd is a 32-bit glibc binary, all stages on `debian:trixie-slim`. Two tiers: one **builder** image carrying a pre-warmed steamcmd (usable standalone as a generic "install a Steam app" builder, never as a runtime), and **per-game runtime** images produced by a multi-stage build where the builder stage downloads the game and the final slim stage copies it in with only that game's runtime deps — including the Steam client libraries the game dlopens, which is called out as the classic first-build trap. The game is **baked at build time**; no runtime install or update, ever, so the tag honestly names what is inside and consumers can pin by digest.

Every game image obeys a shared convention set: documented state paths under one state root, uid-agnostic and never root, world-readable shipped content so operators can isolate instances by uid; native config files as the authoritative interface with a small optional env-override surface; no secret in any layer, missing mandatory secrets fatal at start; unfiltered stdout logging plus a Steam-query HEALTHCHECK and two shipped operator clients (A2S + RCON); and — the section the whole document orbits — a shutdown path where the stop signal always results in a clean save, mediated by the entrypoint for games that ignore SIGTERM, with exit 0 reserved for a confirmed clean stop. Backups are not implemented but their consistent recipe must be documented. Tags are `<version>-rN` for games and dated snapshots for the builder, published by CI with buildid-driven update detection and a smoke test gating every game publish. First game: Project Zomboid Build 42, Java-based, state pinned to a fixed absolute path via the cache-dir option, admin password mandatory on first boot to avoid an interactive hang, shutdown via `save`+`quit` over the server console, workshop mods left to the game's own runtime download.

## 2. Findings

### F1 — blocking — root §5.3 vs. PZ §3/§4 (a per-game "must" contradicting a root "must")

Root §5.3: "The image must be fully operable with a mounted configuration and not a single game-specific environment variable set." Root §6: a per-game document "may deviate from a 'should' with reason, but never weakens a 'must'."

PZ §3 marks `ADMIN_PASSWORD` "**Mandatory on first boot**", and PZ §4 row 1 makes a fresh state directory with no `ADMIN_PASSWORD` a "**Fatal before game start**". Since PZ admin credentials live in the database and not in any config file (PZ §2), a Project Zomboid image mounted with a complete INI and zero env vars cannot start on a fresh state dir. The very first game violates the root must, and the implementer has two conflicting musts with no stated precedence.

Direction: either soften the root rule to something the games can actually honor (e.g. operable from a mounted configuration *for everything the game stores in configuration*, with per-game exceptions named where credentials live outside it), or make the root rule explicitly yield to per-game bootstrap secrets and say so where §6 states that per-game docs cannot weaken musts.

### F2 — blocking — root §5.6 table and PZ §5: the mediation bound is unspecified, unbounded by anything the operator can see or set

Root §5.6 requires "Bounded wait, then terminate the game process; exit non-zero — the save is unconfirmed", and recommends operators use a grace period of at least 90 s. Nothing states what that bound is, who chooses it, whether it is documented, or how it relates to the operator's `--stop-timeout`. The entrypoint cannot read the runtime's grace period, so it is a guess.

Two reasonable implementations diverge observably and in the worst direction the document has: a 60 s internal bound kills a still-saving PZ server on a large map (PZ §5 itself notes "large maps and many players lengthen saves") — producing exactly the mid-write corruption §5.6 exists to prevent, while the operator's 300 s grace period sat unused; a bound larger than the grace period instead lets the runtime `SIGKILL` first, and the entrypoint's careful non-zero exit never happens. This is the one place in the document where "the spec doesn't say how" changes whether saves survive.

Direction: make the mediation deadline a documented, operator-settable value (it is image behavior, not a game setting, so it does not offend §5.3's env-surface rule), require the documentation to state its default and to tell operators to keep the runtime grace period above it, and require a loud log line when the deadline expires.

### F3 — important — root §5.5 / PZ §6: "healthy" is under-defined in two ways, and root §8's smoke test depends on the answer

(a) "must fail once the server no longer accepts players" (root §5.5). A server at its player cap literally no longer accepts players while being perfectly healthy, and A2S returns exactly the numbers needed to make that mistake. One implementation reports unhealthy at `players == maxplayers`; another only on query failure. The first hands orchestrators a reason to restart the busiest server.

(b) A2S answers only when the server has Steam integration active. PZ can be configured non-public/Steam-disabled, in which case a legitimately configured server is permanently unhealthy — and root §8's smoke test ("start with a minimal configuration, report healthy") may or may not exercise a Steam-registered configuration. PZ §2 already lists "whether the Steam query protocol is answered on the main game port" as an open item, but not the Steam-disabled case.

Direction: define unhealthy as "no valid query response within timeout" and explicitly exclude a full server; and state what the image does when the game is configured such that no query listener exists (documented limitation plus a fallback probe, or a documented requirement that the healthcheck presumes Steam integration on).

### F4 — important — root §7 and §5.8: nothing says where `<game-version>` comes from, and §6's minimum list omits it

The tag `<game-version>-rN` and the version label are the consumer-facing contract, and §7 leans on the distinction between version string and buildid ("Steam ships new buildids without version changes"). But no section says how the version string is obtained — Steam's app metadata exposes buildid, not the game's marketing version. For PZ it must be read out of the installed files or a changelog. Two implementations produce different tag namespaces (`42.20-r0` vs `18234567-r0`), and the choice is irreversible once published, since §7 forbids reusing immutable tags.

Direction: add "how the game's version string is determined, and from what artifact" to §6's minimum per-game list, and state in PZ §2 where B42's version string is readable at build time.

### F5 — important — root §3.1 / §8: the builder image is a build input but nothing pins or records it

§3.1 makes every game image a multi-stage build whose builder stage comes "from the steamcmd image", and §8 says game images "should also be rebuilt (revision bump) when the base or the builder image materially changes". Nothing says which builder tag a game build uses. If it is `latest`, the reproducibility argued for in §3.2 ("their tags honestly say which game version is inside — which is what lets consumers pin by digest") is weakened at its root: two builds of the same `-rN` inputs can use different steamcmd content, and §5.8's label set records the Steam buildid and branch but never the builder image tag or digest.

Direction: require game builds to reference a pinned builder tag or digest, and add that reference to the §5.8 label set so a published game image says what built it.

### F6 — important — root §1 / PZ §7 and §2: runtime workshop-mod download has no loud failure path, and its target directory is a single-source fact with a severe failure mode

Root §1 makes game-managed runtime content "the one exception" to no-runtime-installs, and PZ §7 says "the server downloads the mods listed in its configuration at startup into the state root". Neither document says what must happen when that download fails — no Steam connectivity, a delisted item, a partial download. Left unspecified, the game starts anyway: players are kicked for mod mismatch at best, and for map mods a world loaded without them can regenerate or discard cells. That is a data-loss silent failure in a document whose stated bias is that dangerous behavior fails loudly.

Separately, "downloaded workshop mods … lives under one game-managed directory (`~/Zomboid` by default)" (PZ §2) is load-bearing and I have grounds to doubt it: PZ dedicated servers have historically placed workshop content under a `steamapps/workshop` tree, and community reports differ on whether that is under the cache dir or under the server install directory. If it is the install directory, the fact collides with root §3.4 ("never into the shipped game directory"), with the read-only-rootfs expectation of §5.1, and with the world-readable-but-not-writable ownership rule — and the collision surfaces as a mod download that fails at every start.

Direction: promote the mod download target to PZ §2's explicit "to settle before implementation" list alongside the port facts, and state the required behavior on mod-download failure (fail loudly before the world loads, or start with an unmissable log line — but decide it here, not in code).

### F7 — important — root §7 vs. §8: the tag scheme has no branch axis while on-demand builds accept one

§8 allows building "a chosen branch/version", and §2.3 makes branches a first-class Steam concept, but §7's game tag is `<game-version>-rN` with no branch component. Two branches that expose the same version string (a beta tracking stable, a `legacy`-style branch mid-transition) collide on the same immutable tag, breaking §7's own hardest rule: "A published immutable tag is never reused for different content." §10.3 shows the authors already envisage a tag suffix for mod-baked variants, so the axis exists conceptually but not for branches.

Direction: define how a non-default branch appears in the tag (suffix or prefix), or restrict §8's on-demand build to the branch declared in the per-game specification and say that other branches are out of scope until §7 is extended.

### F8 — important — root §8 vs. §7: the auto-publish trigger contradicts the reason the buildid label exists

§8: "a periodic job compares each game's current Steam buildid (§2.3) against the newest published image and, on a new game version, builds and publishes the new tags automatically." §7 says a "game content update whose version string did not change" is precisely a revision bump, "with the buildid label (§5.8) telling the truth the tag cannot". Read literally, §8 compares buildids but acts only on a new *version*, so the exact case §7 built the label for — new buildid, same version — never triggers a build.

Direction: state the trigger as a buildid change, and let §7's rules decide whether the result is a new version tag or a revision bump.

### F9 — important — §5 throughout: a large share of requirements carry no tier marker

The reading contract distinguishes tiers by "must" and "should", and grants deviation rights only for "should". Yet many load-bearing statements are bare present indicative and belong to neither tier: "The image documents **every path the game persistently writes**" (§5.1), "The image documents **every port**" (§5.2), "The game's output goes to **stdout/stderr, unfiltered**" (§5.5), "Each image declares a **HEALTHCHECK** …" (§5.5), "Game images ship two minimal static clients" (§5.5), "Images carry standard OCI annotations" (§5.8), "All documentation stays platform-neutral" (§9). Some then embed an escape hatch that reads like a "should" inside a requirement — "images whose game needs neither may drop them with reason" (§5.5). An implementer under time pressure can defensibly drop the RCON client or the OCI labels; under the document's own contract, that is a legitimate reading.

Direction: pass over §5 and §9 and attach an explicit modal to every statement, and move the "may drop with reason" clause into the sentence's tier rather than trailing a requirement.

### F10 — important — PZ §2/§3: `MAX_HEAP` states the hazard but requires no check, and OOM-kill is silent

PZ §2: "Its maximum heap is set through its launch configuration and must stay below the container memory limit: a heap equal to the limit makes the kernel OOM-kill the server at exactly the allocation the GC would have recovered." PZ §3 then makes `MAX_HEAP` "Optional (documented default)". A fixed default that exceeds a small container limit reproduces the named hazard by default, and a kernel OOM kill is the most silent failure in the whole set: no log line, mid-write, exit 137, and the container restart policy hides it.

Direction: require the entrypoint to read the container memory limit where the cgroup exposes it and fail loudly (or clamp with a warning) when the effective heap is not comfortably below it; where the limit is unreadable, say so and state what the default assumes.

### F11 — minor — root §5.6 table row 3 contradicts itself

"| Game crashes or exits by itself | Propagate a non-zero exit |". If the game exits 0 — an operator issuing `quit` through the RCON client the image ships (§5.5), a self-initiated clean shutdown — "propagate" yields 0 while the cell demands non-zero. The bullet above ("0 for a requested stop that completed cleanly; non-zero for everything else") does not settle whether an RCON-requested quit is "a requested stop".

Direction: say whether the exit code is propagated verbatim or normalized, and classify an out-of-band operator quit explicitly.

### F12 — minor — root §1 "nothing else" vs. §5.5's mandated extra clients

§1: game images contain "the installed game and its runtime dependencies — nothing else". §5.5 requires two additional static clients that are neither. Small, but it is the kind of absolute an implementer cites when cutting scope.

Direction: qualify §1 ("plus the operator clients of §5.5").

### F13 — minor — no stated project license, though §5.8 requires a license annotation

"Images carry standard OCI annotations: source repository, description, license" — the document never says which license the repository carries, and §9's deliverables list no LICENSE file. The implementer must guess a value that ends up baked into every published image.

### F14 — minor — the first-run permission failure is loud but its remedy is nowhere required

PZ §1: "A missing or unwritable state root is a loud fatal before the game starts". Good — but the overwhelmingly common trigger is a fresh named volume created root-owned while the container runs as `--user 1000:1000` (root §3.4). §9's README requirements list "writable paths and the state root" without requiring the ownership-preparation step, so the most frequent first-contact failure has a loud message and no documented cure.

Direction: add the mount-ownership prerequisite to §9's per-image README contents.

### F15 — minor — root §5.3's rewrite caveat is aimed at the operator, not at the image's own overrides

§5.3 warns about "An operator who re-renders the file on every deploy", but the image itself re-applies env overrides at every start ("when set, the entrypoint applies them to the effective configuration at startup"). For any setting also changeable in-game, that silently reverts the in-game change on every restart — same failure, caused by the image. PZ §3 documents only the credential-persistence consequence.

Direction: require the per-image documentation to state that any variable left set in a compose file wins over in-game changes at every restart.

### F16 — minor — `latest` ordering across game versions is undefined

§7: "a moving `latest` points at the newest revision of the newest game version." Ordering game version strings is not a solved problem (`42.9` vs `42.20` lexically inverts). Direction: define `latest` as the most recently published image, or state the comparison rule per game.

### F17 — minor — the root document admits no blind spots of its own

PZ §2 models this well with its dated facts and its explicit "Open port facts, to settle before the port table and healthcheck are final". The root document has Non-Goals and Future Considerations but never names what it is unsure about (§2.7's `steamclient.so` hazard is the closest). Given the doctrine, a short "known unknowns" note at root level would carry weight.

### F18 — minor — formatting defect in §5.3

Line 225 reads ` . The image must be fully operable… ` — the sentence-ending period of the previous bullet is orphaned onto its own line with a leading space, which renders as a stray paragraph in Markdown.

## 3. Questions for the operator

1. Is root §5.3's "not a single game-specific environment variable set" meant as an absolute, or as "everything the game keeps in configuration"? The answer decides whether F1 is fixed in the root or in PZ.
2. Who owns the shutdown deadline — a fixed image default, or an operator variable? And should the documentation instruct operators to set `--stop-timeout` above it?
3. Is `<game-version>` for PZ intended to be the marketing version (`42.20`) read from the install, or something derived from the buildid? Has a source for it been identified in a B42 install?
4. Is PZ ever expected to be run with Steam integration off (LAN/private)? If yes, is a permanently-unhealthy container the accepted outcome?
5. Are non-default Steam branches in scope for the tag scheme now, or should §8's "chosen branch" be narrowed to the branch each per-game specification declares?
6. What license does the repository carry, and should a LICENSE file be one of §9's deliverables?
7. Has the PZ workshop-mod download target actually been observed on a Build 42 Linux server, or is it inferred? Its answer decides whether root §3.4 and the read-only-rootfs expectation survive contact with mods.

## 4. Verdict

2 blocking, 8 important (plus 8 minor). Not a quiet round: the two blocking findings — a per-game must that contradicts a root must, and an unspecified shutdown deadline in the one section the document declares its strictest — both sit on the document's own critical path.
