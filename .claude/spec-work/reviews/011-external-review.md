# Review 011 — External review (user-run, other AI platform), 2026-08-12

Source: report pasted back by the user; packet from
.claude/spec-work/external-review-prompt.md; inputs at commit be8158e.

Reviewer verdict: 2 blocking, 2 important, 1 minor; cross-references all
resolve.

Triage (main session, user-approved): F1 accepted as fact completion
(cgroup v2 `max` = no limit; severity overstated — "no limit readable"
already covered it); F2 accepted as important with a simpler fix (the
entrypoint discovers INI-configured RCON from the effective INI it already
manages; no §5.3 exemption needed); F3 partially accepted — the claimed
paradox misreads the existing idempotent-creation clause, but the
asymmetric proxy (missing db proves absence; present db proves nothing) is
now spelled out; F4 accepted as a permissive tini-class note (the shell
reaping claim is overstated — a shell blocking in wait reaps reparented
children — but naming the one expensive mechanism choice is worth it);
F5 accepted (hot copy can catch a native archive mid-write). Reviewer Q1
answered by the §8/§10.7 deferral (user ruling); Q2 accepted as an entropy
requirement on the ephemeral internal-RCON password.

---

## Report as received

1. **Summary-back**
This specification defines a framework for creating production-ready, zero-surprise Docker images for dedicated game servers, starting with Project Zomboid. It heavily prioritizes operational safety, strictly mandating explicit over implicit behaviors to prevent silent state corruption or credential leakage. The architecture uses a shared Debian-slim steamcmd builder to bake game binaries into immutable, uid-agnostic runtime images. These runtimes are fronted by a minimal entrypoint responsible for startup validation, configuration injection, signal translation (clean shutdown mediation), and lifecycle supervision, leaving orchestrational duties (backups, scheduling) to the operator. Automated CI flows manage updates, tag immutability, and security patching.

2. **Findings**

**1. [blocking] PZ §3 — cgroup v2 `max` string causes shell crash**
Evidence: "An implausibly large reported limit (cgroup v1 reports a near-maximum value for 'unlimited') counts as no limit."
Direction: Debian 13 slim uses cgroup v2 by default; unlimited returns the literal string `max` in /sys/fs/cgroup/memory.max. An implementer parsing it as a number crashes. The specification must explicitly mandate handling the string `max`.

**2. [blocking] Root §5.3 vs PZ §5 — RCON mediation blinded by mounted INI**
Evidence: Root §5.3 requires images to be "fully operable with a mounted configuration and no game-specific environment variable set". PZ §5 mandates the entrypoint must reuse the operator's configured RCON to mediate shutdown.
Direction: If the operator defines RCON port/password only in the mounted INI, the entrypoint does not know how to connect to mediate save/quit; the timeout silently SIGKILLs. Mandate the entrypoint parses the native configuration at shutdown, or exempt RCON parameters from root §5.3 and force them env-driven.

**3. [important] PZ §4 — The SQLite admin database observation paradox**
Evidence: PZ §4 forbids checking account existence via "the mere existence of files" yet demands fatal-before-start when the account doesn't exist and no credential is set.
Direction: Observing the account requires querying SQLite; the slim runtime lacks sqlite3 and the spec doesn't mandate it. Relaxing to allow checking the per-SERVER_NAME db file resolves it without tool bloat.

**4. [important] Root §5.6 — Zombie reaping via thin shell entrypoint**
Evidence: "either the game binary is PID 1... or the entrypoint remains PID 1... it must reap orphaned child processes"; PZ §5 establishes the game cannot be PID 1.
Direction: Shell scripts do not reap orphaned grandchildren natively; an AI agent will hallucinate complex buggy traps. Recommend or permit a lightweight init (tini/dumb-init) as true PID 1, delegating signal translation to the entrypoint.

**5. [minor] Root §5.7 vs PZ §8 — Hot copying native backups**
Evidence: PZ §8 "copying the state root gets them for free" vs root §5.7's hot-copy warning.
Direction: A hot copy can capture a native archive as the game writes it. Clarify operators must coordinate copies with the archive schedule or copy archives out separately.

3. **Questions for the operator**
1. If the update workflow goes idle and is disabled by GitHub (root §2.8) with the external watchdog deferred (§10.7), how does the project reliably detect the failure before an unpatched server is compromised?
2. On the loopback internal RCON, if the game's RCON lacks rate limiting, does the ephemeral password provide sufficient entropy against brute force from a compromised container sharing the network namespace?

4. **Verdict**
2 blocking, 2 important findings; the document is highly mature but requires targeted architectural rescues before unsupervised implementation.

Every `§N`/`root §N` cross-reference I followed resolved to an existing section.
