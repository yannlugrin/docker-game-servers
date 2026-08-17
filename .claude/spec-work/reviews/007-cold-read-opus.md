# Review 007 — Cold read, Opus, 2026-08-12

Spawn: general-purpose, worktree isolation, model: Opus, staleness guard
(worktree was stale at 31e56c1; reviewer checked out 6830d8f as instructed).
Inputs: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md at 6830d8f.

Editor's note: findings are genuinely fresh against current text. F1 is a
contradiction introduced by the review-006 application itself (prose vs
table in root §5.6).

---
**Cross-reference check (mechanical):** every `§N` / `§N.M` reference in both documents resolves. Root document: 79 references, targets `1`–`11`, `2.1`–`2.8`, `3.1`–`3.5`, `4.1`/`4.3`, `5.1`–`5.8`, `10.1`/`10.4` — all present. Per-game document: 38 `root §` references (all resolving in the root document) and 24 local references (`§1`–`§7`, all present; `§8` is never referenced, which is fine). One cosmetic exception: line 3 writes "Per-game specification under §6 of the repository-root `SPECIFICATIONS.md`" — a bare `§N` pointing at the root, against the convention the same document states two lines later; the prose disambiguates it, so it is not a finding.

## 1. Summary-back

A public GitHub repository publishing Docker images to GHCR for dedicated game servers. Two tiers: one **builder image** (Debian 13 slim + steamcmd, pre-warmed so its self-update is baked into the layer, usable standalone by anyone as "install a Steam app"), and **per-game runtime images** built multi-stage from a *pinned* builder reference, containing the game copied in, its runtime deps, the Steam client libraries the game dlopens, and two tiny static clients (Steam-query, RCON) — no steamcmd. linux/amd64 only, because steamcmd is a 32-bit glibc binary.

The game is **baked at build time**, never installed at runtime: that is what makes a tag honest, cold starts fast, and digests pinnable. The price — multi-gigabyte images and a rebuild per game update — is accepted and absorbed by CI. Tags are `<game-version>-rN` immutable plus moving `<game-version>` and `latest`; a publish that would overwrite an immutable tag must fail the job loudly. CI does on-demand builds, scheduled buildid-diff detection (auto-publishing on *any* buildid change), and a scheduled base/builder refresh that is the only path by which security patches reach baked images. Every game publish is gated by a smoke test under an arbitrary non-root uid with the read-only rootfs the image claims.

Images are uid-agnostic (no default user, fatal refusal to run as uid 0 with an `ALLOW_UID0` opt-out for rootless runtimes, world-readable shipped content), configured through the game's **native config files** with environment variables as small, optional, at-every-start overrides. Secrets never enter a layer, never reach stdout, and a missing mandatory one is a fatal start. The document's spine is a bias against two silent failures: a stop signal that never reaches the game (hence PID 1 discipline, entrypoint-mediated `save`/`quit`, an operator-settable stop timeout that must sit under the runtime grace period, and exit 0 reserved for a confirmed clean stop) and a credential that quietly lands in a log or a backup.

The first game is Project Zomboid Build 42: Java server with its own JRE, one state root pinned to a fixed path (not `$HOME`-derived, because Java home resolution is fragile under a passwd-less uid), two advertised UDP ports plus RCON, no native SIGTERM handling (so mediation is mandatory), an admin password that lives in a game-created database and would otherwise hang on an interactive prompt, native workshop-mod downloading, and a native backup feature. Its spec carries eight explicitly-named open facts (a–h) to settle at implementation.

## 2. Findings

### F1 — blocking — root §5.6

The prose definition and the normative table disagree on the exit code when the game exits on its own but *badly*. Prose: "**A confirmed clean stop** — the only thing that exits 0 — is defined observably: the shutdown sequence was delivered and the game process exited *on its own* within the timeout. A game process the entrypoint had to terminate, or that crashed on the way down, is unconfirmed." The table row: "| Stop signal, game exits on its own within the stop timeout | Exit 0 — confirmed clean stop |".

A JVM that receives `quit`, begins its save, and then dies to an exception or a signal *has* "exited on its own within the stop timeout" — the table says exit 0, the prose says unconfirmed. The bullet is also self-contradictory in isolation: a crash on the way down *is* an exit on its own. An implementer following the table (the more operative-looking artifact — its column is literally headed "Required behavior") ships the exact miscoding the section names as its worst outcome: "miscoding a dirty stop as clean hides exactly the corruption this section exists to prevent." This is the supervision interface of the section the document calls its strictest, so the divergence is not academic.

*Direction:* make the game's own termination status part of the observable predicate — a confirmed clean stop requires the game to exit *successfully* on its own within the timeout — and split the table row accordingly, so the crash-during-shutdown case has its own line.

### F2 — important — PZ §6, PZ §5, root §5.5

PZ's healthcheck fallback and the operator's status probe both fall back to "the mediation channel of §5, probed per check", while PZ §5 states "The expected channel is the server console over stdin". The console over stdin is write-only: the only feedback is log output — and the same sentence forbids using that as liveness ("a log-line match may serve only as the *readiness* signal (world loaded), never as liveness"). So in the expected configuration the fallback is either unimplementable as written or requires an unstated per-check fresh-response convention (which command is sent? `save` every 30 seconds has side effects; a no-op command is not named). Two reasonable implementations diverge in what the operator observes and in what the server does under a healthcheck.

The same channel is also asserted to carry player count: "serving state and player count come through the mediation channel when the query protocol is off" — but PZ §2's own fact says only "RCON provides `save`, `quit`, and server messages." Player count over that channel is nowhere established, and unlike every neighbouring uncertainty it is not one of the (a)–(h) open items. Root §5.5 makes the "is it serving, and how many players" capability a **must**, so the fallback path is load-bearing for a must.

This is not a corner case: PZ §6 states "A **non-Steam configuration is supported**" and that configuration "silences the query protocol entirely", so it *always* lands on this fallback.

*Direction:* either restrict the fallback to a request/response channel (making internal RCON mandatory whenever the query protocol is unavailable), or add "can the console channel answer a status query non-destructively, and can it report player count" as an explicit open item with a stated consequence if it resolves unfavorably.

### F3 — important — root §5.2, PZ §5

Root §5.2's bind rule is unscoped: "The image's shipped or effective configuration must make the game listen on `0.0.0.0` wherever the bind address is configurable". Its stated reasoning is about port publication, and the next bullet handles admin interfaces separately — but nothing exempts admin interfaces from the rule. Meanwhile PZ §5 requires the opposite for the entrypoint's own listener: "the listener binds **loopback only** — 'unpublished port' is no protection under host networking or a shared network namespace". Root §6 says a per-game document "never weakens a must", so as written PZ §5 is in conflict with a root must.

Worse, the ambiguity has a security consequence for the *operator's* RCON, whose bind address PZ never states: an implementer applying root §5.2 literally binds PZ RCON to `0.0.0.0`, which under host networking or a shared namespace is precisely the "silently owned server" the next bullet warns about.

*Direction:* scope the `0.0.0.0` requirement to player-facing/published ports and state the bind expectation for admin interfaces explicitly (loopback unless the operator publishes them deliberately).

### F4 — important — root §8, root §2

Root §8 makes the scheduled refresh a must and grounds it strongly: "Once games are baked in, this refresh is the *only* path by which security patches reach game images … The cadence is the implementation's choice; the mechanism is not." But §2 records no environment constraint about the scheduler itself, and GitHub Actions disables `schedule`-triggered workflows in a public repository after roughly 60 days without repository activity. A specification repository that is finished and stable is exactly the repository that sees no commits for two months — at which point the only patch path stops running, with the images still pulling and still passing every check. That is the document's own failure shape (silent, discovered late) attached to its own security mechanism.

Whether the refresh's "advances the pinned builder reference" produces a repository commit — and thus resets the clock — is left to the implementer, so the outcome is not even predictable.

*Direction:* record the deactivation behavior as an environment fact in §2 and require the refresh mechanism to be resistant to it (e.g. the refresh must produce repository activity, or the scheduler must be outside the repository's activity clock), plus a way for the operator to notice that the refresh has not run.

### F5 — important — root §8

Update detection has no loud-failure path: "a periodic job compares each game's current Steam buildid (§2.3) against the buildid label of the newest published image (§5.8) and, on **any** buildid change, builds and publishes automatically". Nothing says what happens when the comparison cannot be made — Steam unreachable, the query returning nothing, the newest published image carrying no buildid label (a hand-built or pre-label image), a label that does not parse. The natural implementation of an unparseable comparison is "no change detected, exit 0", which is a green job that has silently stopped detecting updates, producing the exact harm §8 names two bullets later: "leaving same-version content updates unpublished would silently strand servers on stale builds instead."

Compare §7, which does exactly the right thing for its own risk ("must fail the job, never proceed"). The asymmetry looks like an oversight rather than a choice.

*Direction:* require the detection job to fail loudly when it cannot establish both sides of the comparison, and state that "cannot compare" is never treated as "no change".

### F6 — important — root §5.1, PZ §1, root §3.4

Root §5.1 says "The image must honor `$HOME` when the game derives paths from it, and must document whether it does." That sentence is a requirement and its own opt-out in one breath — "must honor" and "document whether it does" cannot both be the rule — and PZ takes the second reading, pinning the state root independent of `$HOME` and setting `$HOME` itself: "the image sets `$HOME` itself to a documented location **inside the state root**, because the Steam client link farm and JVM crash dumps may land under it".

The gap this leaves is operationally live: neither document says what happens when the *operator* sets `HOME` (a one-line `environment:` entry in compose, and a common one). Does the image's value win, or the operator's? Under `--read-only` with only the state root and `/tmp` writable, an operator-set `HOME` points the Steam client link farm and crash dumps at a read-only path — and the failure mode of a missing `~/.steam/sdk64` link farm is precisely the one root §2.7 warns is the classic first-build failure, which can present as a server that runs but never registers with Steam rather than as a crash. PZ requires a loud fatal for an unwritable *state root* but says nothing about `$HOME`.

*Direction:* decide whether the image's `$HOME` is fixed (operator override ignored, or refused loudly) or honored, state it, and if honored extend PZ §1's writability fatal to cover `$HOME`. Also disambiguate the root §5.1 sentence into a single rule.

### F7 — important — PZ §4, PZ §2

The entire first-boot design rests on a mechanism that is never stated as a fact. PZ §4's table row reads "Create the admin account via the game's non-interactive mechanism (`ADMIN_PASSWORD` wins if both are set — it states desired state); start". But PZ §2's facts say only "Admin credentials live in the server database, created on first boot. With no database and no admin password provided, the server **prompts interactively** — in a container, a silent hang." That a non-interactive *creation* path exists is assumed; and the document's own diligence makes the omission conspicuous, since the analogous *change* on an existing account is called out as open item (d).

If the assumption is wrong, the entrypoint cannot pre-empt the prompt and the container hangs — the exact failure the table exists to prevent — with the only mitigation being the healthcheck eventually going unhealthy after `start_period`, which PZ §6 sizes for minutes of world generation.

*Direction:* promote the non-interactive account-creation mechanism to a stated §2 fact (or to an open item with a stated consequence if it does not exist), and consider requiring the entrypoint to fail loudly rather than hand over to a game that may prompt.

### F8 — important — PZ §7, PZ §2 item (g), root §3.4

Open item (g) identifies a collision but stops short of resolving it: "if the target turns out to be the shipped game directory, it collides with the world-readable-not-writable content rule (root §3.4) and the read-only rootfs (§1), so the answer reshapes §7". Root §3.4 is not a "should" here — "All state is written under `$HOME` or under the image's documented state paths — never into the shipped game directory" — and root §6 forbids the per-game document from weakening a must. So if (g) resolves unfavorably, the implementer faces a root must with no sanctioned escape and no stated preference among the plausible responses (relocate the mod tree into the state root via configuration or a link; declare the game directory writable and abandon the read-only claim; refuse to support workshop mods). Those choices differ in exactly what an operator observes: the documented writable-path set, the read-only claim the §8 smoke test asserts against, and whether mods survive a container replacement.

"Reshapes §7" is a note to self, not a decision, and this is the one open item whose unfavorable resolution puts the image in violation rather than merely on a fallback.

*Direction:* state the required response now — most plausibly, the mod target must end up inside the documented state root by configuration or relocation, and if that proves impossible the deviation must be documented and the read-only claim narrowed rather than the §3.4 rule bent.

### F9 — important — root §5.6, PZ §3

Root §5.6 requires "an **operator-settable stop timeout** (an environment variable with a documented default)" and the binding rule "**the timeout must sit below the runtime's stop grace period**", while also recording that "Docker's 10-second default is a save-corrupting trap for game servers." Nothing says which way the shipped *default* should err, and the two defensible choices are opposite. A default aligned with the recommended 90-second grace violates the binding rule on every unmodified `docker run` (SIGKILL at 10 s, mid-save); a default under 10 s satisfies the rule out of the box but truncates saves on the large Build 42 maps PZ §5 explicitly mentions. PZ §3 just says "Optional (documented default…)" and repeats the rule.

The mitigation the document does provide — the entrypoint printing its effective timeout at start and on stop — makes the resulting exit 137 attributable *after* a save has already been lost, and the entrypoint cannot read the runtime's grace period to warn in advance. For a document that treats this as its flagship silent failure, leaving the default unspecified is a guess the implementer should not have to make.

*Direction:* state the intended default and the reasoning for the direction it errs in, and say explicitly that the image cannot detect the grace period (so the burden is documentation plus the printed value).

### F10 — minor — PZ §3, root §5.3, root §6

Root §5.3 counts "the uid-0 opt-out of §3.4" as part of the sanctioned env surface, and root §6 requires the per-game document to list "every variable, its purpose, its mandatory-or-optional flag". PZ §3's table lists eleven variables including `STOP_TIMEOUT` but omits `ALLOW_UID0`. Separately, root §3.4 defines only the accepting values ("`1` or `true` (case-insensitive)") and not the behavior for `ALLOW_UID0=yes` or `=0` — the safe direction, but the operator gets the generic "use `--user`" fatal with no hint that their opt-out attempt was rejected as unparseable. *Direction:* add the variable to PZ §3; consider requiring the fatal message to mention a set-but-unrecognized `ALLOW_UID0`.

### F11 — minor — PZ §3

The heap guard's justification and its tier disagree: "the allowance is a number two implementations compute identically (a should-level starting point: the larger of 512 MB or 25% of the heap), not an adjective." Identical computation across implementations is a must-shaped property; a should-level value is by definition deviable. *Direction:* keep the value at should level but make the must be "a documented, deterministic number", or promote the formula.

### F12 — minor — PZ §2, root §5.5

Root §5.5 requires the documentation to state "**who rotates which file** — an unrotated log the operator does not know about fills the state disk slowly and silently, and a full state disk corrupts saves." PZ §2 acknowledges the obligation ("log-file rotation ownership must still be documented") but whether the PZ server rotates or caps its own log files is neither a stated fact nor one of the (a)–(h) open items — so the implementer has no input from which to write the required sentence, in a design where those logs share the state root with saves and native backup archives. *Direction:* add it to §2 as a fact to verify.

### F13 — minor — root §8

The refresh is described in an order that advances the pin before anything proves the new builder works: "it publishes a fresh builder date tag, **advances the pinned builder reference** the game builds use (§3.1 …), and rebuilds every game image against the refreshed base and builder." A broken builder date tag therefore leaves the repository pinned to it after the rebuilds fail, blocking every subsequent on-demand game build — including an urgent one. Failures are loud (the jobs fail), which keeps this minor. *Direction:* state that the pin advances only on successful game rebuilds, or that a failed refresh must restore the previous pin.

### F14 — minor — root §3.2, §7

"registry storage is cheap" is asserted as part of the baked-image trade-off, and §7 makes every immutable `-rN` permanent by construction, while §8's refresh mints a new revision of every multi-gigabyte game image on an unspecified cadence. The document takes no position on retention of superseded immutable tags — and it cannot simply be "delete old ones", since §7's whole promise is that consumers pin them. *Direction:* one sentence on the retention stance (unbounded and deliberate, or a stated policy), so the implementer does not invent a cleanup job that breaks pinning.

### F15 — minor — root §5.6, PZ §6

A stop signal arriving during world load (minutes, per PZ §6) is covered by the table only via the timeout row: mediation fails because the console is not up, the entrypoint waits out the full `STOP_TIMEOUT`, terminates, and exits non-zero. That is defensible but means an intentional `docker compose down` shortly after start produces a slow shutdown and a failure exit code that a `restart: on-failure` policy will act on, for a shutdown that risked nothing. *Direction:* either confirm this is intended, or let the entrypoint treat "stop before the game was ever ready" as a distinct, fast, clean case.

## 3. Questions for the operator

1. **F1:** which is authoritative — the prose definition or the table? Specifically, should a game that exits with a non-zero status of its own accord after `quit` exit 0 or non-zero?
2. **F4:** where will the CI live, and does the scheduled refresh commit the advanced builder pin back to the repository? The answer determines whether the 60-day scheduled-workflow deactivation applies.
3. **F9:** which way should the shipped `STOP_TIMEOUT` default err — safe under Docker's 10-second default, or matched to the recommended 90-second grace?
4. **F6:** is the image's `$HOME` fixed (operator override ignored/refused) or honored?
5. **F2/F7:** should PZ's open-item list grow to cover (i) non-interactive admin-account *creation*, (ii) a non-destructive status/player-count query over the console channel, and (iii) PZ's own log rotation? All three are load-bearing for a root must and all three are currently assumed rather than flagged.
6. **PZ §2:** the claim "Build 42 is the stable branch since 2026-07-29 (version 42.20)" is the premise of the whole first game and postdates what I can independently corroborate. Was it verified against Steam directly on 2026-08-12, or from community sources? If Build 42 is not in fact the default branch, root §7's no-branch-axis rule and root §11's B41 non-goal both need revisiting.
7. **F3:** is the `0.0.0.0` bind requirement meant to apply to admin interfaces, and what bind address should operator-enabled RCON use?

## 4. Verdict

1 blocking, 8 important, 6 minor. Not a quiet round: F1 is an internal contradiction in the document's most consequential contract, and F2–F9 are places where two competent implementations would diverge in what the operator can observe.
