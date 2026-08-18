#!/usr/bin/env python3
"""Every `<document>` §N pointer resolves, and names the section it points at.

The failure this exists for was committed at `step-004`, in the very commit
that created the target section: four rituals pointed at
`.claude/docs/agents.md` §5, written from the numbering as it stood before a
new section was inserted ahead of it in the same commit. Nothing was
malformed, nothing was missing, and the reader following the pointer landed on
the re-measure recipe with no way to know they had been sent to the wrong
place.

**A number-only check would not have caught it, and this was measured rather
than reasoned:** an earlier draft of this file checked that §N existed, and
passed the defect, because §5 did exist. That is the whole argument for the
title. A section number is a reference with no redundancy — any number that
happens to exist looks right — while a number *and* a title cannot both be
wrong in the same direction by accident.

So inside `.claude/agents/` and `.claude/skills/`, the class this repository's
governance tooling lives in, a pointer **must** carry a quoted title, and it
must be a prefix of that section's heading (a prefix, so a long heading can be
cited by its distinctive opening rather than transcribed). Everywhere else a
title is optional and checked when present: the plans, the logs and
`CLAUDE.md` carry two dozen such pointers, and requiring titles there is prose
churn in files this check exists to protect, not to rewrite.

Deliberately narrow, for the same reason the frontmatter check is: exactly one
shape is recognised, a backticked path ending in `.md` followed by §N and an
optional quoted title. That shape is unambiguous, so this check makes no
judgement calls and cannot become a false-positive machine. Prose that names a
section any other way — "section 2", "root §3" — is out of scope on purpose:
`SPECIFICATIONS.md` is read-only under rule 1, so a check that could go red on
a specification's own cross-references would be a check nobody can turn green.

The path resolves from the citing file's own directory, then from the
repository root, then — for a bare filename with no slash, which is how these
documents cite each other from inside `.claude/docs/` — from `.claude/docs/`.
A path that resolves nowhere is reported too: a pointer into a file that does
not exist is the same defect one step further along.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# A backticked path ending in .md, then §N, then optionally a quoted title.
# Matched over the whole document rather than line by line, and the title may
# therefore wrap: these files are hand-wrapped at ~76 columns, and a check
# that only saw single-line titles would quietly stop checking the long ones —
# which are exactly the titles worth citing. Whitespace inside a reference is
# normalised before comparison, so a wrap is invisible to the result.
REFERENCE = re.compile(r"`([^`\n]+\.md)`\s*§(\d+)(?:\s*\"([^\"]+?)\")?")
SECTION = re.compile(r"^## (\d+)\.\s*(.*)$")

# The two standing path exclusions, matching `.pre-commit-config.yaml`:
# material this repository does not own and does not lint.
EXCLUDED = (".claude/spec-work/", ".claude/refs/")

# Where a title is not optional. These are the files whose whole purpose is to
# be followed by a session that will not re-read the target to check.
TITLE_REQUIRED = (".claude/agents/", ".claude/skills/")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def documents(root: Path) -> list[str]:
    """Every markdown file `just check` would look at, tracked or not.

    Enumerated through git for the same reason the harness does it: git owns
    the ignore rules, and duplicating them here is how the two drift apart.
    """
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others",
         "--exclude-standard", "--", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    names = [name for name in listing.stdout.split("\0") if name]
    return sorted(name for name in names if not name.startswith(EXCLUDED))


def sections_of(path: Path) -> dict[int, str]:
    """Every `## N. Heading` in a document, as {N: heading text}."""
    matched = (SECTION.match(line) for line in path.read_text().splitlines())
    return {int(m.group(1)): flattened(m.group(2)) for m in matched if m}


def flattened(text: str) -> str:
    """One line, single-spaced — how a wrapped title compares to a heading."""
    return " ".join(text.split())


def resolve(cited: str, citing: Path, root: Path) -> Path | None:
    candidates = [citing.parent / cited, root / cited]
    if "/" not in cited:
        candidates.append(root / ".claude" / "docs" / cited)
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def main() -> int:
    root = project_root()
    problems: list[str] = []
    sections: dict[Path, dict[int, str]] = {}
    checked = 0

    for name in documents(root):
        citing = root / name
        text = citing.read_text()
        for match in REFERENCE.finditer(text):
            cited, section, title = match.group(1), match.group(2), match.group(3)
            title = flattened(title) if title else ""
            checked += 1
            where = f"{name}:{text.count(chr(10), 0, match.start()) + 1}"
            target = resolve(cited, citing, root)
            if target is None:
                problems.append(f"{where}: `{cited}` resolves to no file")
                continue
            if target not in sections:
                sections[target] = sections_of(target)
            found = sections[target]
            if int(section) not in found:
                listed = ", ".join(f"§{n}" for n in sorted(found))
                problems.append(
                    f"{where}: `{cited}` has no §{section} —"
                    f" it has {listed or 'no numbered sections'}"
                )
                continue
            heading = found[int(section)]
            if not title:
                if name.startswith(TITLE_REQUIRED):
                    problems.append(
                        f'{where}: §{section} is cited without a title —'
                        f' write §{section} "{heading}"'
                    )
            elif not heading.startswith(title):
                problems.append(
                    f'{where}: §{section} is titled "{heading}", not "{title}"'
                )

    for problem in problems:
        print(f"DANGLING  {problem}")
    print(f"{checked - len(problems)}/{checked} section references resolve")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
