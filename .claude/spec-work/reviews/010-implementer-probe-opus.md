# Review 010 — Implementer probe, Opus, 2026-08-12

Spawn: general-purpose, worktree isolation, model: Opus, staleness guard
(worktree stale at 31e56c1; checked out 643b77b).
Inputs: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md at 643b77b.
Lens: implementer probe (plan-derived gap hunt).

Verdict: 0 blocking, 5 important (F1-F5), 5 minor (F6-F10).

---
I checked out `643b77b` (my worktree was stale at `31e56c1`, 12 commits behind) and verified HEAD before reading.

**Cross-reference check:** all `§N` / `§N.M` references in both documents resolve. Root references span §1–§11 including §2.1–2.8, §3.1/3.2/3.4, §4.1/4.3, §5.1–5.8, §10.1, §10.4 — every target exists. In `project-zomboid/SPECIFICATIONS.md`, bare `§1`–`§8` all resolve locally and every `root §N` / `Root §N` resolves in the root document. No dangling `D-0xx`, TODO, or placeholder markers remain.

## 1. Summary-back

A public GitHub repo publishing Docker images for dedicated game servers to GHCR, in two tiers. Tier one is a `steamcmd` builder image on Debian 13 slim, pre-warmed so its self-update is baked in, date-tagged because steamcmd has no versions, usable standalone by anyone as a "install a Steam app" build stage. Tier two is one runtime image per game, multi-stage: the builder stage (referenced by a *pinned* tag/digest) installs the game, the final stage starts fresh from slim and copies the game plus its runtime deps — including the Steam client libraries the game dlopens, which is the classic first-build failure. steamcmd never ships in a game image; the game is frozen at build time, so tags are honest and updates mean rebuilds.

Game images are conventions-first: uid-agnostic with no default user and a loud fatal on uid 0 (opt-out `ALLOW_UID0` for rootless runtimes), native config files as the authoritative interface with a small closed set of env vars as overrides, no secrets in layers or on stdout, every persistent path documented under one state root, a Steam-query HEALTHCHECK rather than a process check, and — the section the whole document orbits — a shutdown path where SIGTERM reliably reaches the game, the entrypoint mediates for games that ignore it, an operator-settable stop timeout sits below the runtime grace period, and exit 0 means a *confirmed* clean stop and nothing else. Everything that can fail silently (a `SIGKILL` mid-save, a leaked credential, a scheduled job that quietly stopped running, a moved immutable tag, an unrotated log filling the state disk) is required to fail loudly instead.

CI does on-demand builds, buildid-driven update detection, and a scheduled refresh that is the sole patch path into baked images — with a watchdog outside its own scheduler because GitHub disables idle schedules. Every game publish is gated by a smoke test under an arbitrary uid and a read-only rootfs. First game: Project Zomboid Build 42, whose per-game spec pins a fixed state root, sets `$HOME` inside it, resolves first-boot admin credentials with a decision table (the game otherwise prompts and hangs), mediates stop via console-or-internal-RCON, and carries thirteen dated open items to verify at implementation.

That reading matches what I'd build. Two places where I'd want confirmation my reading is the intended one are noted as questions 3 and 4.

## 2. Implementation plan sketch (scaffolding for the findings)

1. Repo scaffolding: root README, contributor guide, LICENSE (given).
2. Builder image: trixie-slim + `lib32gcc-s1` + CA certs + steamcmd, run once at build; an app-install capability taking app id / branch / beta password / validate.
3. CI: GHCR auth, publish first builder date tag. **← first external prerequisite (F3)**
4. PZ research pass: close the thirteen open items of PZ §2. **← F4, F5**
5. PZ Dockerfile: builder stage pinned to the tag from step 3, install 380870 from the default branch; runtime stage copies game + `steamclient.so` + native deps; world-readable modes; no USER; HEALTHCHECK.
6. Entrypoint: uid-0 gate → env parse/validate → state-root writability → heap-vs-cgroup guard → config override application **← F1** → admin-account branch (PZ §4 table) → exec/relay + reaping → stop mediation, timeout, exit-code table.
7. Query + RCON static clients; `docker exec` save/announce path.
8. Smoke test harness: arbitrary uid, `--read-only`, mounts at state root + `/tmp`, mandatory vars only, healthy-within-bound, stop, assert exit 0.
9. Workflows: on-demand build, buildid detector, unified refresh with pin advance, watchdog **← F2**, PR build-and-test.
10. Per-image READMEs, tag policy, backup recipe, upgrade warning.

## 3. Findings

**F1 — First boot does not define configuration-file genesis. (important; root §5.3 and §6; PZ §4)**
Root §5.3 says: "Environment variables are **optional overrides**: when set, the entrypoint / must apply them to the effective configuration at startup. When unset, / the configuration file's values stand." Root §6 requires the per-game spec to cover "**first boot**: what happens on a fresh state directory, with a decision / table wherever that branches dangerously". PZ's fresh state root has no INI at all — the game authors it on first run — and PZ §4's table branches only on the admin account. Two competent implementations diverge observably: one pre-writes/patches the INI before launching, so `GAME_PORT=17000` is effective on the first start; the other patches only an existing file and lets the game generate defaults, so the first start runs on 16261 — and because that port is *advertised* (PZ §2), the server registers with Steam on the wrong number for its entire first run, then silently changes on restart. That is precisely a dangerous branch with no row.
*Direction:* state the required outcome — overrides are effective on the first start on a fresh state root — and let the per-game spec say which of the game's own mechanisms delivers it (launch arguments, a pre-written file, a generate-then-patch-then-restart cycle). The mechanism can stay open; the first-start observable cannot.

**F2 — The refresh watchdog has no channel the implementer can supply on its own. (important; root §8, §2.8)**
§8 requires: "**a refresh that has not run within its cadence must surface / as a failing check in a channel that does not share the refresh's own / scheduler**", then "the watchdog must live outside the thing it watches (where / it lives is the implementation's choice)". Inside the repository, every candidate shares the failure mode §2.8 describes: a second `schedule` workflow is disabled by the same 60-day idle rule, and a `push`/`pull_request`-triggered check only reports when the repo is active — which is exactly when the refresh is not at risk. The remaining faithful options (an external dead-man's-switch service, an outside cron firing `repository_dispatch`) are delegated services with credentials only the operator can provide, and nothing in §8 or §9 lists them as a prerequisite. Left alone I would guess, and any guess I can make unaided either violates the stated constraint or needs a secret I do not have.
*Direction:* either name the class of channel the operator will provide (and add it to the deliverables/prerequisites), or say explicitly that an external monitoring endpoint is an accepted dependency with its secret handled like any other CI secret — or, if no external dependency is wanted, weaken the requirement to what is actually reachable in-repo and say so.

**F3 — §2.6's GHCR fact omits the manual visibility step, which is where §7's central promise lands. (important; root §2.6, §7)**
§2.6 states: "GHCR hosts public images free of charge, with / credential-less anonymous pulls and native GitHub Actions integration / (build and push in one workflow, no extra credentials)." §7 then requires images "published publicly on GHCR". The step between them is missing: a package first pushed by a workflow is not public — visibility is a per-package setting the repository owner flips outside the workflow. The result is the document's own failure shape: CI goes green, tags exist, labels are right, and no consumer can pull. §2 exists because "discovering them mid-implementation is expensive", and this one is discovered by a stranger, not by the build.
*Direction:* add the one-time visibility action to §2.6 as a fact and name it in §9's deliverables or in an operator-prerequisite line, with the step it blocks (first publish).

**F4 — Two facts root §6 requires are unresolved open items in the PZ spec, one admittedly so. (important; root §6, §7; PZ §2 items e and m)**
Root §6 requires the per-game spec to carry "**where the human-readable version string is read from** ... — it names the tags, §7" and "**what a game-version upgrade does to existing saves** (§5.7)". PZ §2 files both as open questions: "(e) where the **human-readable version string** is / authoritatively read from — the game's own files, Steam metadata, or a / build input — since it names the image tags (root §7)" and "(m) **what a Build 42 point release / does to an existing world** — migrate, invalidate, or regenerate — the / researched answer behind §8's upgrade warning (root §6 requires it as a / fact, not just the warning)." The document names its own non-compliance on (m), which is honest, but leaves an implementer holding two obligations that are not "re-verify a stated fact" — they are original research, and (m) in particular may have no authoritative answer to find. Item (e) additionally gates CI: root §7's buildid-derived fallback applies only "Where a game exposes **no machine-readable version string**", and the per-game spec is required to state "which naming its tags use" — which it cannot until (e) closes. So the tag scheme for the first game is undetermined at the moment CI is written.
*Direction:* close (e) before implementation, or pre-commit the fallback ("if no authoritative version-string source is found by <criterion>, PZ tags are buildid-derived"). For (m), state what the implementer does when research is inconclusive — a documented "unknown, assume irreversible, back up" is a legitimate resolution and better than an open item.

**F5 — Two open items carry a "must" but no stated response if they resolve unfavorably, unlike the rest. (important; PZ §2 items f and i; PZ §6)**
The open-item list is otherwise disciplined: (c) falls back to internal RCON, (d) makes the override fatal, (g) fixes the required response, (k) is "absorbed by §6's fallback order", (l) says the image "**must not ship on that combination**". Two are not. Item (f) asks "how a / **non-Steam configuration** is detected from the effective settings", while §6 states as a must: "The / healthcheck must detect that from the effective configuration (§2, open / item f) and switch to the same fallback order automatically". If detection turns out not to be derivable from the effective settings, the must is unsatisfiable and the only escapes — an operator-set env var, or dropping non-Steam support — are respectively discouraged by root §5.3 ("The image must not invent environment variables") and unstated. Item (i) asks whether the mediation channel "can answer a **status and player-count query / non-destructively**"; root §5.5 makes that capability a must, and §6 routes it through the mediation channel whenever the query protocol is off. Neither item says what happens on a "no". A third corner falls out of the same seam: if (a) and (b) both resolve unfavorably the healthcheck needs a request/response channel, which is RCON; but §5's loopback constraint and item (l)'s must-not-ship clause are written only for the *mediation* combination (c unusable **and** l no-loopback), not for the healthcheck-needs-RCON-but-RCON-cannot-bind-loopback combination.
*Direction:* give (f) and (i) the same treatment the others already get — a named response for the unfavorable resolution — and extend (l)'s must-not-ship / fallback reasoning to cover the case where the *healthcheck*, not the stop path, is the thing that requires the channel.

**F6 — Scope of the `ALLOW_UID0` unparseable-value fatal is ambiguous. (minor; root §3.4, §5.3)**
§3.4 says `0` and `false` are recognized as off, then "any *other* value is unparseable and follows §5.3's validation rule — the fatal message names / the variable and the rejected value, so an operator whose opt-out attempt / was mangled is not left staring at the generic message". The closing clause implies the uid-0 context (where "the generic message" would otherwise fire), but §5.3's rule is written for the whole env surface with no uid condition. So: does `ALLOW_UID0=yes` under `--user 1000:1000` abort the start, or is it inert? Two implementations diverge on a start that either works or refuses.
*Direction:* one sentence saying whether the parse check is unconditional or evaluated only on the uid-0 path.

**F7 — Builder-image publishes are ungated while the builder is a public product. (minor; root §8, §4.1)**
§8 gates game images: "**A smoke test gates every game-image publish**". Nothing gates a builder publish, yet §4.1 makes the builder "usable on its own as a generic 'install a Steam app' builder by anyone". A broken steamcmd layer therefore reaches a public date tag and `latest` with no check; the refresh's pin-advance guard protects this repository's game builds but not outside consumers. Whether to add a builder-side check is a decision two implementers would make differently.
*Direction:* either state that builder publishes are deliberately ungated (with the blast radius, as §11 does elsewhere), or name the minimal assertion — steamcmd runs and completes an anonymous app_info query.

**F8 — The PZ spec never states whether the player-facing ports honor the `0.0.0.0` requirement. (minor; root §5.2, §5 preamble; PZ §2)**
Root §5.2: "For **player-facing ports**, the image's shipped or effective / configuration must make the game listen on `0.0.0.0` wherever the bind / address is configurable; a game that binds narrower and cannot be told / otherwise is documented as a limitation." Root §5's preamble requires the per-game spec to document "how each convention is honored". PZ §2's networking bullet gives ports, defaults, protocols and the advertised flag but is silent on bind address; open item (l) covers RCON's bind address only. The root rule is deterministic once the fact is known, so this is a missing fact rather than an ambiguity — but it is the one bind-address question the open-item list skipped.
*Direction:* record it as a fact, or add it to the open-item list alongside (l).

**F9 — Builder date-tag ordinal is underspecified. (minor; root §7)**
"date-stamped tags (`YYYYMMDD`, with an ordinal / suffix — `YYYYMMDD.N` — when the same day sees more than one build, so / no immutable tag is ever reused)". Whether the second build of a day is `.1` or `.2`, and whether the bare tag is conceptually `.0`, is a guess. The never-reuse invariant plus §7's loud overwrite failure make every guess safe, so this is cosmetic — but it is a guess I would have to make.
*Direction:* one clause fixing the starting ordinal.

**F10 — Docker Hub's rate limit is recorded only as a publishing consideration, not as a build-time dependency. (minor; root §2.6, §3.1)**
§2.6 notes "Docker Hub / rate-limits anonymous pulls" as a reason to prefer GHCR for publication. But §3.1 bases every stage on `trixie-slim`, which CI pulls anonymously from Docker Hub on every on-demand build, every buildid-triggered build, and every refresh rebuild of every game — from shared-IP hosted runners. That is the same fact pointing the other way, and it fails as an intermittent CI error rather than a design problem, which is exactly the kind of mid-implementation surprise §2 exists to prevent.
*Direction:* note the consumption side in §2.6 so the implementer can decide on a registry mirror deliberately rather than after the first throttled build.

## 4. Questions for the operator

1. Which channel should the §8 refresh watchdog use, and will you supply its credential — or is an in-repo, push-triggered staleness check an accepted (weaker) reading of "does not share the refresh's own scheduler"? (F2)
2. Who flips the GHCR packages to public, and at what point in the sequence? (F3)
3. Am I to research and close PZ §2's thirteen open items myself before writing code, or do you arbitrate the load-bearing ones (a, c, d, e, g, m) first? Several change the environment surface and the tag scheme, not just an internal detail. (F4, F5)
4. On a fresh state root with no mounted configuration, must `GAME_PORT` / `DIRECT_PORT` / `SERVER_PASSWORD` be effective on the *first* start, or is first-start-defaults-then-effective-on-restart acceptable? (F1)
5. §8 leaves the refresh cadence to the implementation — is weekly acceptable, or do you have a target?
6. Is `ALLOW_UID0`'s value parsed unconditionally, or only when the container is actually running as uid 0? (F6)
7. Do you want any gate on builder-image publishes? (F7)
8. Confirming that the concrete PZ state-root path, the `MAX_HEAP` default, and the `start_period` value are genuinely mine to choose and document, since all three become permanent operator-facing interface.

## 5. Verdict

0 blocking, 5 important (F1–F5), 5 minor (F6–F10). Not a quiet round: the document is unusually disciplined and I found no contradictions or unreasoned musts, but F1 leaves a dangerous first-boot branch without its row, F2 and F3 are external prerequisites an unsupervised implementer cannot supply, and F4/F5 leave required facts and unfavorable-resolution responses open at points where the implementation must commit.
