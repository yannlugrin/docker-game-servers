#!/usr/bin/env python3
"""Every `<document>` §N pointer resolves, and names the section it points at.

One shape is recognised: a backticked path ending in `.md`, then §N, then an
optional quoted title. The path resolves from the citing file's own directory
or from the repository root, the section must exist, and a quoted title must
be a prefix of that section's heading. Inside `.claude/agents/` and
`.claude/skills/` the title is **required** — that is the class where a
pointer is followed by a session that will not re-read the target to check.

Two deliberate exclusions. Prose naming a section any other way — "section 2",
"root §3" — is not recognised, because every `SPECIFICATIONS.md` is read-only
under rule 1 and a check that could go red on a specification's own
cross-references is a check nobody is allowed to turn green. And documents are
scanned whole rather than line by line, because they wrap at ~76 columns and a
line-based scan would silently stop checking the long titles most worth citing.

Why a title and not just the number, why required in only one class, and the
measurement that settled both: `DECISIONS.md` D-013.
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

NEWLINE = "\n"


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
    for candidate in (citing.parent / cited, root / cited):
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
            where = f"{name}:{text.count(NEWLINE, 0, match.start()) + 1}"
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
