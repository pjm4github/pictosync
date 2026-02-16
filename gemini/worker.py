"""
gemini/worker.py

Background worker for Gemini AI diagram extraction.
Uses JSON Schema for structured output validation.
"""

from __future__ import annotations

import os
import traceback
from typing import Dict, List, Tuple

from PyQt6.QtCore import QObject, pyqtSignal

from PIL import Image

from utils import extract_first_json_object

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

        # Ensure text items have text field
        if kind == "text" and "text" not in ann:
            ann["text"] = ann.get("meta", {}).get("note", "") or ann.get("meta", {}).get("label", "") or "Text"
            warnings.append(f"Annotation {i}: added missing text field")

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
    "pen": {{"color":"#RRGGBB","width":2}},
    "brush": {{"color":"#RRGGBBAA"}},
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
    "pen": {{"color":"#RRGGBB","width":2}},
    "brush": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR ELLIPSES/CIRCLES (ovals, actors, users):
{{
  "kind": "ellipse",
  "geom": {{ "x": <number>, "y": <number>, "w": <number>, "h": <number> }},
  "meta": {{ "label": "<text inside>", "note": "<description>" }},
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2}},
    "brush": {{"color":"#RRGGBBAA"}},
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
    "pen": {{"color":"#RRGGBB","width":2}},
    "brush": {{"color":"#RRGGBBAA"}},
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
    "pen": {{"color":"#RRGGBB","width":2}},
    "brush": {{"color":"#RRGGBBAA"}},
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
    "pen": {{"color":"#RRGGBB","width":2}},
    "brush": {{"color":"#RRGGBBAA"}},
    "text": {{"color":"#RRGGBB","size_pt":<font size>}}
  }}
}}

FOR LINES/ARROWS (connections, relationships):
{{
  "kind": "line",
  "geom": {{ "x1": <start x>, "y1": <start y>, "x2": <end x>, "y2": <end y> }},
  "text": "<text label on or near the line>",
  "meta": {{ "label": "", "tech": "<protocol if shown: HTTP, gRPC, etc.>", "note": "<text label on or near the line - same as text field>" }},
  "style": {{
    "pen": {{"color":"#RRGGBB","width":2}},
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
- Include such text in BOTH the line's "text" field AND meta.note field
- Common line labels: relationship names, protocols (HTTP, gRPC), actions (reads, writes, calls)
- Do NOT create separate "text" items for labels that belong to lines
- Only create standalone "text" items for text that is NOT associated with any shape or line
- If text appears between two shapes along a line path, it's a line label

COLOR EXTRACTION (IMPORTANT):
- Extract the EXACT visible colors from the diagram
- style.pen.color: The stroke/border color of the shape
- style.brush.color: The fill/background color of the shape (use alpha for transparency)
- style.text.color: The color of text INSIDE or ON the element - MUST match the original text color
- Common text colors: white text on dark backgrounds (#FFFFFF), black text on light backgrounds (#000000)
- Look carefully at text color contrast against the background
- For each shape, include style.text.color matching the color of any text labels within that shape
- Use proper hex format: #RRGGBB for opaque colors, #RRGGBBAA for colors with alpha

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
