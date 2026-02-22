"""
gemini/worker.py

Background worker for Gemini AI diagram extraction.
Uses JSON Schema for structured output validation.
"""

from __future__ import annotations

import json as _json
import os
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PyQt6.QtCore import QObject, pyqtSignal

from PIL import Image

from utils import extract_first_json_object


def _load_geom_schema_info() -> Dict[str, Dict[str, Any]]:
    """Load adjust parameter descriptions from annotation_schema.json.

    Returns a dict keyed by kind, each value is a dict of adjust param info:
    ``{"adjust1": {"description": ..., "min": ..., "max": ..., "default": ...}, ...}``
    """
    schema_path = Path(__file__).parent.parent / "schemas" / "annotation_schema.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = _json.load(f)
    except Exception:
        return {}

    defs = schema.get("$defs", {})
    # Map from kind to the geometry $ref name
    kind_to_geom_def = {
        "rect": "rectGeometry",
        "roundedrect": "roundedRectGeometry",
        "ellipse": "rectGeometry",
        "line": "lineGeometry",
        "text": "pointGeometry",
        "hexagon": "hexagonGeometry",
        "cylinder": "cylinderGeometry",
        "blockarrow": "blockArrowGeometry",
        "curve": "curveGeometry",
    }

    result: Dict[str, Dict[str, Any]] = {}
    for kind, def_name in kind_to_geom_def.items():
        geom_def = defs.get(def_name, {})
        props = geom_def.get("properties", {})
        adjust_info: Dict[str, Any] = {}
        for key in ("adjust1", "adjust2"):
            if key in props:
                p = props[key]
                adjust_info[key] = {
                    "description": p.get("description", key),
                    "min": p.get("minimum"),
                    "max": p.get("maximum"),
                    "default": p.get("default"),
                    "ui_label": p.get("ui_label", ""),
                }
        if adjust_info:
            result[kind] = adjust_info
    return result


# Loaded once at import time
_GEOM_SCHEMA_INFO = _load_geom_schema_info()


def _hex_to_color_name(hex_color: str) -> str:
    """Convert a hex color to an approximate human-readable color name.

    Args:
        hex_color: Color string like "#RRGGBB" or "#RRGGBBAA".

    Returns:
        Approximate color name like "blue", "dark red", "light gray".
    """
    try:
        s = hex_color.strip().lstrip("#")
        if len(s) >= 6:
            r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        else:
            return hex_color
    except (ValueError, IndexError):
        return hex_color

    # Grayscale check
    if abs(r - g) < 30 and abs(g - b) < 30:
        avg = (r + g + b) // 3
        if avg < 40:
            return "black"
        if avg < 100:
            return "dark gray"
        if avg < 180:
            return "gray"
        if avg < 230:
            return "light gray"
        return "white"

    # Determine dominant channel(s)
    mx = max(r, g, b)
    brightness = "dark " if mx < 128 else ""

    if r > g and r > b:
        if g > b + 40:
            return f"{brightness}orange/yellow"
        return f"{brightness}red"
    if g > r and g > b:
        if r > b + 40:
            return f"{brightness}yellow-green"
        return f"{brightness}green"
    if b > r and b > g:
        if r > g + 40:
            return f"{brightness}purple/violet"
        return f"{brightness}blue"
    if r > b and g > b:
        return f"{brightness}yellow"
    if r > g and b > g:
        return f"{brightness}magenta/pink"
    if g > r and b > r:
        return f"{brightness}cyan/teal"

    return hex_color


def _get_adjust_aliases(kind: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Get friendly aliases for adjust parameters based on schema ui_label.

    Args:
        kind: Shape kind string.

    Returns:
        (forward_map, reverse_map) where:
        - forward_map: {"adjust1": "corner_radius", ...} for building prompts
        - reverse_map: {"corner_radius": "adjust1", ...} for parsing responses
    """
    schema_info = _GEOM_SCHEMA_INFO.get(kind, {})
    forward: Dict[str, str] = {}
    reverse: Dict[str, str] = {}
    for key in ("adjust1", "adjust2"):
        if key in schema_info:
            info = schema_info[key]
            ui_label = info.get("ui_label", "").strip()
            if ui_label:
                # Convert to snake_case-like alias, e.g. "Radius" -> "radius"
                alias = ui_label.lower().replace(" ", "_")
                forward[key] = alias
                reverse[alias] = key
    return forward, reverse


# Kinds that use bounding-box geometry (left/top/right/bottom edges)
_BBOX_KINDS = frozenset([
    "rect", "roundedrect", "ellipse", "hexagon",
    "cylinder", "blockarrow", "polygon", "curve",
])


def _build_geom_fields_str(kind: str) -> str:
    """Build a geometry fields description string for a given kind.

    Bounding-box shapes use left/top/right/bottom edges (easier for the model
    to identify than x/y/w/h which require subtraction).  Lines keep x1/y1/x2/y2.
    """
    if kind in _BBOX_KINDS:
        fields = "left, top, right, bottom"
    elif kind == "line":
        fields = "x1, y1, x2, y2"
    elif kind == "text":
        fields = "x, y"
    else:
        fields = "left, top, right, bottom"

    forward, _ = _get_adjust_aliases(kind)
    schema_info = _GEOM_SCHEMA_INFO.get(kind, {})
    explanations = []

    if kind in _BBOX_KINDS:
        explanations.append(
            '  "left": x-pixel of the leftmost border edge')
        explanations.append(
            '  "top": y-pixel of the topmost border edge')
        explanations.append(
            '  "right": x-pixel of the rightmost border edge')
        explanations.append(
            '  "bottom": y-pixel of the bottommost border edge')
    elif kind == "line":
        explanations.append(
            '  "x1","y1": pixel position of the first endpoint (or arrowhead tip)')
        explanations.append(
            '  "x2","y2": pixel position of the second endpoint (or arrowhead tip)')

    for key in ("adjust1", "adjust2"):
        if key in schema_info:
            info = schema_info[key]
            alias = forward.get(key, key)
            range_parts = []
            if info.get("min") is not None:
                range_parts.append(f"min {info['min']}")
            if info.get("max") is not None:
                range_parts.append(f"max {info['max']}")
            if info.get("default") is not None:
                range_parts.append(f"default {info['default']}")
            range_str = f" ({', '.join(range_parts)})" if range_parts else ""
            fields += f", {alias}"
            explanations.append(
                f'  "{alias}": {info["description"]}{range_str}')

    if explanations:
        fields += "\n" + "\n".join(explanations)
    return fields


# Optional Gemini import
try:
    from google import genai
except Exception:
    genai = None

# Import schema validation utilities
try:
    from schemas import validate_annotation, normalize_annotation, quick_validate_annotation, VALID_KINDS
    HAS_SCHEMA = True
except ImportError:
    HAS_SCHEMA = False
    VALID_KINDS = ["rect", "roundedrect", "ellipse", "line", "text", "hexagon", "cylinder", "blockarrow", "polygon"]


def validate_and_fix_annotations(data: Dict) -> Tuple[Dict, List[str]]:
    """
    Validate and fix annotations in the extracted data.
    Returns the fixed data and a list of warnings/fixes applied.
    """
    warnings = []
    annotations = data.get("annotations", [])

    if not isinstance(annotations, list):
        warnings.append("annotations field is not a list, replacing with empty list")
        data["annotations"] = []
        return data, warnings

    fixed_annotations = []
    for i, ann in enumerate(annotations):
        if not isinstance(ann, dict):
            warnings.append(f"Annotation {i}: not a dict, skipping")
            continue

        kind = ann.get("kind")
        if kind not in VALID_KINDS:
            warnings.append(f"Annotation {i}: invalid kind '{kind}', skipping")
            continue

        # Quick validation
        if HAS_SCHEMA:
            is_valid, error = quick_validate_annotation(ann)
            if not is_valid:
                warnings.append(f"Annotation {i}: {error}, attempting to fix")
                # Try to normalize/fix the annotation
                try:
                    ann = normalize_annotation(ann)
                except Exception as e:
                    warnings.append(f"Annotation {i}: could not fix: {e}, skipping")
                    continue

        # Ensure required fields exist
        if "geom" not in ann:
            warnings.append(f"Annotation {i}: missing geom, skipping")
            continue

        # Fix common issues
        geom = ann.get("geom", {})

        # Ensure numeric values
        for key in geom:
            if not isinstance(geom[key], (int, float)):
                try:
                    geom[key] = round(float(geom[key]), 2)
                    warnings.append(f"Annotation {i}: converted geom.{key} to number")
                except (ValueError, TypeError):
                    warnings.append(f"Annotation {i}: invalid geom.{key}, skipping")
                    continue

        # Ensure positive dimensions for shapes
        if kind in ["rect", "roundedrect", "ellipse", "hexagon", "cylinder", "blockarrow", "polygon"]:
            if geom.get("w", 0) <= 0 or geom.get("h", 0) <= 0:
                warnings.append(f"Annotation {i}: invalid dimensions, skipping")
                continue

        # Migrate legacy "text" field — lines use meta.label, others use meta.note
        if "text" in ann:
            legacy_text = ann.pop("text")
            meta = ann.setdefault("meta", {})
            if kind == "line":
                if not meta.get("label") and legacy_text:
                    meta["label"] = legacy_text
                    warnings.append(f"Annotation {i}: migrated text to meta.label")
            else:
                if not meta.get("note") and legacy_text:
                    meta["note"] = legacy_text
                    warnings.append(f"Annotation {i}: migrated text to meta.note")
        # Ensure text items have meta.note
        if kind == "text":
            meta = ann.setdefault("meta", {})
            if not meta.get("note"):
                meta["note"] = meta.get("label", "") or "Text"
                warnings.append(f"Annotation {i}: added missing meta.note")

        # Fill in all missing schema fields with defaults
        try:
            ann = normalize_annotation(ann)
        except Exception:
            pass  # Keep as-is if normalization fails

        fixed_annotations.append(ann)

    data["annotations"] = fixed_annotations
    return data, warnings


class ExtractWorker(QObject):
    """
    Background worker that extracts diagram annotations using Gemini AI.
    Uses JSON Schema to validate and normalize extracted items.

    Signals:
        finished(dict): Emitted with parsed and validated JSON result on success
        failed(str): Emitted with error message on failure
        raw_text(str): Emitted with raw API response text
    """

    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)
    raw_text = pyqtSignal(str)
    tokens_used = pyqtSignal(int)

    def __init__(self, png_path: str, model: str):
        super().__init__()
        self.png_path = png_path
        self.model = model

    def run(self):
        """Execute the extraction request."""
        try:
            if genai is None:
                raise RuntimeError("google-genai not installed. pip install google-genai")
            api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("GOOGLE_API_KEY is not set.")

            client = genai.Client(api_key=api_key)

            img = Image.open(self.png_path)
            w, h = img.size

            prompt = self._build_extraction_prompt(w, h)

            response = client.models.generate_content(
                model=self.model,
                contents=[prompt, img],
            )

            text = getattr(response, "text", None) or ""
            self.raw_text.emit(text)

            usage = getattr(response, "usage_metadata", None)
            if usage:
                total = getattr(usage, "total_token_count", 0) or 0
                if total > 0:
                    self.tokens_used.emit(total)

            parsed = extract_first_json_object(text)
            if parsed is None:
                raise ValueError("Model response did not contain parseable JSON.")

            # Validate and fix annotations
            parsed, warnings = validate_and_fix_annotations(parsed)

            # Add warnings to the data for user visibility
            if warnings:
                parsed["_extraction_warnings"] = warnings

            self.finished.emit(parsed)

        except Exception as e:
            msg = f"{e}\n\n{traceback.format_exc()}"
            self.failed.emit(msg)

    def _build_extraction_prompt(self, width: int, height: int) -> str:
        """Build the extraction prompt with schema-based structure."""
        return f"""You are a diagram element extractor. Analyze this image and extract all visual elements.

IMPORTANT: This image is EXACTLY {width} pixels wide and {height} pixels tall.
All coordinates in your response MUST be in ABSOLUTE PIXEL values within this {width}x{height} pixel space.
Do NOT use normalized coordinates (0-1), do NOT use a 0-1000 range. Use raw pixel positions.
For example, a shape at the horizontal center should have x ≈ {width // 2}, not x ≈ 0.5 or x ≈ 500.
A shape halfway down should have y ≈ {height // 2}, not y ≈ 0.5 or y ≈ 500.

Return ONLY valid JSON (no markdown code fences) matching this exact schema:

{{
  "version": "draft-1",
  "image": {{ "width": {width}, "height": {height} }},
  "annotations": [<array of annotation objects>]
}}

Each annotation object must have this structure:

FOR RECTANGLES (sharp corners):
{{
  "kind": "rect",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number> }},
  "meta": {{ "label": "<text inside>", "tech": "<technology if shown>", "note": "<description>" }},
  "text": "<C4 format: Label [Tech] Description>",
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "fill": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR ROUNDED RECTANGLES (rounded corners):
{{
  "kind": "roundedrect",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number>, "adjust1": <corner radius in pixels> }},
  "meta": {{ "label": "<text inside>", "tech": "<technology if shown>", "note": "<description>" }},
  "text": "<C4 format: Label [Tech] Description>",
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "fill": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR ELLIPSES/CIRCLES (ovals, actors, users):
{{
  "kind": "ellipse",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number> }},
  "meta": {{ "label": "<text inside>", "note": "<description>" }},
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "fill": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR HEXAGONS (six-sided shapes, often used for processes, services, or decision nodes):
{{
  "kind": "hexagon",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number>, "adjust1": <indent ratio 0.0-0.5, default 0.25> }},
  "meta": {{ "label": "<text inside>", "tech": "<technology if shown>", "note": "<description>" }},
  "text": "<C4 format: Label [Tech] Description>",
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "fill": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR CYLINDERS (database/storage shapes with curved top and bottom):
{{
  "kind": "cylinder",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number>, "adjust1": <cap ratio 0.1-0.5, default 0.15> }},
  "meta": {{ "label": "<text inside>", "tech": "<technology if shown>", "note": "<description>" }},
  "text": "<C4 format: Label [Tech] Description>",
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "fill": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR BLOCK ARROWS (thick arrow shapes pointing right, used for flow direction or processes):
{{
  "kind": "blockarrow",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number>, "adjust1": <shaft width ratio 0.2-0.9, default 0.5>, "adjust2": <arrowhead length in pixels, default 15> }},
  "meta": {{ "label": "<text inside>", "tech": "<technology if shown>", "note": "<description>" }},
  "text": "<C4 format: Label [Tech] Description>",
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "fill": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR LINES/ARROWS (connections, relationships):
{{
  "kind": "line",
  "geom": {{ "x1": <start x>, "y1": <start y>, "x2": <end x>, "y2": <end y> }},
  "text": "<text label on or near the line>",
  "meta": {{ "label": "<text label on or near the line - same as text field>", "tech": "<protocol if shown: HTTP, gRPC, etc.>", "note": "" }},
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2,"dash":"solid|dashed","dash_pattern_length":30,"dash_solid_percent":50}},
    "arrow": "none|start|end|both",
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR TEXT LABELS (standalone text NOT associated with any shape or line):
{{
  "kind": "text",
  "geom": {{ "x": <number>, "y": <number> }},
  "text": "<the text content>",
  "meta": {{ "label": "<category>" }},
  "style": {{ "text": {{"color":"#RRGGBB","size_pt":<font size>}} }}
}}

COORDINATE RULES:
- Image is {width} pixels wide and {height} pixels tall
- Origin (0,0) is top-left corner of the image
- x increases rightward (0 to {width}), y increases downward (0 to {height})
- ALL values must be ABSOLUTE PIXEL coordinates (NOT normalized 0-1, NOT 0-1000 range)
- A shape touching the right edge has x + w = {width}; a shape touching the bottom has y + h = {height}
- The output bounding box must EXACTLY OVERLAY the shape as it appears in the PNG

BOUNDING BOX EXTRACTION (CRITICAL - follow these steps for EVERY shape):
Step 1: Find the four EDGES of the shape by scanning the image:
  * LEFT EDGE:   find the leftmost visible pixel of the shape's border/fill → this is geom.x
  * TOP EDGE:    find the topmost visible pixel of the shape's border/fill → this is geom.y
  * RIGHT EDGE:  find the rightmost visible pixel of the shape's border/fill → right_x
  * BOTTOM EDGE: find the bottommost visible pixel of the shape's border/fill → bottom_y
Step 2: Calculate dimensions:
  * geom.w = right_x - geom.x
  * geom.h = bottom_y - geom.y
Step 3: VERIFY the bounding box covers the ENTIRE shape:
  * The shape's leftmost pixel must be at geom.x (NOT to the left of it)
  * The shape's topmost pixel must be at geom.y (NOT above it)
  * The shape's rightmost pixel must be at geom.x + geom.w (NOT to the right of it)
  * The shape's bottommost pixel must be at geom.y + geom.h (NOT below it)
  * 0 <= geom.x and geom.x + geom.w <= {width}
  * 0 <= geom.y and geom.y + geom.h <= {height}

COMMON MISTAKES TO AVOID:
- Do NOT estimate x from the shape's center or text position - use the LEFTMOST visible edge
- For HEXAGONS: x must be the leftmost pointed vertex, NOT the left side of the text area
- For CYLINDERS: y must be the very top of the curved elliptical cap, x must be the leftmost edge of the cylinder body
- For BLOCK ARROWS: x must be the left flat edge of the shaft, NOT the center of the arrow
- Shapes are often wider and taller than they first appear due to borders and vertices

DETECTION GUIDELINES:
1. Detect ALL visible shapes: boxes, containers, components, actors, databases, processes
2. Distinguish sharp corners (rect) from rounded corners (roundedrect)
3. Estimate corner radius in pixels for rounded rectangles
4. Identify hexagonal shapes (six-sided polygons) as "hexagon"
5. Identify cylinder/drum shapes (databases, storage) as "cylinder" - these have curved/elliptical top and bottom caps
6. Identify thick block arrow shapes as "blockarrow" - these are filled arrow-shaped polygons, NOT line arrows
7. Detect connection lines and their arrow directions
8. Extract text labels inside shapes into that shape's meta.label field
9. For text, estimate the font size in points

LINE LABEL ASSOCIATION (IMPORTANT):
- Text that overlays, crosses, or is positioned near a line/arrow belongs TO that line
- Include such text in BOTH the line's "text" field AND meta.label field
- Common line labels: relationship names, protocols (HTTP, gRPC), actions (reads, writes, calls)
- Do NOT create separate "text" items for labels that belong to lines
- Only create standalone "text" items for text that is NOT associated with any shape or line
- If text appears between two shapes along a line path, it's a line label

COLOR EXTRACTION (IMPORTANT):
- Extract the EXACT visible colors from the diagram
- style.pen.color: The stroke/border color of the shape
- style.fill.color: The fill/background color of the shape (use alpha for transparency)
- style.text.color: The color of text INSIDE or ON the element - MUST match the original text color
- Common text colors: white text on dark backgrounds (#FFFFFF), black text on light backgrounds (#000000)
- Look carefully at text color contrast against the background
- For each shape, include style.text.color matching the color of any text labels within that shape
- Use proper hex format: #RRGGBB for opaque colors, #RRGGBBAA for colors with alpha

DASH STYLE DETECTION (IMPORTANT):
- Examine every line and shape border for solid vs dashed strokes
- style.pen.dash: "solid" for continuous lines, "dashed" for broken/dotted lines
- style.pen.dash_pattern_length: estimated total length of one dash+gap cycle in pixels (default 30)
- style.pen.dash_solid_percent: estimated percentage of the pattern that is solid (default 50)
- Always include all three dash properties for every pen style

ARROW DETECTION:
- Arrow at end (toward x2,y2): "end"
- Arrow at start (toward x1,y1): "start"
- Arrows at both ends: "both"
- No arrows: "none"

OUTPUT REQUIREMENTS:
- Return ONLY the JSON object, no explanation
- Ensure all coordinates are numbers, not strings
- Include all visible diagram elements
- If uncertain about an element, include it with meta.note="uncertain"
"""


class FocusedAlignWorker(QObject):
    """Background worker that refines a single annotation by sending
    a cropped ROI from the PNG to Gemini AI.

    Uses iterative refinement: the first pass finds the shape, then
    subsequent passes re-crop tighter around the previous result and
    ask Gemini to correct its answer.

    Signals:
        finished(dict): Emitted with refined annotation dict on success
        failed(str): Emitted with error message on failure
        progress(int, str): Emitted with (iteration, message) during work
    """

    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    tokens_used = pyqtSignal(int)

    def __init__(self, png_path: str, model: str, record: dict,
                 padding: int = 0, max_iterations: int = 1):
        """Create a focused alignment worker.

        Args:
            png_path: Path to the background PNG image.
            model: Gemini model name to use.
            record: Annotation record dict from item.to_record().
            padding: Extra padding in pixels (0 = auto-compute).
            max_iterations: Number of refinement passes (1 = single shot).
        """
        super().__init__()
        self.png_path = png_path
        self.model = model
        self.record = record
        self.padding = padding
        self.max_iterations = max_iterations

    def run(self):
        """Execute the iterative focused alignment request."""
        try:
            if genai is None:
                raise RuntimeError("google-genai not installed. pip install google-genai")
            api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("GOOGLE_API_KEY is not set.")

            client = genai.Client(api_key=api_key)

            img = Image.open(self.png_path)
            img_w, img_h = img.size

            # Current best estimate of the geometry (in image space)
            current_geom = dict(self.record.get("geom", {}))
            kind = self.record.get("kind", "")
            result = None

            for iteration in range(1, self.max_iterations + 1):
                self.progress.emit(iteration,
                    f"Pass {iteration}/{self.max_iterations}")

                # Compute ROI from current best estimate
                # Tighter padding on refinement passes
                pad_factor = 1.0 if iteration == 1 else 0.5
                crop_x, crop_y, crop_w, crop_h = self._compute_roi_from_geom(
                    current_geom, kind, img_w, img_h, pad_factor)

                crop_img = img.crop((
                    crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

                # Build prompt — initial or refinement
                if iteration == 1:
                    prompt = self._build_focused_prompt(
                        crop_w, crop_h, crop_x, crop_y)
                else:
                    # Translate current result back to crop-space for the prompt
                    prev_crop_geom = self._to_crop_space(
                        current_geom, kind, crop_x, crop_y)
                    prompt = self._build_refinement_prompt(
                        crop_w, crop_h, prev_crop_geom, iteration)

                # Debug: print prompt and crop info to console
                print(f"\n{'='*60}")
                print(f"FOCUS ALIGN [{self.model}] Pass {iteration}/{self.max_iterations}")
                print(f"Crop: x={crop_x} y={crop_y} w={crop_w} h={crop_h}")
                print(f"{'='*60}")
                print(prompt)
                print(f"{'='*60}\n")

                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt, crop_img],
                )

                text = getattr(response, "text", None) or ""

                usage = getattr(response, "usage_metadata", None)
                if usage:
                    total = getattr(usage, "total_token_count", 0) or 0
                    if total > 0:
                        self.tokens_used.emit(total)

                print(f"--- Gemini response (pass {iteration}) ---")
                print(text[:1000])
                print(f"--- end response ---\n")

                parsed = extract_first_json_object(text)
                if parsed is None:
                    if iteration == 1:
                        raise ValueError(
                            f"Gemini response did not contain parseable JSON."
                            f"\n\nRaw response:\n{text[:500]}")
                    # Refinement failed to parse — keep previous result
                    break

                result = self._translate_to_image_space(
                    parsed, crop_x, crop_y, crop_w, crop_h)

                print(f"--- Translated to image-space (pass {iteration}) ---")
                print(f"  geom: {result.get('geom')}")
                print(f"  style: {result.get('style')}")
                print(f"---\n")

                # Update current_geom for the next iteration
                current_geom = dict(result.get("geom", current_geom))

                # Save the actual crop used in this iteration
                last_crop = (crop_x, crop_y, crop_w, crop_h)

            if result is None:
                raise ValueError("No valid result from any iteration.")

            # Attach the ACTUAL crop that was sent to Gemini (not recomputed)
            result["_crop"] = {
                "x": last_crop[0], "y": last_crop[1],
                "w": last_crop[2], "h": last_crop[3],
                "png_path": self.png_path,
                "iterations": self.max_iterations,
            }

            self.finished.emit(result)

        except Exception as e:
            msg = f"{e}\n\n{traceback.format_exc()}"
            self.failed.emit(msg)

    def _compute_roi_from_geom(self, geom: dict, kind: str,
                                img_w: int, img_h: int,
                                pad_factor: float = 1.0) -> Tuple[int, int, int, int]:
        """Compute the Region of Interest bounding box from a geometry dict.

        Args:
            geom: Geometry dict (may be the original or a refined estimate).
            kind: Shape kind string.
            img_w: Full image width in pixels.
            img_h: Full image height in pixels.
            pad_factor: Multiplier for padding (1.0 = full, 0.5 = tighter).

        Returns:
            (crop_x, crop_y, crop_w, crop_h) tuple clamped to image bounds.
        """
        if kind == "line":
            x_min = min(geom.get("x1", 0), geom.get("x2", 0))
            y_min = min(geom.get("y1", 0), geom.get("y2", 0))
            x_max = max(geom.get("x1", 0), geom.get("x2", 0))
            y_max = max(geom.get("y1", 0), geom.get("y2", 0))
            elem_w = x_max - x_min
            elem_h = y_max - y_min
        elif kind == "text":
            x_min = geom.get("x", 0)
            y_min = geom.get("y", 0)
            elem_w = 200
            elem_h = 50
            x_max = x_min + elem_w
            y_max = y_min + elem_h
        elif kind == "curve":
            x_min = geom.get("x", 0)
            y_min = geom.get("y", 0)
            elem_w = geom.get("w", 100)
            elem_h = geom.get("h", 100)
            x_max = x_min + elem_w
            y_max = y_min + elem_h
        else:
            x_min = geom.get("x", 0)
            y_min = geom.get("y", 0)
            elem_w = geom.get("w", 100)
            elem_h = geom.get("h", 100)
            x_max = x_min + elem_w
            y_max = y_min + elem_h

        max_dim = max(elem_w, elem_h, 1)
        base_pad = self.padding if self.padding > 0 else max(80, int(0.5 * max_dim))
        pad = int(base_pad * pad_factor)

        crop_x = max(0, int(x_min - pad))
        crop_y = max(0, int(y_min - pad))
        crop_x2 = min(img_w, int(x_max + pad))
        crop_y2 = min(img_h, int(y_max + pad))

        return crop_x, crop_y, crop_x2 - crop_x, crop_y2 - crop_y

    def _build_focused_prompt(self, crop_w: int, crop_h: int,
                              crop_x: int, crop_y: int) -> str:
        """Build a prompt that gives Gemini the current estimate and asks
        it to verify/correct each edge against the actual pixels.

        Args:
            crop_w: Width of the cropped image in pixels.
            crop_h: Height of the cropped image in pixels.
            crop_x: X offset of the crop in the full image.
            crop_y: Y offset of the crop in the full image.

        Returns:
            Prompt string for Gemini.
        """
        kind = self.record.get("kind", "rect")
        meta = self.record.get("meta", {})
        style = self.record.get("style", {})
        geom = self.record.get("geom", {})
        text_content = meta.get("note", "") or self.record.get("text", "")

        # ---- Extract known properties from the record ----
        pen = style.get("pen", {}) or {}
        fill = style.get("fill", {}) or {}
        txt_style = style.get("text", {}) or {}
        pen_color = pen.get("color", "")
        pen_width = pen.get("width", 2)
        pen_dash = pen.get("dash", "solid")
        fill_color = fill.get("color", "")
        text_color = txt_style.get("color", "")
        arrow_mode = style.get("arrow", "")

        label = meta.get("label", "")
        tech = meta.get("tech", "")
        note = meta.get("note", "")

        # ---- Build a detailed description of the shape ----
        shape_description = self._describe_shape(
            kind, geom, pen_color, pen_width, pen_dash, fill_color,
            label, tech, note, text_content, text_color, arrow_mode,
        )

        # ---- Geometry fields expected in response ----
        geom_fields = _build_geom_fields_str(kind)

        # ---- Style template for the response JSON ----
        if kind == "line":
            style_section = """    "pen": {"color": "#RRGGBB", "width": <integer>, "dash": "solid|dashed", "dash_pattern_length": 30, "dash_solid_percent": 50},
    "arrow": "none|start|end|both",
    "text": {"color": "#RRGGBB", "size_pt": <number>}"""
        else:
            style_section = """    "pen": {"color": "#RRGGBB", "width": <integer>, "dash": "solid|dashed", "dash_pattern_length": 30, "dash_solid_percent": 50},
    "fill": {"color": "#RRGGBBAA"},
    "text": {"color": "#RRGGBB", "size_pt": <number>}"""

        return f"""Image size: {crop_w} x {crop_h} pixels. Origin (0,0) = top-left.

FIND THIS ELEMENT:
{shape_description}

TASK: Look at the image and find the element described above.
Report the pixel coordinates of its four edges (where the border starts).
If multiple shapes are visible, pick the one matching the text description.

You may briefly describe what you see before the JSON. End with ONLY a JSON object:

{{
  "kind": "{kind}",
  "geom": {{ {geom_fields} }},
  "style": {{
{style_section}
  }}
}}

Rules:
- All coordinates are absolute pixel positions within this {crop_w}x{crop_h} crop
- Extract exact colors from the image pixels
- Tightly enclose the shape border — no extra padding"""

    @staticmethod
    def _describe_shape(
        kind: str, geom: dict,
        pen_color: str, pen_width: int, pen_dash: str, fill_color: str,
        label: str, tech: str, note: str, text_content: str,
        text_color: str, arrow_mode: str,
    ) -> str:
        """Build a human-readable description of the shape for the prompt.

        Args:
            kind: Shape kind (rect, line, etc.).
            geom: Geometry dict from the record.
            pen_color: Border color hex string.
            pen_width: Border width in pixels.
            pen_dash: "solid" or "dashed".
            fill_color: Fill color hex string (may include alpha).
            label: Meta label text.
            tech: Meta technology text.
            note: Meta note text.
            text_content: The annotation's text field.
            text_color: Text color hex string.
            arrow_mode: Arrow mode for lines ("none", "start", "end", "both").

        Returns:
            Multi-line description string.
        """
        lines = []

        # Shape type with visual characteristics
        shape_names = {
            "rect": "RECTANGLE with sharp 90-degree corners",
            "roundedrect": "ROUNDED RECTANGLE with rounded corners",
            "ellipse": "ELLIPSE (oval or circle)",
            "hexagon": "HEXAGON (six-sided polygon with pointed left/right vertices)",
            "cylinder": "CYLINDER (database/drum shape with curved elliptical top and bottom caps)",
            "blockarrow": "BLOCK ARROW (thick filled arrow shape pointing right)",
            "polygon": "POLYGON (multi-sided closed shape)",
            "line": "LINE / ARROW connector between elements",
            "text": "STANDALONE TEXT label",
            "curve": "CURVED PATH or connector",
        }
        lines.append(f"Type: {shape_names.get(kind, kind.upper())}")

        if kind == "line":
            # Line-specific description
            stroke_parts = []
            if pen_color:
                color_name = _hex_to_color_name(pen_color)
                stroke_parts.append(f"approximately {color_name}")
            if pen_dash == "dashed":
                stroke_parts.append("DASHED")
            else:
                stroke_parts.append("solid")
            lines.append(f"Line style: {', '.join(stroke_parts)}")

            if arrow_mode:
                arrow_desc = {
                    "none": "no arrowheads — find the two bare endpoints",
                    "end": "arrowhead at ONE end - x1,y1 is the non-arrow end, "
                           "x2,y2 is the tip of the arrowhead",
                    "start": "arrowhead at the START - x1,y1 is the arrowhead tip, "
                             "x2,y2 is the non-arrow end",
                    "both": "arrowheads at BOTH ends - x1,y1 and x2,y2 are "
                            "the tips of the two arrowheads",
                }
                lines.append(f"Arrow: {arrow_desc.get(arrow_mode, arrow_mode)}")

            lines.append("ENDPOINT RULES: x1,y1 and x2,y2 must be the exact pixel "
                         "positions where the line/arrow starts and ends. For arrows, "
                         "use the tip of the arrowhead, not the base.")
        else:
            # Shape border / stroke — describe qualitatively
            border_parts = []
            if pen_color:
                color_name = _hex_to_color_name(pen_color)
                border_parts.append(f"approximately {color_name} colored")
            if pen_dash == "dashed":
                border_parts.append("DASHED line style")
            else:
                border_parts.append("solid line style")
            lines.append(f"Border/stroke: {', '.join(border_parts)}")

            # Fill color — qualitative
            if kind != "text" and fill_color:
                if fill_color.upper() in ("#00000000", "#FFFFFF00"):
                    lines.append("Fill: transparent (no fill)")
                else:
                    fill_name = _hex_to_color_name(fill_color)
                    lines.append(f"Fill/background: approximately {fill_name}")

        # Text content — PRIMARY identifier for finding the right shape
        text_parts = []
        if label:
            text_parts.append(f'label "{label}"')
        if tech:
            text_parts.append(f'technology tag "[{tech}]"')
        if note and note != label:
            text_parts.append(f'description "{note}"')
        if text_content and text_content != label:
            text_parts.append(f'full text "{text_content}"')

        if text_parts:
            lines.append(f"Text content (use this to identify the shape): "
                         f"{', '.join(text_parts)}")
        else:
            lines.append("Text content: none visible")

        lines.append("")
        lines.append("NOTE: All colors and sizes above are approximate. "
                     "Measure exact values from the image pixels.")

        return "\n".join(f"  {l}" for l in lines)

    @staticmethod
    def _to_crop_space(geom: dict, kind: str,
                       crop_x: int, crop_y: int) -> dict:
        """Convert image-space geometry to crop-relative coordinates.

        For bbox shapes, converts x/y/w/h to left/top/right/bottom edges
        since that's what the prompt asks for. Also renames adjust keys
        to their ui_label aliases.

        Args:
            geom: Geometry dict in full-image coordinates.
            kind: Shape kind string.
            crop_x: X offset of the crop.
            crop_y: Y offset of the crop.

        Returns:
            New dict with crop-relative edge coordinates and aliased keys.
        """
        cg = dict(geom)
        if kind == "line":
            cg["x1"] = round(cg.get("x1", 0) - crop_x, 1)
            cg["y1"] = round(cg.get("y1", 0) - crop_y, 1)
            cg["x2"] = round(cg.get("x2", 0) - crop_x, 1)
            cg["y2"] = round(cg.get("y2", 0) - crop_y, 1)
        elif kind in _BBOX_KINDS:
            # Convert x/y/w/h to left/top/right/bottom edges
            x = cg.pop("x", 0)
            y = cg.pop("y", 0)
            w = cg.pop("w", 0)
            h = cg.pop("h", 0)
            cg["left"] = round(x - crop_x, 1)
            cg["top"] = round(y - crop_y, 1)
            cg["right"] = round(x + w - crop_x, 1)
            cg["bottom"] = round(y + h - crop_y, 1)
        else:
            cg["x"] = round(cg.get("x", 0) - crop_x, 1)
            cg["y"] = round(cg.get("y", 0) - crop_y, 1)

        # Rename adjust keys to ui_label aliases for the prompt
        forward, _ = _get_adjust_aliases(kind)
        for adjust_key, alias in forward.items():
            if adjust_key in cg:
                cg[alias] = cg.pop(adjust_key)

        return cg

    def _build_refinement_prompt(self, crop_w: int, crop_h: int,
                                  prev_geom: dict, iteration: int) -> str:
        """Build a refinement prompt that shows the previous estimate.

        Args:
            crop_w: Width of the cropped image in pixels.
            crop_h: Height of the cropped image in pixels.
            prev_geom: Previous geometry estimate in crop-space.
            iteration: Current iteration number (2+).

        Returns:
            Prompt string for Gemini.
        """
        kind = self.record.get("kind", "rect")
        meta = self.record.get("meta", {})
        style = self.record.get("style", {})
        text_content = meta.get("note", "") or self.record.get("text", "")

        pen = style.get("pen", {}) or {}
        fill = style.get("fill", {}) or {}
        arrow_mode = style.get("arrow", "")
        label = meta.get("label", "")
        tech = meta.get("tech", "")
        note = meta.get("note", "")

        shape_description = self._describe_shape(
            kind, self.record.get("geom", {}),
            pen.get("color", ""), pen.get("width", 2), pen.get("dash", "solid"),
            fill.get("color", ""), label, tech, note, text_content,
            (style.get("text", {}) or {}).get("color", ""), arrow_mode,
        )

        # Format previous geometry as JSON snippet
        import json
        prev_geom_str = json.dumps(prev_geom, indent=2)

        # Geometry fields for the response
        geom_fields = _build_geom_fields_str(kind)

        if kind == "line":
            style_section = """  "style": {
    "pen": {"color": "#RRGGBB", "width": <integer>, "dash": "solid|dashed", "dash_pattern_length": 30, "dash_solid_percent": 50},
    "arrow": "none|start|end|both",
    "text": {"color": "#RRGGBB", "size_pt": <number>}
  }"""
        else:
            style_section = """  "style": {
    "pen": {"color": "#RRGGBB", "width": <integer>, "dash": "solid|dashed", "dash_pattern_length": 30, "dash_solid_percent": 50},
    "fill": {"color": "#RRGGBBAA"},
    "text": {"color": "#RRGGBB", "size_pt": <number>}
  }"""

        return f"""Refinement pass {iteration}. Image: {crop_w}x{crop_h} pixels, origin (0,0) = top-left.

FIND THIS ELEMENT:
{shape_description}

A previous pass returned this (it may be WRONG — re-measure from the image):
{prev_geom_str}

Report the pixel coordinates of the element's edges by examining the actual image.
You may briefly describe what you see before the JSON. End with ONLY a JSON object:

{{
  "kind": "{kind}",
  "geom": {{ {geom_fields} }},
{style_section}
}}

Rules:
- All coordinates are absolute pixel positions within this {crop_w}x{crop_h} crop
- Tightly enclose the shape border — no extra padding"""

    def _translate_to_image_space(
        self, result: dict, crop_x: int, crop_y: int, crop_w: int, crop_h: int
    ) -> dict:
        """Translate crop-space coordinates back to full-image space.

        Args:
            result: Parsed JSON result with crop-relative coordinates.
            crop_x: X offset of the crop in the full image.
            crop_y: Y offset of the crop in the full image.
            crop_w: Width of the crop.
            crop_h: Height of the crop.

        Returns:
            Result dict with coordinates in full-image space.
        """
        geom = result.get("geom", {})
        kind = result.get("kind", self.record.get("kind", ""))

        # Safety check: if spatial coords look normalized (all < 2.0), rescale
        _, reverse = _get_adjust_aliases(kind)
        alias_keys = set(reverse.keys())
        spatial_keys = {"x", "y", "w", "h", "x1", "y1", "x2", "y2",
                        "left", "top", "right", "bottom"}
        coord_vals = [v for k, v in geom.items()
                      if isinstance(v, (int, float)) and k in spatial_keys]
        if coord_vals and all(abs(v) < 2.0 for v in coord_vals):
            # Likely normalized 0-1 — multiply by crop dimensions
            for key in list(geom.keys()):
                if not isinstance(geom[key], (int, float)):
                    continue
                if key in alias_keys:
                    continue
                if key in ("x", "x1", "x2", "w", "left", "right"):
                    geom[key] = round(geom[key] * crop_w, 2)
                elif key in ("y", "y1", "y2", "h", "top", "bottom"):
                    geom[key] = round(geom[key] * crop_h, 2)

        # Convert edge-based output (left/top/right/bottom) to x/y/w/h
        if "left" in geom and "right" in geom:
            left = geom.pop("left")
            top = geom.pop("top", 0)
            right = geom.pop("right")
            bottom = geom.pop("bottom", 0)
            geom["x"] = round(float(left), 2)
            geom["y"] = round(float(top), 2)
            geom["w"] = round(float(right) - float(left), 2)
            geom["h"] = round(float(bottom) - float(top), 2)

        # Translate crop-space to image-space
        if kind == "line":
            geom["x1"] = round(geom.get("x1", 0) + crop_x, 2)
            geom["y1"] = round(geom.get("y1", 0) + crop_y, 2)
            geom["x2"] = round(geom.get("x2", 0) + crop_x, 2)
            geom["y2"] = round(geom.get("y2", 0) + crop_y, 2)
        else:
            geom["x"] = round(geom.get("x", 0) + crop_x, 2)
            geom["y"] = round(geom.get("y", 0) + crop_y, 2)
            # w, h do not need translation

        # Map ui_label aliases back to adjust1/adjust2
        for alias, adjust_key in reverse.items():
            if alias in geom:
                geom[adjust_key] = geom.pop(alias)

        result["geom"] = geom
        return result
