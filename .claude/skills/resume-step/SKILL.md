---
name: resume-step
description: Post-interruption verification — run after work ended
  abnormally (a usage limit, a crash, a reboot, a killed console) or
  whenever the operator doubts what the last session claims to have done.
  Distrusts the transcript, verifies the claimed state against the
  repository and the world, then reports discrepancies and repair
  options. Verifies and reports only; it never repairs.
---

# resume-step

Work was interrupted or the last session's claims are in doubt. Your
job is to establish what is actually true, then stop.

**When to use.** Instead of `/orient` — it embeds the same orientation —
after an abnormal end, or whenever the operator doubts the last
session's account. Prefer invoking it from a fresh session, which cannot
be tempted to trust the old transcript.

**Doctrine: the transcript is a claim, not evidence.** What the
conversation — or its summary, or your own memory of it — says was
completed is exactly what an interruption falsifies: the narrative
was written before the interrupt, the state after. Evidence is the
repository and the world; every claim is checked against them.

**Resolve the active track first**, as `/orient` does: `CLAUDE.md`'s
Track map and Current state pointer name the track, and with it the
plan, the decision log, the step-identifier prefix and the
specification set. An interrupted session may have left that pointer
mid-move, so treat it as a claim like any other.

In order:

1. **Anchor on approved truth.** The last annotated step tag is the
   last operator-approved state:
   `git describe --tags --abbrev=0 --match 'step-*'`
   (before the first tag, the anchor is the repository root).
   `git log` and `git diff` from there to `HEAD`, plus `git status`,
   are the complete evidence of everything since — committed and
   uncommitted.
2. **Cross-check the memory files.** Read `CLAUDE.md`'s pointers, root
   `PLAN.md` and `DECISIONS.md`, the active track's plan entry for the
   current step and its status, and the tail of that track's decision
   log; check each claim against the git evidence. They were written by
   the same interrupted session, so a mismatch is a finding, never
   something to reconcile silently — a status of `awaiting test` over a
   half-delivered diff is precisely what you are looking for.
3. **Working-tree forensics.** Examine uncommitted changes for
   half-written work (a file edited where its counterpart was not, a
   reference to something that does not exist yet). Capture what you
   find as quotable output *before* running anything over the tree.
   Then, as the **last** forensic act, run `just check`: green is cheap
   evidence the tree is at least well-formed; red localizes the
   interruption. It goes last because a failing check repairs in place
   (`DECISIONS.md` D-006), and here the tree it would rewrite is
   uncommitted evidence with no committed copy behind it — a truncated
   file missing its final newline is exactly what an interruption
   leaves and exactly what `end-of-file-fixer` silently erases.
4. **World state, inside the boundary.** The step may have touched
   things no file records — consult the current step's "how the
   operator tests it" entry and its cleanup notes in the plan for what
   it may have half-applied, then check for it with rule 9's free
   read-only side: this project's Docker images, containers and
   volumes, their logs and inspection, and anonymous remote reads.
   Start with `ls -la .local/`, which a reader would not derive: local
   test state and bind-mount roots collect there (`DECISIONS.md`
   D-004), so a smoke test cut in half leaves its evidence in one
   place. Anything gated you request from the operator, never run;
   anything unverifiable from here you report as unverified — an
   honest gap beats a guessed answer.
5. **Report, then stop — two shapes:**
   - **Discrepancies found:** the resume point and its evidence;
     each discrepancy as the claim plus the contradicting evidence;
     what could not be verified; and the repair options — continue
     the step from the verified state, roll back to the last
     `step-*` tag, or redo the partial work — with your
     recommendation. The repair is the operator's ruling; you
     execute nothing until they choose.
   - **Everything consistent:** deliver `/orient`'s report — current
     step and status, what the in-progress diff contains, what
     remains — plus one line: verification found no discrepancies,
     and what was checked. Then wait for the operator's go.
