"""
pptx_export.py

Export canvas annotations to PowerPoint slides.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.oxml.ns import nsmap


# PowerPoint uses EMUs (English Metric Units)
# 914400 EMUs = 1 inch, typical screen is 96 DPI
# So 1 pixel at 96 DPI = 914400 / 96 = 9525 EMUs
EMUS_PER_PIXEL = 9525

# Default slide size (standard 16:9 widescreen)
DEFAULT_SLIDE_WIDTH = Emu(12192000)  # 10 inches
DEFAULT_SLIDE_HEIGHT = Emu(6858000)  # 7.5 inches


def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Color in format "#RRGGBB" or "#RRGGBBAA"

    Returns:
        Tuple of (r, g, b) or None if invalid
    """
    if not hex_color or not hex_color.startswith("#"):
        return None

    hex_color = hex_color.lstrip("#")

    # Handle alpha channel (#RRGGBBAA format) — strip trailing alpha
    if len(hex_color) == 8:
        hex_color = hex_color[:6]

    if len(hex_color) != 6:
        return None

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


def has_alpha_transparency(hex_color: str) -> bool:
    """
    Check if a hex color has alpha transparency (not fully opaque).

    Args:
        hex_color: Color in format "#RRGGBB" or "#RRGGBBAA"

    Returns:
        True if the color has transparency (alpha < FF)
    """
    if not hex_color or not hex_color.startswith("#"):
        return False

    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 8:
        alpha = hex_color[6:8].upper()
        return alpha != "FF"

    return False


def px_to_emu(pixels: float) -> int:
    """Convert pixels to EMUs."""
    return int(pixels * EMUS_PER_PIXEL)


def _apply_line_style(line, style: Dict[str, Any], arrow_mode: str = "none"):
    """
    Apply stroke/line styling to a shape's line.

    Args:
        line: The shape.line object from python-pptx
        style: Style dict containing pen properties
        arrow_mode: Arrow mode for lines (none, start, end, both)
    """
    pen = style.get("pen", {})

    # Set line color
    pen_color = pen.get("color", "#FF0000")
    rgb = hex_to_rgb(pen_color)
    if rgb:
        line.color.rgb = RGBColor(*rgb)

    # Set line width
    pen_width = pen.get("width", 2)
    line.width = Pt(pen_width)

    # Set dash style
    dash = pen.get("dash", "solid")
    if dash == "dashed":
        # Use round dot dash style for dashed lines
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        line.dash_style = MSO_LINE_DASH_STYLE.DASH


def _apply_fill_style(fill, style: Dict[str, Any]):
    """
    Apply fill styling to a shape.

    Args:
        fill: The shape.fill object from python-pptx
        style: Style dict containing fill properties
    """
    fill_style = style.get("fill") or style.get("brush") or {}
    fill_color = fill_style.get("color", "#00000000")

    # Check if fill is transparent
    if has_alpha_transparency(fill_color):
        fill.background()  # No fill
    else:
        rgb = hex_to_rgb(fill_color)
        if rgb:
            fill.solid()
            fill.fore_color.rgb = RGBColor(*rgb)
        else:
            fill.background()


def _add_text_to_shape(shape, meta: Dict[str, Any], text_style: Dict[str, Any]):
    """
    Add text content (label, tech, note) to a shape's text frame.

    Args:
        shape: The PowerPoint shape
        meta: Metadata dict containing label, tech, note
        text_style: Text style with color and size
    """
    if not shape.has_text_frame:
        return

    tf = shape.text_frame
    tf.word_wrap = True

    # Set vertical alignment (python-pptx 1.0.2 uses vertical_anchor, not anchor)
    valign = meta.get("text_valign", "top")
    if valign == "middle":
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    elif valign == "bottom":
        tf.vertical_anchor = MSO_ANCHOR.BOTTOM
    else:
        tf.vertical_anchor = MSO_ANCHOR.TOP

    # Get text color
    text_color = text_style.get("color", "#000000")
    rgb = hex_to_rgb(text_color)

    # Paragraph spacing from meta (in lines: 0, 0.5, 1, 1.5, 2)
    text_spacing = meta.get("text_spacing", 0.0)
    spacing_pt = Pt(int(text_spacing * 12)) if text_spacing else None

    # Collect text lines
    lines = []
    if meta.get("label"):
        lines.append(("label", meta["label"], meta.get("label_align", "center"), meta.get("label_size", 12), True))
    if meta.get("tech"):
        lines.append(("tech", f"[{meta['tech']}]", meta.get("tech_align", "center"), meta.get("tech_size", 10), False))
    if meta.get("note"):
        lines.append(("note", meta["note"], meta.get("note_align", "center"), meta.get("note_size", 10), False))

    if not lines:
        return

    # Add first line to existing paragraph
    first = True
    for line_type, text, align, size, bold in lines:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        # Use explicit run creation to reliably override theme defaults
        p.clear()
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        if rgb:
            run.font.color.rgb = RGBColor(*rgb)

        # Set alignment
        if align == "left":
            p.alignment = PP_ALIGN.LEFT
        elif align == "right":
            p.alignment = PP_ALIGN.RIGHT
        else:
            p.alignment = PP_ALIGN.CENTER

        # Apply inter-paragraph spacing
        if spacing_pt:
            p.space_before = spacing_pt


def _add_rectangle(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a rectangle shape to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)
    w = px_to_emu(geom.get("w", 100) * scale_x)
    h = px_to_emu(geom.get("h", 100) * scale_y)

    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def _add_rounded_rectangle(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a rounded rectangle shape to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)
    w = px_to_emu(geom.get("w", 100) * scale_x)
    h = px_to_emu(geom.get("h", 100) * scale_y)

    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)

    # Adjust corner radius if possible
    # python-pptx doesn't directly expose corner radius, but we can try via adjustments
    radius = geom.get("adjust1", geom.get("radius", 10))  # Support legacy "radius" key
    try:
        # The adjustment value is a percentage (0-100000)
        # Corner radius is relative to the shorter dimension
        min_dim = min(geom.get("w", 100), geom.get("h", 100))
        if min_dim > 0:
            adj_value = int((radius / min_dim) * 100000)
            adj_value = min(50000, max(0, adj_value))  # Clamp to valid range
            shape.adjustments[0] = adj_value / 100000
    except (IndexError, AttributeError):
        pass  # Not all shapes support adjustments

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def _add_ellipse(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add an ellipse/oval shape to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)
    w = px_to_emu(geom.get("w", 100) * scale_x)
    h = px_to_emu(geom.get("h", 100) * scale_y)

    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def _add_line(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a line connector to the slide."""
    from pptx.enum.dml import MSO_LINE_DASH_STYLE
    from pptx.oxml.ns import qn
    from pptx.oxml import parse_xml
    from lxml import etree

    geom = record.get("geom", {})
    x1 = px_to_emu(geom.get("x1", 0) * scale_x)
    y1 = px_to_emu(geom.get("y1", 0) * scale_y)
    x2 = px_to_emu(geom.get("x2", 100) * scale_x)
    y2 = px_to_emu(geom.get("y2", 100) * scale_y)

    # add_connector expects (connector_type, begin_x, begin_y, end_x, end_y)
    # Pass the actual endpoints directly to preserve line direction
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        x1, y1,
        x2, y2
    )

    # Apply line style
    style = record.get("style", {})
    _apply_line_style(connector.line, style)

    # Handle arrows using XML manipulation (python-pptx doesn't expose this directly)
    arrow_mode = style.get("arrow", "none")
    if arrow_mode != "none":
        # Access the line element in the connector's spPr
        spPr = connector._element.spPr
        ln = spPr.find(qn("a:ln"))
        if ln is None:
            # Create ln element if it doesn't exist
            ln = etree.SubElement(spPr, qn("a:ln"))

        # Add tail (end) arrow
        if arrow_mode in ("end", "both"):
            tail_end = ln.find(qn("a:tailEnd"))
            if tail_end is None:
                tail_end = etree.SubElement(ln, qn("a:tailEnd"))
            tail_end.set("type", "triangle")

        # Add head (start) arrow
        if arrow_mode in ("start", "both"):
            head_end = ln.find(qn("a:headEnd"))
            if head_end is None:
                head_end = etree.SubElement(ln, qn("a:headEnd"))
            head_end.set("type", "triangle")

    # Add text label as a text box at the midpoint of the line
    meta = record.get("meta", {})
    label = meta.get("label", "")
    if label:
        text_style = style.get("text", {})
        font_size = text_style.get("size_pt", 10)
        text_color = text_style.get("color", "#000000")
        rgb = hex_to_rgb(text_color)

        mid_x = (geom.get("x1", 0) + geom.get("x2", 0)) / 2
        mid_y = (geom.get("y1", 0) + geom.get("y2", 0)) / 2

        # Size from meta text_box dimensions or estimate from text
        box_w = meta.get("text_box_width", 0)
        if not box_w:
            box_w = max(50, len(label) * font_size * 0.6 + 20)
        box_h = meta.get("text_box_height", 0)
        if not box_h:
            box_h = font_size * 1.5 + 10

        tx = px_to_emu((mid_x - box_w / 2) * scale_x)
        ty = px_to_emu((mid_y - box_h / 2) * scale_y)
        tw = px_to_emu(box_w * scale_x)
        th = px_to_emu(box_h * scale_y)

        tbox = slide.shapes.add_textbox(tx, ty, tw, th)
        tf = tbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.clear()
        run = p.add_run()
        run.text = label
        run.font.size = Pt(font_size)
        if rgb:
            run.font.color.rgb = RGBColor(*rgb)

        align = meta.get("label_align", "center")
        if align == "left":
            p.alignment = PP_ALIGN.LEFT
        elif align == "right":
            p.alignment = PP_ALIGN.RIGHT
        else:
            p.alignment = PP_ALIGN.CENTER


def _add_text(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a text box to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)

    text = record.get("text", "")
    style = record.get("style", {})
    text_style = style.get("text", {})
    font_size = text_style.get("size_pt", 12)

    # Use geom dimensions when available, otherwise estimate
    if geom.get("w"):
        w = px_to_emu(geom["w"] * scale_x)
    else:
        char_width = font_size * 0.6
        w = px_to_emu(max(50, len(text) * char_width + 20) * scale_x)

    if geom.get("h"):
        h = px_to_emu(geom["h"] * scale_y)
    else:
        h = px_to_emu((font_size * 1.5 + 10) * scale_y)

    shape = slide.shapes.add_textbox(x, y, w, h)

    # Text items have no outline border
    shape.line.fill.background()

    # Apply fill style (usually transparent for text items)
    _apply_fill_style(shape.fill, style)

    tf = shape.text_frame
    tf.word_wrap = True

    # Vertical alignment (python-pptx 1.0.2 uses vertical_anchor, not anchor)
    meta = record.get("meta", {})
    valign = meta.get("text_valign", "top")
    if valign == "middle":
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    elif valign == "bottom":
        tf.vertical_anchor = MSO_ANCHOR.BOTTOM
    else:
        tf.vertical_anchor = MSO_ANCHOR.TOP

    p = tf.paragraphs[0]
    p.clear()
    run = p.add_run()
    run.text = text

    # Apply text styling
    text_color = text_style.get("color", "#000000")
    rgb = hex_to_rgb(text_color)
    run.font.size = Pt(font_size)
    if rgb:
        run.font.color.rgb = RGBColor(*rgb)

    # Horizontal alignment
    align = meta.get("label_align", "center")
    if align == "left":
        p.alignment = PP_ALIGN.LEFT
    elif align == "right":
        p.alignment = PP_ALIGN.RIGHT
    else:
        p.alignment = PP_ALIGN.CENTER


def _add_hexagon(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a hexagon shape to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)
    w = px_to_emu(geom.get("w", 100) * scale_x)
    h = px_to_emu(geom.get("h", 80) * scale_y)

    shape = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, x, y, w, h)

    # Adjust indent ratio (adjust1 is 0.0-0.5, PPTX adjustment is 0.0-0.5)
    adjust1 = geom.get("adjust1", 0.25)
    try:
        shape.adjustments[0] = adjust1
    except (IndexError, AttributeError):
        pass

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def _add_cylinder(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a cylinder (can) shape to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)
    w = px_to_emu(geom.get("w", 80) * scale_x)
    h = px_to_emu(geom.get("h", 120) * scale_y)

    shape = slide.shapes.add_shape(MSO_SHAPE.CAN, x, y, w, h)

    # Adjust cap height ratio (adjust1 is 0.1-0.5, PPTX adjustment is similar)
    adjust1 = geom.get("adjust1", 0.15)
    try:
        shape.adjustments[0] = adjust1
    except (IndexError, AttributeError):
        pass

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def _add_blockarrow(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a block arrow shape to the slide."""
    geom = record.get("geom", {})
    x = px_to_emu(geom.get("x", 0) * scale_x)
    y = px_to_emu(geom.get("y", 0) * scale_y)
    w = px_to_emu(geom.get("w", 150) * scale_x)
    h = px_to_emu(geom.get("h", 60) * scale_y)

    shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, w, h)

    # Adjust shaft width ratio and arrowhead length
    adjust1 = geom.get("adjust1", 0.5)  # shaft width ratio
    adjust2 = geom.get("adjust2", 15)   # arrowhead length in pixels
    try:
        # PPTX RIGHT_ARROW: adj1 = shaft width ratio, adj2 = head length ratio
        shape.adjustments[0] = adjust1
        total_w = geom.get("w", 150)
        if total_w > 0:
            shape.adjustments[1] = adjust2 / total_w
    except (IndexError, AttributeError):
        pass

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def _add_polygon(slide, record: Dict[str, Any], scale_x: float, scale_y: float):
    """Add a polygon (freeform) shape to the slide."""
    geom = record.get("geom", {})
    x = geom.get("x", 0) * scale_x
    y = geom.get("y", 0) * scale_y
    w = geom.get("w", 100) * scale_x
    h = geom.get("h", 100) * scale_y

    points = geom.get("points", [])
    if not points or len(points) < 3:
        # Fall back to rectangle if no valid polygon points
        _add_rectangle(slide, record, scale_x, scale_y)
        return

    # Build freeform shape from relative points
    # points are [[rx, ry], ...] where rx/ry are 0.0-1.0 relative to w/h
    start_x = px_to_emu(x + points[0][0] * w)
    start_y = px_to_emu(y + points[0][1] * h)
    builder = slide.shapes.build_freeform(start_x, start_y)

    # add_line_segments takes an iterable of (x, y) pairs and auto-closes
    vertices = [
        (px_to_emu(x + pt[0] * w), px_to_emu(y + pt[1] * h))
        for pt in points[1:]
    ]
    builder.add_line_segments(vertices, close=True)

    shape = builder.convert_to_shape()

    style = record.get("style", {})
    _apply_line_style(shape.line, style)
    _apply_fill_style(shape.fill, style)

    meta = record.get("meta", {})
    _add_text_to_shape(shape, meta, style.get("text", {}))


def export_to_pptx(
    annotations: List[Dict[str, Any]],
    output_path: str,
    scene_rect: Optional[Dict[str, float]] = None,
    background_png: Optional[str] = None,
) -> None:
    """
    Export annotations to a PowerPoint file.

    Args:
        annotations: List of annotation records from canvas items
        output_path: Path to save the .pptx file
        scene_rect: Scene rectangle with x, y, w, h (for scaling)
        background_png: Optional path to background image
    """
    prs = Presentation()

    # Set slide dimensions based on scene rect
    if scene_rect:
        scene_w = scene_rect.get("w", 800)
        scene_h = scene_rect.get("h", 600)
        prs.slide_width = px_to_emu(scene_w)
        prs.slide_height = px_to_emu(scene_h)
    else:
        scene_w = 800
        scene_h = 600

    # Use blank layout
    blank_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(blank_layout)

    # Calculate scale factors (1:1 if using scene dimensions)
    scale_x = 1.0
    scale_y = 1.0

    # Add background image if provided
    if background_png:
        try:
            from pptx.util import Inches
            import os
            if os.path.exists(background_png):
                slide.shapes.add_picture(
                    background_png,
                    0, 0,
                    prs.slide_width,
                    prs.slide_height
                )
        except Exception:
            pass  # Skip if image can't be added

    # Flatten groups recursively before export
    def _flatten_annotations(anns):
        flat = []
        for rec in anns:
            if rec.get("kind") == "group":
                flat.extend(_flatten_annotations(rec.get("children", [])))
            else:
                flat.append(rec)
        return flat

    annotations = _flatten_annotations(annotations)

    # Sort annotations by z-index to maintain layering
    sorted_annotations = sorted(
        annotations,
        key=lambda a: a.get("z", 0)
    )

    # Add each shape to the slide
    for record in sorted_annotations:
        kind = record.get("kind", "")

        if kind == "rect":
            _add_rectangle(slide, record, scale_x, scale_y)
        elif kind == "roundedrect":
            _add_rounded_rectangle(slide, record, scale_x, scale_y)
        elif kind == "ellipse":
            _add_ellipse(slide, record, scale_x, scale_y)
        elif kind == "line":
            _add_line(slide, record, scale_x, scale_y)
        elif kind == "text":
            _add_text(slide, record, scale_x, scale_y)
        elif kind == "hexagon":
            _add_hexagon(slide, record, scale_x, scale_y)
        elif kind == "cylinder":
            _add_cylinder(slide, record, scale_x, scale_y)
        elif kind == "blockarrow":
            _add_blockarrow(slide, record, scale_x, scale_y)
        elif kind == "polygon":
            _add_polygon(slide, record, scale_x, scale_y)

    prs.save(output_path)
