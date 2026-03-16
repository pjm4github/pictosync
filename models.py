"""
models.py

Data models and constants for the Diagram Annotator application.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Optional

from settings import get_settings


# ----------------------------
# Annotation contents model — overlay-2.0
# ----------------------------

@dataclass
class TextFrame:
    """Layout of the text block within the shape bounding box.

    Controls margins (inset area) and default alignment.
    Maps to ``annotationContents.frame`` in the JSON schema.
    """
    margin_left: float = 4.0
    margin_right: float = 4.0
    margin_top: float = 4.0
    margin_bottom: float = 4.0
    valign: str = "top"     # top | middle | bottom
    halign: str = "center"  # left | center | right | justified

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TextFrame":
        if not isinstance(d, dict):
            return cls()
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class CharFormat:
    """Character-level formatting.

    Used as document-level defaults (``annotationContents.default_format``)
    and as sparse per-run overrides (``textRun.format``).  Absent fields
    inherit from ``default_format``; absent fields in ``default_format``
    use the system sans-serif defaults.
    """
    font_family: str = ""
    font_size: int = 12
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    color: str = ""              # #RRGGBBAA hex; empty = inherit
    background_color: str = ""   # #RRGGBBAA hex; empty = none
    superscript: bool = False
    subscript: bool = False

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CharFormat":
        if not isinstance(d, dict):
            return cls()
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})

    def to_dict(self, sparse: bool = False) -> Dict[str, Any]:
        """Serialize to dict.

        Args:
            sparse: If True, omit fields equal to their defaults (useful for
                    per-run format overrides so only deltas are stored).
        """
        if not sparse:
            return {f.name: getattr(self, f.name) for f in fields(self)}
        _zero = CharFormat()
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if getattr(self, f.name) != getattr(_zero, f.name)
        }


@dataclass
class TextRun:
    """An inline run within a paragraph.

    ``type`` discriminates between a text span (``"text"``) and an anchored
    inline graphic (``"anchor"``).
    """
    type: str = "text"         # "text" | "anchor"
    id: str = ""               # session-stable, not persisted
    # ── text run ──────────────────────────────────────────────────────
    text: str = ""
    format: Optional[CharFormat] = field(default=None, repr=False)
    # ── anchor run ────────────────────────────────────────────────────
    anchor_id: str = ""
    sizing: str = "inline"     # "inline" | "fixed"
    width: float = 0.0
    height: float = 0.0
    baseline_offset: float = 0.0

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TextRun":
        if not isinstance(d, dict):
            return cls()
        run_type = d.get("type", "text")
        rid = d.get("id", "")
        if run_type == "text":
            fmt = CharFormat.from_dict(d["format"]) if "format" in d else None
            return cls(type="text", id=rid, text=d.get("text", ""), format=fmt)
        if run_type == "anchor":
            return cls(
                type="anchor", id=rid,
                anchor_id=d.get("anchor_id", ""),
                sizing=d.get("sizing", "inline"),
                width=d.get("width", 0.0),
                height=d.get("height", 0.0),
                baseline_offset=d.get("baseline_offset", 0.0),
            )
        return cls(type=run_type, id=rid)

    def to_dict(self) -> Dict[str, Any]:
        if self.type == "text":
            d: Dict[str, Any] = {"type": "text", "text": self.text}
            if self.id:
                d["id"] = self.id
            if self.format is not None:
                fmt_d = self.format.to_dict(sparse=True)
                if fmt_d:
                    d["format"] = fmt_d
            return d
        if self.type == "anchor":
            d = {"type": "anchor", "anchor_id": self.anchor_id}
            if self.id:
                d["id"] = self.id
            if self.sizing != "inline":
                d["sizing"] = self.sizing
            if self.width:
                d["width"] = self.width
            if self.height:
                d["height"] = self.height
            if self.baseline_offset:
                d["baseline_offset"] = self.baseline_offset
            return d
        return {"type": self.type}


@dataclass
class TextBlock:
    """A paragraph block — the block-level container in the document.

    Maps 1:1 to a QTextBlock.  ``runs`` contains the ordered inline spans.
    """
    runs: List[TextRun] = field(default_factory=list)
    id: str = ""
    halign: str = ""       # empty = inherit from frame.halign
    line_spacing: float = 1.0
    space_before: float = 0.0
    space_after: float = 0.0

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TextBlock":
        if not isinstance(d, dict):
            return cls()
        runs = [TextRun.from_dict(r) for r in d.get("runs", [])]
        return cls(
            id=d.get("id", ""),
            halign=d.get("halign", ""),
            line_spacing=d.get("line_spacing", 1.0),
            space_before=d.get("space_before", 0.0),
            space_after=d.get("space_after", 0.0),
            runs=runs,
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"runs": [r.to_dict() for r in self.runs]}
        if self.id:
            d["id"] = self.id
        if self.halign:
            d["halign"] = self.halign
        if self.line_spacing != 1.0:
            d["line_spacing"] = self.line_spacing
        if self.space_before:
            d["space_before"] = self.space_before
        if self.space_after:
            d["space_after"] = self.space_after
        return d

    def plain_text(self) -> str:
        """Return concatenated text content of all text runs."""
        return "".join(r.text for r in self.runs if r.type == "text")


# ── Deprecated flat keys (overlay-1.0) ────────────────────────────────────
# These are present in contents dicts written before overlay-2.0.
# Used by from_dict migration and by schemas/__init__.py expected-template
# pruning.
DEPRECATED_CONTENTS_FIELDS = frozenset({
    "text", "halign", "valign", "spacing", "color", "font_family", "font_size",
    "margin_left", "margin_right", "margin_top", "margin_bottom",
    "flow_type", "image_url", "image_anchor",
})

# Old meta keys that signal the legacy pre-contents format (label/tech/note)
_OLD_META_KEYS = {"label", "tech", "note", "label_align", "label_size",
                  "tech_align", "tech_size", "note_align", "note_size",
                  "text_valign", "text_spacing"}


def build_contents_text(
    label: str = "",
    tech: str = "",
    note: str = "",
    label_size: int = 12,
    tech_size: int = 10,
    note_size: int = 10,
) -> str:
    """Build HTML text from legacy label/tech/note fields.

    Produces ``<p>`` blocks with inline ``<b>``/``<i>`` matching the old
    three-line rendering convention: label bold, tech italic in brackets,
    note plain.

    Args:
        label: Primary label text.
        tech: Technology string (rendered italic in square brackets).
        note: Freeform description.
        label_size: Font size for label (currently informational).
        tech_size: Font size for tech line (currently informational).
        note_size: Font size for note line (currently informational).

    Returns:
        HTML string suitable for ``AnnotationContents.text``.
    """
    parts: list[str] = []
    if label:
        parts.append(f"<p><b>{label}</b></p>")
    if tech:
        parts.append(f"<p><i>[{tech}]</i></p>")
    if note:
        parts.append(f"<p>{note}</p>")
    return "\n".join(parts)


@dataclass
class AnnotationContents:
    """Contents payload for diagram annotations (overlay-2.0).

    Primary fields:
        frame: Layout/margin/alignment of the text block.
        default_format: Document-level character format defaults.
        blocks: Ordered paragraph blocks with inline runs.
        wrap: Whether text wraps within the frame.
        text_box_width/height: Override box dimensions (0 = shape-derived).

    Backward-compat flat fields (overlay-1.0, read-only after migration):
        text, halign, valign, spacing, color, font_family, font_size,
        margin_left/right/top/bottom, flow_type, image_url, image_anchor.

    These flat fields are kept so canvas items and dock.py can access them
    via ``getattr(meta, "halign", ...)`` without modification when loading
    older files.  They are also written as mirrors during overlay-2.0 round-
    trips so that legacy canvas rendering still works without an items rewrite.
    """
    # ── overlay-2.0 primary ───────────────────────────────────────────
    frame: Optional[TextFrame] = field(default=None, repr=False)
    default_format: Optional[CharFormat] = field(default=None, repr=False)
    blocks: Optional[List[TextBlock]] = field(default=None, repr=False)
    wrap: bool = True
    text_box_width: float = 0.0
    text_box_height: float = 0.0
    # ── overlay-1.0 flat fields (mirrors + fallbacks) ─────────────────
    text: str = ""
    halign: str = "left"
    valign: str = "top"
    spacing: float = 0.0
    color: str = "#FF00FFFF"
    font_family: str = ""
    font_size: int = 12
    margin_left: float = 0.0
    margin_right: float = 0.0
    margin_top: float = 0.0
    margin_bottom: float = 0.0
    flow_type: str = "none"
    image_url: str = ""
    image_anchor: int = 0
    # Arbitrary extra keys preserved through round-trips
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    # -- Block-based label/tech/note property aliases -------------------

    def _ensure_blocks(self) -> List[TextBlock]:
        """Ensure at least 3 blocks exist (label, tech, note) and return them.

        Also initialises ``frame`` and ``default_format`` from effective
        values when they are ``None``, so the overlay-2.0 structure is
        always complete after this call.
        """
        if self.blocks is None:
            self.blocks = []
        if self.frame is None:
            self.frame = self.effective_frame()
        if self.default_format is None:
            self.default_format = self.effective_default_format()
        while len(self.blocks) < 3:
            self.blocks.append(TextBlock(runs=[TextRun(type="text", text="")]))
        return self.blocks

    @property
    def label(self) -> str:
        """Block 0 plain text (bold run)."""
        if self.blocks and len(self.blocks) >= 1:
            return self.blocks[0].plain_text()
        return ""

    @label.setter
    def label(self, value: str) -> None:
        blks = self._ensure_blocks()
        blks[0].runs = [TextRun(type="text", text=value,
                                format=CharFormat(bold=True))]
        self.text = _blocks_to_legacy_text(self.blocks)

    @property
    def tech(self) -> str:
        """Block 1 plain text (italic run). Stored WITHOUT brackets."""
        if self.blocks and len(self.blocks) >= 2:
            return self.blocks[1].plain_text()
        return ""

    @tech.setter
    def tech(self, value: str) -> None:
        blks = self._ensure_blocks()
        blks[1].runs = [TextRun(type="text", text=value,
                                format=CharFormat(italic=True))]
        self.text = _blocks_to_legacy_text(self.blocks)

    @property
    def note(self) -> str:
        """Block 2 plain text (plain run)."""
        if self.blocks and len(self.blocks) >= 3:
            return self.blocks[2].plain_text()
        return ""

    @note.setter
    def note(self, value: str) -> None:
        blks = self._ensure_blocks()
        blks[2].runs = [TextRun(type="text", text=value)]
        self.text = _blocks_to_legacy_text(self.blocks)

    # -- Serialization -------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AnnotationContents":
        """Create from a dict, accepting overlay-2.0, overlay-1.0, and legacy formats.

        Format detection order:
        1. Legacy (label/tech/note keys) → migrate to HTML text.
        2. Overlay-2.0 (``blocks`` or ``frame`` key) → populate nested fields
           and mirror to flat fields for canvas rendering.
        3. Overlay-1.0 (flat text/halign/color fields) → populate flat fields.

        Args:
            d: Contents/meta dict (any format).

        Returns:
            An ``AnnotationContents`` instance.
        """
        if not isinstance(d, dict):
            return cls()

        # ── 1. Legacy meta format (label/tech/note) ─────────────────
        if bool(_OLD_META_KEYS & d.keys()):
            label_val = d.get("label", "")
            tech_val = d.get("tech", "")
            note_val = d.get("note", "")
            label_size = d.get("label_size", 12)
            tech_size = d.get("tech_size", 10)
            note_size = d.get("note_size", 10)
            html = build_contents_text(label_val, tech_val, note_val,
                                       label_size, tech_size, note_size)
            halign = d.get("label_align", "center")
            valign = d.get("text_valign", "top")
            spacing = d.get("text_spacing", 0.0)
            text_box_width = d.get("text_box_width", 0.0)
            text_box_height = d.get("text_box_height", 0.0)

            # Build overlay-2.0 blocks from legacy fields
            blocks: List[TextBlock] = [
                TextBlock(runs=[TextRun(type="text", text=label_val,
                                        format=CharFormat(bold=True, font_size=label_size))]),
                TextBlock(runs=[TextRun(type="text", text=tech_val,
                                        format=CharFormat(italic=True, font_size=tech_size))]),
                TextBlock(runs=[TextRun(type="text", text=note_val,
                                        format=CharFormat(font_size=note_size))]),
            ]
            frame = TextFrame(halign=halign, valign=valign)
            default_format = CharFormat(font_size=label_size)

            old_all = _OLD_META_KEYS | {"text_box_width", "text_box_height", "dsl"}
            extras: Dict[str, Any] = {k: v for k, v in d.items()
                                       if k not in old_all}
            if "dsl" in d:
                extras["dsl"] = d["dsl"]
            return cls(
                frame=frame, default_format=default_format, blocks=blocks,
                text=html, halign=halign, valign=valign, spacing=spacing,
                font_size=label_size,
                text_box_width=text_box_width, text_box_height=text_box_height,
                margin_left=frame.margin_left, margin_right=frame.margin_right,
                margin_top=frame.margin_top, margin_bottom=frame.margin_bottom,
                extras=extras,
            )

        # ── 2. Overlay-2.0 (has blocks or frame) ────────────────────
        if "blocks" in d or "frame" in d:
            frame = TextFrame.from_dict(d.get("frame") or {})
            default_format = CharFormat.from_dict(d.get("default_format") or {})
            blocks = [TextBlock.from_dict(b) for b in d.get("blocks") or []]
            wrap = d.get("wrap", True)
            text_box_width = d.get("text_box_width", 0.0)
            text_box_height = d.get("text_box_height", 0.0)

            # Mirror nested → flat for canvas item backward compat
            halign = frame.halign
            valign = frame.valign
            color = default_format.color or "#FF00FFFF"
            font_family = default_format.font_family
            font_size = default_format.font_size or 12

            # Build legacy text fallback from blocks (for items that haven't
            # been updated to render from blocks yet)
            text = _blocks_to_legacy_text(blocks)

            extras = {k: v for k, v in d.items()
                      if k not in {"frame", "default_format", "blocks", "wrap",
                                   "text_box_width", "text_box_height"}}
            return cls(
                frame=frame, default_format=default_format, blocks=blocks,
                wrap=wrap, text_box_width=text_box_width,
                text_box_height=text_box_height,
                text=text, halign=halign, valign=valign,
                color=color, font_family=font_family, font_size=font_size,
                margin_left=frame.margin_left, margin_right=frame.margin_right,
                margin_top=frame.margin_top, margin_bottom=frame.margin_bottom,
                extras=extras,
            )

        # ── 3. Overlay-1.0 flat format ───────────────────────────────
        known_names = {
            f.name for f in fields(cls)
            if f.name not in ("extras", "frame", "default_format", "blocks")
        }
        known: Dict[str, Any] = {}
        extras = {}
        for k, v in d.items():
            if k in known_names:
                known[k] = v
            else:
                extras[k] = v
        return cls(**known, extras=extras)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Writes overlay-2.0 format (frame + default_format + blocks) when
        ``blocks`` is not None.  Falls back to overlay-1.0 flat format for
        items that have not been migrated yet.
        """
        if self.blocks is not None:
            d: Dict[str, Any] = {}
            if self.frame is not None:
                d["frame"] = self.frame.to_dict()
            if self.default_format is not None:
                fmt_d = self.default_format.to_dict(sparse=True)
                if fmt_d:
                    d["default_format"] = fmt_d
            d["blocks"] = [b.to_dict() for b in self.blocks]
            d["wrap"] = self.wrap
            if self.text_box_width:
                d["text_box_width"] = self.text_box_width
            if self.text_box_height:
                d["text_box_height"] = self.text_box_height
            # Convenience keys for external tooling and property panel
            d["label"] = self.label
            d["tech"] = self.tech
            d["note"] = self.note
            d.update(self.extras)
            return d

        # Overlay-1.0 flat format
        _FLAT = {
            "text", "halign", "valign", "spacing", "color", "font_family",
            "font_size", "margin_left", "margin_right", "margin_top",
            "margin_bottom", "wrap", "flow_type", "text_box_width",
            "text_box_height", "image_url", "image_anchor",
        }
        out = {f.name: getattr(self, f.name)
               for f in fields(self) if f.name in _FLAT}
        out.update(self.extras)
        return out

    # -- Defaults ------------------------------------------------------

    @classmethod
    def get_formatting_defaults(cls) -> Dict[str, Any]:
        """Get default values for all annotationContents fields.

        Returns a nested dict matching the overlay-2.0 structure.
        Values are loaded from settings (DefaultContentsSettings).
        """
        d = get_settings().settings.defaults
        return {
            "frame": {
                "halign":        d.halign,
                "valign":        d.valign,
                "margin_left":   d.margin_left,
                "margin_right":  d.margin_right,
                "margin_top":    d.margin_top,
                "margin_bottom": d.margin_bottom,
            },
            "default_format": {
                "font_family":   d.font_family,
                "font_size":     d.font_size,
                "color":         d.color,
            },
            "wrap":            d.wrap,
            "text_box_width":  d.text_box_width,
            "text_box_height": d.text_box_height,
        }

    def effective_frame(self) -> TextFrame:
        """Return the effective TextFrame, using defaults if not set."""
        return self.frame if self.frame is not None else TextFrame(
            margin_left=self.margin_left,
            margin_right=self.margin_right,
            margin_top=self.margin_top,
            margin_bottom=self.margin_bottom,
            valign=self.valign,
            halign=self.halign,
        )

    def effective_default_format(self) -> CharFormat:
        """Return the effective CharFormat, using flat field mirrors if not set."""
        return self.default_format if self.default_format is not None else CharFormat(
            font_family=self.font_family,
            font_size=self.font_size,
            color=self.color,
        )


def hex_to_css_color(hex_color: str) -> str:
    """Convert a stored ``#RRGGBBAA`` color to a CSS-compatible string.

    Qt's HTML renderer (used by ``QTextDocument``) does not support the CSS
    Level-4 8-digit hex syntax.  This function converts:

    * ``#RRGGBBAA`` with alpha=FF → ``#RRGGBB``
    * ``#RRGGBBAA`` with partial alpha → ``rgba(r,g,b,a)``
    * ``#RRGGBB`` (6 digits) → returned as-is
    * anything else → returned as-is

    Args:
        hex_color: Stored color string (``#RRGGBBAA`` or ``#RRGGBB``).

    Returns:
        CSS color string safe to embed in HTML ``style`` attributes.
    """
    h = hex_color.lstrip("#")
    if len(h) == 8:
        try:
            r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
            if a == 255:
                return f"#{h[:6]}"
            return f"rgba({r},{g},{b},{a / 255:.3f})"
        except ValueError:
            pass
    return hex_color


def _blocks_to_legacy_text(blocks: List[TextBlock]) -> str:
    """Produce a simple HTML body string from blocks for legacy canvas rendering.

    Only handles basic bold/italic/underline/color/font run formats.
    Used internally when populating the backward-compat ``text`` field.

    Args:
        blocks: List of ``TextBlock`` objects.

    Returns:
        HTML body fragment string (no ``<html>/<head>/<body>`` wrapper).
    """
    import html as _html
    parts: list[str] = []
    for blk in blocks:
        runs_html = ""
        for run in blk.runs:
            if run.type != "text":
                continue
            span = _html.escape(run.text)
            fmt = run.format
            if fmt:
                if fmt.bold:
                    span = f"<b>{span}</b>"
                if fmt.italic:
                    span = f"<i>{span}</i>"
                if fmt.underline:
                    span = f"<u>{span}</u>"
                if fmt.strikethrough:
                    span = f"<s>{span}</s>"
                if fmt.superscript:
                    span = f"<sup>{span}</sup>"
                if fmt.subscript:
                    span = f"<sub>{span}</sub>"
                styles = []
                if fmt.color:
                    styles.append(f"color:{hex_to_css_color(fmt.color)}")
                if fmt.background_color:
                    styles.append(f"background-color:{hex_to_css_color(fmt.background_color)}")
                if fmt.font_size and fmt.font_size != 12:
                    styles.append(f"font-size:{fmt.font_size}pt")
                if fmt.font_family:
                    styles.append(f"font-family:{fmt.font_family}")
                if styles:
                    span = f"<span style='{';'.join(styles)}'>{span}</span>"
            runs_html += span
        align_css = {
            "left": "left", "center": "center",
            "right": "right", "justified": "justify",
        }.get(blk.halign, "")
        style = f" style='text-align:{align_css};'" if align_css else ""
        parts.append(f"<p{style}>{runs_html}</p>")
    return "\n".join(parts)


def normalize_contents(contents_dict: Dict[str, Any], kind: str) -> Dict[str, Any]:
    """Normalize a contents dict by adding default values for missing fields.

    For overlay-2.0 dicts (with ``blocks``), defaults are applied to the
    nested ``frame`` and ``default_format`` sub-objects.  For overlay-1.0
    flat dicts, the flat formatting defaults are applied.

    Args:
        contents_dict: The contents dict to normalize (may be partial).
        kind: The item kind (rect, roundedrect, ellipse, line, text, …).

    Returns:
        A contents dict with formatting defaults applied.
    """
    result: Dict[str, Any] = {}
    if contents_dict:
        result.update(contents_dict)

    if "blocks" in result or "frame" in result:
        # Overlay-2.0: apply nested defaults
        fmtd = AnnotationContents.get_formatting_defaults()
        if "frame" not in result:
            result["frame"] = {}
        for k, v in fmtd["frame"].items():
            result["frame"].setdefault(k, v)
        if "default_format" not in result:
            result["default_format"] = {}
        for k, v in fmtd["default_format"].items():
            result["default_format"].setdefault(k, v)
        result.setdefault("wrap", fmtd["wrap"])
    else:
        # Overlay-1.0: apply flat defaults
        d = get_settings().settings.defaults
        flat_defaults = {
            "halign":        d.halign,
            "valign":        d.valign,
            "spacing":       d.spacing,
            "color":         d.color,
            "font_family":   d.font_family,
            "font_size":     d.font_size,
            "margin_left":   d.margin_left,
            "margin_right":  d.margin_right,
            "margin_top":    d.margin_top,
            "margin_bottom": d.margin_bottom,
            "wrap":          d.wrap,
            "flow_type":     d.flow_type,
            "text_box_width":  d.text_box_width,
            "text_box_height": d.text_box_height,
            "image_url":     d.image_url,
            "image_anchor":  d.image_anchor,
        }
        for key, default_value in flat_defaults.items():
            if key not in result:
                result[key] = default_value

    return result


# Backwards-compatibility aliases
AnnotationMeta = AnnotationContents
normalize_meta = normalize_contents


# ----------------------------
# External type → PictoSync kind alias mapping
# ----------------------------

KIND_ALIAS_MAP: Dict[str, str] = {
    # ── C4 Model types ──
    "person":                   "roundedrect",
    "external_person":          "roundedrect",
    "system":                   "roundedrect",
    "external_system":          "roundedrect",
    "system_db":                "cylinder",
    "external_system_db":       "cylinder",
    "system_queue":             "roundedrect",
    "external_system_queue":    "roundedrect",
    "container":                "roundedrect",
    "external_container":       "roundedrect",
    "container_db":             "cylinder",
    "external_container_db":    "cylinder",
    "container_queue":          "roundedrect",
    "external_container_queue": "roundedrect",
    "component":                "roundedrect",
    "external_component":       "roundedrect",
    "component_db":             "cylinder",
    "external_component_db":    "cylinder",
    "component_queue":          "roundedrect",
    "external_component_queue": "roundedrect",
    # ── PlantUML types ──
    "rectangle":  "rect",
    "database":   "cylinder",
    "actor":      "ellipse",
    "interface":  "ellipse",
    "cloud":      "ellipse",
    "node":       "rect",
    "folder":     "rect",
    "queue":      "rect",
    "participant": "rect",
    "class":      "rect",
    "entity":     "rect",
    "note":       "roundedrect",
    "title":      "text",
}


def resolve_kind_alias(external_type: str, fallback: Optional[str] = None) -> Optional[str]:
    """Resolve an external type name to a PictoSync annotation kind.

    Args:
        external_type: The external type name (e.g. ``'container_db'``,
            ``'database'``, ``'person'``).
        fallback: Kind to return if no alias match.  Defaults to ``None``.

    Returns:
        The PictoSync kind string, or *fallback* if no mapping exists.
    """
    return KIND_ALIAS_MAP.get(external_type, fallback)


# ----------------------------
# Drawing mode constants
# ----------------------------

class Mode:
    """Drawing mode constants for the annotator."""
    SELECT = "select"
    RECT = "rect"
    ROUNDEDRECT = "roundedrect"
    ELLIPSE = "ellipse"
    LINE = "line"
    TEXT = "text"
    HEXAGON = "hexagon"
    CYLINDER = "cylinder"
    BLOCKARROW = "blockarrow"
    POLYGON = "polygon"
    CURVE = "curve"
    ORTHOCURVE = "orthocurve"
    ISOCUBE = "isocube"
    SEQBLOCK = "seqblock"
    PORT = "port"


# ----------------------------
# Graphics item constants
# ----------------------------

ANN_ID_KEY = 1  # QGraphicsItem.data key for annotation id

# Resizable shape handle constants
HANDLE_SIZE = 8.0
HIT_DIST = 10.0
MIN_SIZE = 5.0
