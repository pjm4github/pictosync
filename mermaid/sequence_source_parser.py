"""
mermaid/sequence_source_parser.py

Parse Mermaid sequence diagram source text (.mmd/.mermaid) into structured
participant, message, note, and block data.

This is **step 1** of a two-step pipeline:

    1. Source parse  → semantic data (participants, messages, notes, blocks)
    2. SVG geometry  → positions matched to source data from step 1

The parser handles ``sequenceDiagram`` sources with participants, actors,
messages (all arrow types), notes, and control-flow blocks (loop, alt, opt,
par, critical, break, rect).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ═══════════════════════════════════════════════════════════
# Data classes
# ═══════════════════════════════════════════════════════════

@dataclass
class SeqParticipant:
    """A parsed sequence diagram participant or actor.

    Attributes:
        alias: Internal identifier used in messages.
        label: Display name (may differ from alias).
        actor_type: ``"participant"`` or ``"actor"``.
        created: True if introduced with ``create``.
    """
    alias: str = ""
    label: str = ""
    actor_type: str = "participant"
    created: bool = False


@dataclass
class SeqMessage:
    """A parsed sequence diagram message (arrow).

    Attributes:
        from_alias: Source participant alias.
        to_alias: Target participant alias.
        text: Message label text.
        line_type: ``"solid"`` or ``"dotted"``.
        arrow_type: ``"arrow"`` (``->>``), ``"open"`` (``->``),
            ``"cross"`` (``-x``), ``"point"`` (``-)``).
        activate: True if ``+`` suffix on arrow.
        deactivate: True if ``-`` suffix on arrow.
    """
    from_alias: str = ""
    to_alias: str = ""
    text: str = ""
    line_type: str = "solid"
    arrow_type: str = "arrow"
    activate: bool = False
    deactivate: bool = False


@dataclass
class SeqNote:
    """A parsed sequence diagram note.

    Attributes:
        text: Note content.
        placement: ``"left_of"``, ``"right_of"``, or ``"over"``.
        actors: List of participant aliases the note is attached to.
    """
    text: str = ""
    placement: str = "over"
    actors: List[str] = field(default_factory=list)


@dataclass
class SeqBlock:
    """A parsed sequence diagram control-flow block.

    Attributes:
        block_type: ``"loop"``, ``"alt"``, ``"opt"``, ``"par"``,
            ``"critical"``, ``"break"``, ``"rect"``.
        label: Block label text.
        sections: List of ``(label, items)`` tuples for ``else``/``and``
            branches.  The first section has the block's own label.
    """
    block_type: str = ""
    label: str = ""
    sections: List[Tuple[str, list]] = field(default_factory=list)


@dataclass
class SeqParseResult:
    """Complete result from parsing a sequence diagram source file.

    Attributes:
        title: Diagram title (if any).
        participants: All declared/auto-registered participants.
        messages: All parsed messages.
        notes: All parsed notes.
        blocks: All parsed control-flow blocks.
        autonumber: Whether ``autonumber`` was specified.
    """
    title: str = ""
    participants: List[SeqParticipant] = field(default_factory=list)
    messages: List[SeqMessage] = field(default_factory=list)
    notes: List[SeqNote] = field(default_factory=list)
    blocks: List[SeqBlock] = field(default_factory=list)
    autonumber: bool = False


# ═══════════════════════════════════════════════════════════
# Arrow type mapping
# ═══════════════════════════════════════════════════════════

# Arrow regex: captures optional activation modifiers (+/-) after the arrow.
# Group layout: from, arrow_str, modifier, to, text
_ARROW_RE = re.compile(
    r"^"
    r"(\S+?)"             # from_alias (non-greedy, no spaces)
    r"\s*"
    r"(-?->>|-->>|->>|->|-->|--\)|--x|-\)|->|-x)"  # arrow
    r"([+-])?"            # optional activate/deactivate modifier
    r"\s*"
    r"(\S+?)"             # to_alias
    r"\s*"
    r"(?::\s*(.*))?"      # optional : text
    r"$"
)

# Map arrow string to (line_type, arrow_type)
_ARROW_MAP = {
    "->>":  ("solid", "arrow"),
    "-->>": ("dotted", "arrow"),
    "->":   ("solid", "open"),
    "-->":  ("dotted", "open"),
    "-x":   ("solid", "cross"),
    "--x":  ("dotted", "cross"),
    "-)":   ("solid", "point"),
    "--)":  ("dotted", "point"),
}

# Note placement regex
_NOTE_RE = re.compile(
    r"^Note\s+(left\s+of|right\s+of|over)\s+(.+?)(?:\s*:\s*(.*))?$",
    re.IGNORECASE,
)

# Participant/actor declaration regex
_PARTICIPANT_RE = re.compile(
    r"^(participant|actor|create\s+participant|create\s+actor)\s+"
    r"(\S+)"
    r"(?:\s+as\s+(.+))?"
    r"$",
    re.IGNORECASE,
)

# Block start keywords
_BLOCK_KEYWORDS = {"loop", "alt", "opt", "par", "critical", "break", "rect"}

# Block continuation keywords (else/and)
_SECTION_KEYWORDS = {"else", "and"}


# ═══════════════════════════════════════════════════════════
# Main parser
# ═══════════════════════════════════════════════════════════

def parse_sequence_source(text: str) -> SeqParseResult:
    """Parse Mermaid sequence diagram source text into structured data.

    Args:
        text: Full content of a ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result with participants, messages, notes, and blocks.

    Raises:
        ValueError: If the text does not start with ``sequenceDiagram``.
    """
    result = SeqParseResult()

    # Strip leading whitespace and detect diagram type
    stripped = text.strip()
    if not stripped:
        raise ValueError("Not a sequence diagram: empty source")

    # Find first non-comment, non-empty line
    first_keyword = None
    for line in stripped.splitlines():
        line_s = line.strip()
        if not line_s or line_s.startswith("%%"):
            continue
        first_keyword = line_s
        break

    if first_keyword is None or not first_keyword.startswith("sequenceDiagram"):
        raise ValueError(
            "Not a sequence diagram. First line must start with "
            "'sequenceDiagram'."
        )

    # Remove comments (%% ...)
    text = re.sub(r"%%[^\n]*", "", text)

    # Track known aliases for auto-registration
    known_aliases: dict[str, SeqParticipant] = {}
    # Track block nesting
    block_stack: list[SeqBlock] = []

    def _ensure_participant(alias: str) -> None:
        """Auto-register a participant if not already known."""
        if alias not in known_aliases:
            p = SeqParticipant(alias=alias, label=alias)
            known_aliases[alias] = p
            result.participants.append(p)

    for line in text.splitlines():
        line_s = line.strip()

        # Skip empty lines and the diagram keyword
        if not line_s or line_s.startswith("sequenceDiagram"):
            continue

        # ── Title ──
        if line_s.lower().startswith("title"):
            m = re.match(r"title\s+(.+)$", line_s, re.IGNORECASE)
            if m:
                result.title = m.group(1).strip()
            continue

        # ── Autonumber ──
        if line_s.lower() == "autonumber":
            result.autonumber = True
            continue

        # ── Activate / Deactivate (standalone) ──
        if line_s.lower().startswith("activate ") or line_s.lower().startswith("deactivate "):
            continue  # recognised but not stored as messages

        # ── Participant / Actor declaration ──
        pm = _PARTICIPANT_RE.match(line_s)
        if pm:
            decl_type = pm.group(1).lower()
            alias = pm.group(2)
            label = pm.group(3).strip() if pm.group(3) else alias
            created = decl_type.startswith("create")
            actor_type = "actor" if "actor" in decl_type else "participant"
            p = SeqParticipant(
                alias=alias,
                label=label,
                actor_type=actor_type,
                created=created,
            )
            known_aliases[alias] = p
            result.participants.append(p)
            continue

        # ── Note ──
        nm = _NOTE_RE.match(line_s)
        if nm:
            placement_raw = nm.group(1).lower().replace(" ", "_")
            actors_str = nm.group(2).strip()
            note_text = nm.group(3).strip() if nm.group(3) else ""
            actors = [a.strip() for a in actors_str.split(",")]
            result.notes.append(SeqNote(
                text=note_text,
                placement=placement_raw,
                actors=actors,
            ))
            continue

        # ── Block end ──
        if line_s.lower() == "end":
            if block_stack:
                block_stack.pop()
            continue

        # ── Block section (else/and) ──
        lower_s = line_s.lower()
        section_match = None
        for kw in _SECTION_KEYWORDS:
            if lower_s.startswith(kw):
                rest = line_s[len(kw):].strip()
                section_match = (kw, rest)
                break

        if section_match and block_stack:
            kw, label = section_match
            block_stack[-1].sections.append((label, []))
            continue

        # ── Block start ──
        block_match = None
        for kw in _BLOCK_KEYWORDS:
            if lower_s.startswith(kw):
                rest = line_s[len(kw):].strip()
                block_match = (kw, rest)
                break

        if block_match:
            kw, label = block_match
            blk = SeqBlock(
                block_type=kw,
                label=label,
                sections=[(label, [])],
            )
            result.blocks.append(blk)
            block_stack.append(blk)
            continue

        # ── Message (arrow) ──
        am = _ARROW_RE.match(line_s)
        if am:
            from_alias = am.group(1)
            arrow_str = am.group(2)
            modifier = am.group(3)  # + or - or None
            to_alias = am.group(4)
            msg_text = am.group(5) or ""

            # Strip activation modifiers from aliases
            from_alias = from_alias.lstrip("+-")
            to_alias = to_alias.rstrip("+-")

            line_type, arrow_type = _ARROW_MAP.get(
                arrow_str, ("solid", "arrow")
            )

            msg = SeqMessage(
                from_alias=from_alias,
                to_alias=to_alias,
                text=msg_text.strip(),
                line_type=line_type,
                arrow_type=arrow_type,
                activate=modifier == "+",
                deactivate=modifier == "-",
            )
            result.messages.append(msg)

            # Auto-register participants
            _ensure_participant(from_alias)
            _ensure_participant(to_alias)
            continue

    return result


def parse_sequence_source_file(path: str) -> SeqParseResult:
    """Parse a sequence diagram source file.

    Args:
        path: Path to the ``.mmd`` or ``.mermaid`` file.

    Returns:
        Parsed result.

    Raises:
        ValueError: If the file does not contain a sequence diagram.
    """
    with open(path, "r", encoding="utf-8") as f:
        return parse_sequence_source(f.read())
