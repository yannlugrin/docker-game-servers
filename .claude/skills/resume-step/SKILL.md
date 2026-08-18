---
name: resume-step
description: >-
  Post-interruption verification — run after work ended abnormally (a usage
  limit, a crash, a reboot, a killed console) or whenever the operator doubts
  what the last session claims to have done. Distrusts the transcript,
  verifies the claimed state against the repository and the world, then
  reports discrepancies and repair options. Verifies and reports only; it
  never repairs.
---

# Resume — verify what is actually true

Work was interrupted or the last session's claims are in doubt. Your job is
to establish what is actually true, then stop.

**When to use.** Instead of `/orient` — it embeds the same orientation —
after an abnormal end, or whenever the operator doubts the last session's
account. Prefer invoking it from a fresh session, which cannot be tempted to
trust the old transcript.

**Verify only.** This ritual reads, runs read-only checks and reports. It
repairs nothing: the repair is the operator's ruling.

**Which documents.** "The plan" and "the decision log" below mean the
**active track's**, resolved when this runs — from `CLAUDE.md`'s track map
and its `Current state` pointer. On a component track the root
specification applies too.

**Doctrine: the transcript is a claim, not evidence.** What the conversation
— or its summary, or your own memory of it — says was completed is exactly
what an interruption falsifies: the narrative was written before the
interrupt, the state after. Evidence is the repository and the world; every
claim is checked against them.

In order:

1. **Anchor on approved truth.** The last annotated step tag is the last
   operator-approved state:
   `git describe --tags --abbrev=0 --match 'step-*'`
   (before the first tag, the anchor is the repository root). `git log` and
   `git diff` from there to `HEAD`, plus `git status`, are the complete
   evidence of everything since — committed and uncommitted.
2. **Read what `/orient` reads, then cross-check it.** This ritual replaces
   `/orient`, so it performs the same session-start reading, not a narrower
   one: `CLAUDE.md` in full, the **root** `PLAN.md` and `DECISIONS.md`, then
   the active track's plan, log and specification, plus the specification
   sections the current step names — the root specification included, on
   every track. `CLAUDE.md` routes a resumed session here *before touching
   anything*, so a ritual that read less would be how a session ends up
   working from no specification at all.

   Then check each claim in those files against the git evidence. They were
   written by the same interrupted session, so a mismatch is a finding, never
   something to reconcile silently — a status of `awaiting test` over a
   half-delivered diff is precisely what you are looking for.

3. **Working-tree forensics.** Examine uncommitted changes for half-written
   work (a file edited where its counterpart was not, a reference to
   something that does not exist yet). Run `just check`: green is cheap
   evidence the tree is at least well-formed; red localizes the interruption.
   If it reports that the harness is not installed, `just setup` was
   interrupted too — say so rather than running it.

   **The test half is a judgement, not a default.** Today `just test` is the
   guard's selftest and costs a fraction of a second, so run it too. Once it
   builds or starts this project's images it becomes a local write and a
   multi-minute cost, inside the one ritual most likely to be running on a
   broken tree — from then on run it only when you know what it costs, and
   say what you skipped.
4. **World state, inside the boundary.** The step may have touched things no
   file records — consult the current step's "how I test it" and cleanup
   notes in the plan for what it may have half-applied. All of the following
   are read-only and free under rule 9:

   - `ls -l .venv/bin/pre-commit` — is the pinned toolchain installed at all;
   - `docker ps -a`, `docker images`, `docker volume ls` — this project's own
     containers, images and volumes, matched **by name**. Until the `sc` and
     `pz` tracks build one, nothing here belongs to this project, and
     everything listed is another project's work on a shared daemon
     (`.claude/docs/environment.md` §3 "Docker on this host");
   - `ls -la .local/` — the gitignored scratch root holding local test state
     directories and downloaded game content;
   - `git status -sb` and `git ls-remote --tags origin` — whether an
     interrupted close left its commit or its annotated tag unpushed;
   - `gh run list` and `gh api user/packages?package_type=container` —
     GitHub API reads, which rule 9 rules free: CI runs and published
     packages.

   Anything **gated** by the rule-9 boundary — a push, any `gh` write, a
   registry publish or deletion, an unscoped `docker … prune` — you request
   from the operator and never run, not even to establish state. Anything
   unverifiable from here you report as unverified: an honest gap beats a
   guessed answer.
5. **Report, then stop — two shapes:**
   - **Discrepancies found:** the resume point and its evidence; each
     discrepancy as the claim plus the contradicting evidence; what could
     not be verified; and the repair options — continue the step from the
     verified state, roll back to the last `step-*` tag, or redo the partial
     work — with your recommendation. The repair is the operator's ruling;
     you execute nothing until they choose.
   - **Everything consistent:** deliver `/orient`'s report — current step and
     status, what the in-progress diff contains, what remains — plus one
     line: verification found no discrepancies, and what was checked. Then
     wait for the operator's go.

---

*Editing this file: frontmatter is `name` and `description` only — why is
in `.claude/docs/agents.md` §4 "A skill's frontmatter".*
