# Review 009 — Challenge checkpoint 2 (premise audit), 2026-08-12

Spawn: general-purpose, worktree isolation, session model (Fable 5),
staleness guard (checked out a2b2138).
Inputs: SPECIFICATIONS.md + project-zomboid/SPECIFICATIONS.md +
.claude/spec-work/decisions.md at a2b2138.

Verdict: 6 foundations examined (+2 criteria-selected non-foundational);
0 reopened — all reaffirmed; D-015 and D-012 log entries to re-align with
the specification, D-016 premise patched, §10.6 gains the §5.8 label in
its swap list.

---
Checked out `a2b2138` (detached HEAD) before reading anything; all three documents plus the eight archived review rounds were read at that commit.

# Premise audit — foundations at a2b2138

**Target selection.** Foundational decisions: D-001, D-002, D-003, D-004, D-008, D-016 — all examined. No decision lacks recorded reasoning (no automatic findings). All entries carry the same date (2026-08-12), but the five reaffirmations from challenge 001 were made against the *first draft* (cc7aa40), before reviews 002–008 reshaped the specification — so every foundation was re-tested against the current text, and D-016, added after challenge 001 and never challenge-tested, got particular attention. Premise-erosion and neutralized-benefits sweeps across the non-foundational entries selected D-015 (premise directly contradicted by the current spec) and D-012 (the pattern challenge 001 already flagged, evolved further since). D-011 was examined and dismissed again on the same grounds as challenge 001: its non-persistence premise was always conditional ("where the game permits"), and PZ §3 now documents the failure of that condition explicitly rather than hiding it.

Three challenges survive the zero-based test honestly applied. All three end in reaffirmation.

---

## Challenge 1 — D-015, "No default user; the entrypoint refuses uid 0"

**Original reasoning and premises.** The entrypoint exits fatally on uid 0; "an explicit uid choice is mandatory to run the image." The Why explicitly records the rejected alternatives: "Rejected: non-root default uid …, root default with docs …, **escape hatch env (would be cargo-culted)**."

**What undermines it.** The current specification mandates exactly the rejected escape hatch. Root §3.4 defines `ALLOW_UID0` as "one documented opt-out," §5.3 lists "the uid-0 opt-out of §3.4" as part of the sanctioned env surface, and PZ §3's table carries the variable. The opt-out was introduced by review 006 F5 (rootless Podman and default-`runAsUser` Kubernetes land on in-container uid 0, where it maps to an unprivileged host user and the root-owned-files reason does not hold) and refined by reviews 007/008 (unparseable values, recognized negatives). The log entry was never amended — unlike D-009 and D-012, which carry amendment notes, so this is a lapse in the log's own convention. The decision log and the specification now assert opposite things about the same mechanism.

**Zero-based answer.** Knowing the rootless/userns facts now in §3.4 and review 006, the choice made today is the spec's current form: no default user, fatal on uid 0, plus a single loudly-documented opt-out whose setting *is* the deliberate choice. The original entry's fear (cargo-culting) is answered by the design, not ignored by it: the opt-out is scoped, its documentation names the only legitimate cases, and unparseable values are fatal. The log's recorded form — refusal with no opt-out — would not be chosen today, because it makes the image unbootable on runtimes §1 promises to support ("any orchestrator").

**Recommendation: reaffirm** the decision as the specification now states it — and amend D-015's entry: record the rootless/userns premise, the `ALLOW_UID0` opt-out, and narrow the "escape hatch rejected" clause to what actually remains rejected (an undocumented or default-on escape). The spec is right; the log is stale.

**Cost asymmetry.** Amending the entry is a paragraph now. Left as is, the log is the document a future maintainer consults for *why* — and it currently instructs them that the one mechanism rootless deployments depend on was deliberately rejected. The likely failure is someone "cleaning up" `ALLOW_UID0` as unauthorized drift, breaking every rootless/K8s deployment at once. Cheap now, expensive and confusing later: fix the log now.

---

## Challenge 2 — D-012, the shipped RCON client (neutralized-benefits pattern, second iteration)

**Original reasoning and premises.** As amended after challenge 001: the RCON client is "an operator convenience — save/announce via `docker exec` without exposing the RCON port — and a shutdown-mediation *alternative* where the operator configured RCON," explicitly "**not** shutdown infrastructure."

**What undermines it.** The erosion continued through reviews 005–008, and the recorded rationale again lags the spec — but this time the drift runs in the component's *favor*. PZ §5 now requires the exec save/announce capability to work "**regardless of `RCON_PASSWORD`**" through the entrypoint's own mediation channel — so the client's recorded justification (exec convenience) has been reassigned to the mediation channel, and PZ §6 confines the client to "useful to operators only when operator RCON is enabled." Read against the log alone, the client is a component whose every recorded benefit has been legislated away — a textbook candidate for §5.5's drop-with-reason clause. But the same reviews gave it a new, contingent load-bearing role the log never mentions: if console-over-pipe fails (PZ §2 item c), stop mediation becomes entrypoint-managed internal RCON (PZ §5); if the query protocol is off or A2S fails to track serving state (items f, i, k), the *healthcheck itself* falls back onto that RCON channel (PZ §6). In those branches the shipped RCON client is precisely the infrastructure the image's flagship guarantees run on.

**Zero-based answer.** Ship it. It costs low megabytes, and until open items c/f/i/k/l resolve, the image cannot know whether the client is a convenience or the backbone of stop mediation and health probing. A zero-based designer reading only the current documents would ship both clients for exactly that reason.

**Recommendation: reaffirm**, with the rationale rewritten a second time: the RCON client's strongest current justification is the contingent fallback role (internal-RCON mediation and probe channel), with operator convenience secondary. As recorded, D-012 invites a future game image to drop the client under the drop-with-reason clause in exactly the configuration that needs it.

**Cost asymmetry.** Adding or dropping a static client later is a one-line change and a `-rN` revision bump — the cheap side of the ledger, which is the argument for reaffirming now rather than reopening. The log fix is a sentence.

---

## Challenge 3 — D-016, "Non-Steam games are a Future Consideration"

**Original reasoning and premises.** Deferral is safe because "§5 names no Steam mechanism as a must except the game-protocol probe, which is protocol-generic in intent (made explicit in §10.6)."

**What undermines it.** The premise is no longer exactly true. §5.8 — a must — requires every game image to carry "the **Steam buildid and branch** the game was installed from," and §8's update detection is keyed to that label. §10.6's swap list names the build stage, CI's update detection, and the healthcheck protocol — but not the §5.8 label requirement, which a non-Steam image cannot satisfy as written. This grew after D-016 was logged: reviews 002/004 hardened the buildid label from tag detail into the machine-readable spine of §8's comparison.

**Zero-based answer.** The same decision, without hesitation. The deferral's core claim — a non-Steam game arrives as a new directory touching nothing existing — survives: the buildid label generalizes trivially to "the per-game version-source identifier" (§7 already has the buildid-derived tag fallback showing the shape), and nothing must be built now. The premise has a small factual hole; the decision does not.

**Recommendation: reaffirm.** Optionally patch the hole at near-zero cost: add the §5.8 label to §10.6's list of pieces that swap per non-Steam game, and soften D-016's premise to "no Steam mechanism §10.6 does not account for."

**Cost asymmetry.** Nothing is being built either way; the cost of the label generalization is identical now or later. That symmetry is itself the argument for reaffirming — deferral genuinely does not grow more expensive by waiting, which was the decision's whole point.

---

## Foundations examined and reaffirmed without challenge

- **D-001 (monorepo):** premises intact; D-014's per-game specification files and §10.6's per-game builder stages stretch "one pipeline" mildly but strengthen the shared-conventions argument. Zero-based: same choice.
- **D-002 (builder is a build stage, not a runtime base):** re-grounded per challenge 001 and the log absorbed it ("corroborating, not load-bearing"). Seven review rounds added nothing that would want steamcmd at runtime — PZ's mods are game-downloaded (D-010), and §2.7's steamclient.so trap is handled by the multi-stage copy. Zero-based: same choice.
- **D-003 (game baked at build time):** the strongest confirmation in the archive — review 004 F6 *promoted* the scheduled refresh to a must precisely because baking makes it the only patch path, i.e. the spec paid baking's cost deliberately rather than eroding its benefit. §8's watchdog, the never-re-patch rule, and the smoke test all assume baking and cohere around it. Zero-based: same choice.
- **D-004 (debian:trixie-slim everywhere):** premises hold; §2.9 honestly downgrades the size claims to expectations-to-measure, which moves numbers, not the architecture. Zero-based: same choice.
- **D-008 (wine deferred):** §10.1 unchanged across all eight rounds; nothing in §3–§5 grew Linux-binary-specific. Zero-based: same choice.

---

**Verdict: 6 foundational decisions examined (plus 2 criteria-selected non-foundational entries, D-012 and D-015); 0 recommended for reopening — all reaffirmed, with two decision-log entries (D-015, D-012) requiring their recorded rationale brought back in line with the specification, D-015 being the urgent one since its log text and the spec currently contradict each other.**
