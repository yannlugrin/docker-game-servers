# Review 012 — Platform-side contract review, 2026-08-12

Source: report from the project that owns the image contract
(.claude/doc/image-contract.md), relayed by the user; inputs ~commit 917d8fb.

Headline: no contradictions with the contract; the on-platform delta is one
§11.2 sheet. Facts all check (including start_period semantics and cgroup
v2 `max`); B42-stable date past the reviewer's knowledge, noted as
unverified-not-doubted.

Requested edits, both accepted (user agreement 2026-08-12):

1. PZ item (l)'s must-not-ship was over-broad: the non-Steam profile always
   rides the fallback to internal RCON, so an unfavorable (l) would have
   blocked the whole image over a niche profile's probe. Narrowed: hard
   no-ship only for (c)+(l) both unfavorable (no safe stop-mediation
   channel); healthcheck-only case → the non-Steam profile is documented
   as degraded/unsupported under that resolution. Conditionally narrows
   the earlier "non-Steam supported" ruling, with the user's agreement.
   (Reviewer also expects (c) to resolve favorably: B41-era console took
   piped stdin; community images use a FIFO.)

2. PZ §4's idempotent-creation branch was circular ("where existence is
   not observable ... create when the account is absent") and invited a
   dangerous escape (blind creation gives INITIAL_ADMIN_PASSWORD override
   semantics if creation resets existing accounts). Fixed by naming the
   observation: the account lives in the per-SERVER_NAME SQLite database
   and querying it is the predicate (minimal SQLite client sanctioned in
   the image tooling); missing-database shortcut kept for the absent
   direction; blind-creation risk stated.

Optional polish, accepted: root §2.4 now states the SIGKILL exception
(always lands, forced from the parent namespace — why the grace period is
a last line of defense).

Compatibility findings A1–A5: platform-side sheet lines, no spec changes
(A1 = open item (o)'s split, guaranteed on that platform via its passwd
mount; A2 = contract §6.3 second case, sheet line; A3 accepted
degradation; A5 the pairing rule recorded on the sheet). The (o)
JVM-home-mitigation crumb was considered and deliberately not added
(mechanism territory; (o) already forces the verification).
