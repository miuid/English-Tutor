"""Parse give-feedback output into per-criterion rubric levels.

The give-feedback output contract requires a ``## Per-criterion levels``
section with lines of the shape::

    - <criterion name>: **<A–E level>** — <short note>

The parser is tolerant of minor variations (missing bullets or bold markers,
en/em dashes, lowercase letters) and ignores anything that is not a valid
criterion line — including the parenthesised ``Overall`` line and levels that
are not a single A–E letter with an optional ``+``/``-`` (fits ``String(5)``;
en/em dashes normalise to ``-``).
"""

import re
from dataclasses import dataclass

_LEVEL_RE = re.compile(r"^[A-E][+-]?$")

_CRITERION_LINE_RE = re.compile(
    r"^\s*(?:[-*•]\s*)?"  # optional bullet
    r"\**\s*(?P<name>[^:*#–—-]+?)\s*\**"  # criterion name (no colon, bold, or dash)
    r"\s*:\s*"  # name/level separator
    r"\**\s*(?P<level>[A-Ea-e](?:\s*[+–—-])?)\s*\**"  # A–E level, optionally bold
    r"(?:\s*[–—-]\s*(?P<note>.*))?"  # optional em/en-dash note
    r"\s*$"
)

_DASHES = str.maketrans({"–": "-", "—": "-"})

_SECTION_HEADING_RE = re.compile(r"^#{1,6}\s*.*per-criterion", re.IGNORECASE)
_ANY_HEADING_RE = re.compile(r"^#{1,6}\s")
_BULLET_LINE_RE = re.compile(r"^\s*[-*•]\s")


@dataclass(frozen=True)
class RubricLevel:
    criterion_name: str
    level: str
    note: str | None


def parse_rubric_levels(output: str) -> list[RubricLevel]:
    """Extract per-criterion levels from give-feedback output.

    When a ``per-criterion`` heading is present only bullet lines in that
    section are scanned (avoids false positives like ``Strength: A …``);
    otherwise all lines are scanned. Returns only entries with a valid A–E
    level (optionally ``+``/``-``); non-matching lines are ignored, so a
    missing section yields an empty list.
    """
    levels: list[RubricLevel] = []
    for line in _section_lines(output.splitlines()):
        match = _CRITERION_LINE_RE.match(line)
        if not match:
            continue
        name = match.group("name").strip().strip("*").strip()
        if not name or name.lower().startswith("overall"):
            continue
        level = match.group("level").translate(_DASHES).replace(" ", "").upper()
        if not _LEVEL_RE.match(level):
            continue
        note = (match.group("note") or "").strip() or None
        levels.append(RubricLevel(criterion_name=name, level=level, note=note))
    return levels


def _section_lines(lines: list[str]) -> list[str]:
    """Return the lines to scan for criterion entries.

    Without a per-criterion heading, all lines are scanned. With one, only
    bullet lines under it (up to the next heading) are scanned — the contract
    mandates `- ` bullets there, and restricting to bullets prevents false
    positives from trailing lines like ``Strength: A …``.
    """
    start = next(
        (i for i, line in enumerate(lines) if _SECTION_HEADING_RE.match(line)),
        None,
    )
    if start is None:
        return lines
    end = next(
        (i for i in range(start + 1, len(lines)) if _ANY_HEADING_RE.match(lines[i])),
        len(lines),
    )
    return [line for line in lines[start + 1 : end] if _BULLET_LINE_RE.match(line)]
