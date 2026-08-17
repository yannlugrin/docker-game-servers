# Review 001 — Challenge (premise audit), 2026-08-12

Spawn: general-purpose, worktree isolation, session model (Fable 5).
Inputs: SPECIFICATIONS.md + .claude/spec-work/decisions.md (first complete draft, commit cc7aa40).

---

Both documents read in full. Scope of the audit before the challenges:

- **Foundational decisions:** D-001, D-002, D-003, D-004, D-008 — all selected.
- **No-reasoning findings:** none. Every entry carries a "Why" and premises.
- **Staleness:** every decision and the specification carry the same date (2026-08-12, today), so no decision is old relative to project drift. No target selected on this criterion.
- **Premise erosion / neutralized benefits:** two non-foundational entries selected on these criteria — D-012 (neutralized-benefits pattern) and D-011 (premise partially contradicted by §6.3). D-011 was examined and dismissed without a challenge: its load-bearing premise (credentials injectable at startup without disk persistence) holds for the case that matters (PZ first boot), and the one hole — post-first-boot `ADMIN_PASSWORD` may be un-appliable — is already explicitly designed for in §6.3 row 4. Raising it would be manufacturing a finding the spec has already closed.

Two challenges survive honest application of the zero-based test. Both end in reaffirmation, one with a required re-grounding of the recorded rationale.

---

## Challenge 1 — D-003, "Game files baked into the image at build time" (with the shared premise in D-002)

**Original reasoning and premises.** D-003's "Why" opens: *"the target platform's contract requires the tag to say which game version is inside and pins images by digest."* D-002's premises likewise state: *"the deployment platform pins digests and never updates in place."* The architecture's most foundational choice is recorded as resting on the contract of a specific, unnamed deployment platform.

**What undermines it.** The specification has since scrubbed that platform out of existence as a design input. §1: images *"must not name or assume any specific hosting platform"*; §9 requires all documentation to stay platform-neutral. The images are now generic public images whose consumers may or may not pin digests — the recorded premise ("the platform pins digests") is not a fact about the current project; it is a fact about a platform the project no longer assumes. A secondary erosion: D-003's decision text says flatly *"Nothing is downloaded at container start,"* while D-010/§6.6 now has the game downloading workshop mods at startup, reintroducing — for modded servers only — the Steam-connectivity-at-start and slow-first-start costs that D-003's "Why" counts among the benefits of baking.

**Zero-based answer.** Knowing only what the documents now contain, the same decision is made, on grounds the spec itself already states platform-neutrally in §3.2: runtime installation gives a meaningless tag, unreproducible content, and minutes-long cold starts regardless of who consumes the image; honest `<game-version>-rN` tags are what make §7 and §8 coherent. The mod exception does not tip it: mods are server state (D-010's framing is correct), and the game-version guarantees hold for vanilla and modded servers alike. Baking wins zero-based, without any platform in the picture.

**Recommendation: reaffirm** — but re-ground the recorded rationale. The decision survives; its written justification does not. The log entries for D-002 and D-003 should cite the platform-neutral reasoning of §3.2 (honest tags, digest-pinnable content, fast start) and drop the "target platform's contract" premise, so a future audit doesn't find a foundation resting on a premise the spec forbids assuming. The "Nothing is downloaded at container start" sentence should be narrowed to match the §1/§6.6 carve-out.

**Cost asymmetry.** Reversing baking later is the most expensive flip in the project — it invalidates the tag scheme (§7), the CI model (§8), the smoke test, and two non-goals (§11). Re-grounding the rationale now costs two paragraphs in the log. Maximal asymmetry in favor of settling it now: reaffirmed on corrected grounds.

---

## Challenge 2 — D-012, the shipped RCON client (neutralized-benefits pattern)

**Original reasoning and premises.** D-012 ships two static clients. The query client is justified by the healthcheck. The RCON client's recorded justification: *"justified independently: PZ does not handle SIGTERM natively… so clean shutdown needs an in-image mediation tool anyway"* — i.e., the entrypoint's stop mediation is the reason it exists.

**What undermines it.** Requirements accumulated since have cancelled that primary benefit, each step locally reasonable:

1. §6.1 (fact): PZ's RCON is *"enabled only when an RCON password is configured."*
2. §5.6 (requirement): mediation *"must work regardless of optional operator configuration — a stop that only works when the operator happened to enable RCON is a stop that fails silently on default setups."*
3. §6.4 (consequence): the entrypoint must use the server console; *"RCON only as an alternative when configured."*

Net: the entrypoint cannot rely on the RCON client for its stated job, on the very first game. The remaining benefit — operator `docker exec` save/announce (§5.5) — is real but also only functions when the operator has set `RCON_PASSWORD`. This is exactly the pattern: the component is kept while its recorded raison d'être has been legislated away.

**Zero-based answer.** Would the RCON client still be shipped today, knowing all of the above? Narrowly yes, for the PZ image: it costs low megabytes, gives operators save/announce without exposing the RCON port, and remains a legitimate mediation *alternative*. But it would be shipped as an operator convenience with an explicit "only useful when RCON is enabled" caveat — not as shutdown infrastructure — and §5.5's existing drop-with-reason clause would govern it per game.

**Recommendation: reaffirm**, with the rationale rewritten. D-012's "Why" should state the surviving justification (operator convenience + mediation alternative) and delete the claim that clean shutdown *needs* it — because §5.6 now guarantees the opposite. Left uncorrected, a future game image's implementer reading D-012 could build RCON-dependent shutdown mediation, which §5.6 exists to forbid.

**Cost asymmetry.** Dropping or adding a static client later is a one-line image change and a revision bump (`-rN` exists precisely for this). Cheap to change later — which is the argument for reaffirming now rather than reopening.

---

## Decisions examined and reaffirmed without challenge

- **D-001 (monorepo):** premises intact; the future wine line (§10.1) adds a parallel base pair, mildly stretching "one base," but strengthens rather than weakens the shared-conventions argument. Zero-based: same choice.
- **D-002 (builder, not runtime base):** survives once its shared platform premise is re-grounded per Challenge 1; workshop mods are downloaded by the game itself, not steamcmd, so the runtime-steamcmd exclusion is untouched. Zero-based: same choice.
- **D-004 (debian:trixie-slim everywhere):** premises verified same-day; musl exclusion is forced for the builder and effectively forced for glibc-linked game binaries at runtime; the ~75 MB base is noise against multi-GB game payloads, so no lighter-base pressure exists even under the "as light as each game allows" goal. Zero-based: same choice.
- **D-008 (wine deferred):** premises hold — the first game is native Linux, and nothing in §3–§5 is Linux-binary-specific; the deferral's cost genuinely does not grow with time. Zero-based: same choice.

---

**Verdict: 5 foundational decisions examined (plus 2 pattern-selected non-foundational targets); 0 recommended for reopening — all reaffirmed, 2 of them (D-003/D-002 and D-012) contingent on re-grounding their recorded rationale in the decision log.**
