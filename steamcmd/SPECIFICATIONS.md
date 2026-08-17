# steamcmd Builder Image — Specification

Per-image specification under §6 of the repository-root `SPECIFICATIONS.md`.

**This document carries no requirements of its own.** The steamcmd builder is
specified in full by the root document, and a requirement stated twice is a
requirement that drifts (root §6, `DECISIONS.md` D-004). It exists as a
pointer, so that every shipped image directory holds a specification document
and a missing file never has to be interpreted.

References written `§N` would point to this document; references written
`root §N` point to the root document. Since this document defines no sections,
every reference here is of the second form.

## Where the builder is specified

| Subject | Section |
|---|---|
| Purpose, and that it is **not** a runtime image | root §4.1 |
| Base image and the pre-warmed steamcmd layer | root §4.2, root §3.1 |
| Installing an app id from a branch, validation, and the build-time credential channel that must leave nothing in any layer or in the build history | root §4.3, root §10.4 |
| Nothing beyond steamcmd's needs | root §4.4 |
| Why steamcmd is 32-bit glibc, and why images are linux/amd64 only | root §2.1 |
| Why the builder cannot be pinned to a steamcmd version | root §2.2 |
| The build direction, and the pinned builder reference every game image uses | root §3.1 |
| Date-stamped tags, the ordinal suffix, and the moving `latest` | root §7 |
| The publish gate — steamcmd must run to completion on an anonymous metadata query before a date tag is pushed | root §8 |
| OCI annotations | root §5.8 |
| The per-image README, which is also the GHCR page | root §9 |
| That a general-purpose runtime steamcmd image is a non-goal | root §11 |

The conventions of root §5 bind **game** images; they do not bind this one,
which ships no game and runs no server. Where a root §5 convention is
nevertheless meaningful for the builder — its annotations (§5.8), its
documentation (§9) — the table above names the section that applies.

## If this document ever gains requirements

It would stop being a pointer, and root §6's pointer form would no longer
describe it. That is a specification change: raise it, and follow rule 1's
amendment channel rather than adding requirements here.
