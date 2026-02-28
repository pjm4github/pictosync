"""
mermaid/renderer.py

Render Mermaid SVG files to PNG using Qt's SVG renderer.

Mermaid outputs ``<foreignObject>`` with embedded XHTML for all text
labels.  Qt's ``QSvgRenderer`` cannot render ``<foreignObject>``, so
this module pre-processes the SVG — replacing each ``<foreignObject>``
with a native SVG ``<text>`` element — before rasterising.

The PNG is written to a temporary directory so the original SVG's
directory is never modified.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer

# Register namespaces so ET.write() doesn't mangle them with ns0/ns1 prefixes
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

_SVG_NS = "http://www.w3.org/2000/svg"
_XHTML_NS = "http://www.w3.org/1999/xhtml"


def find_mmdc() -> str | None:
    """Find the Mermaid CLI (mmdc) executable.

    Search order:
        1. PictoSync settings (external_tools.mmdc_path)
        2. MMDC_PATH environment variable
        3. mmdc on system PATH

    Returns:
        Path to mmdc executable if found, None otherwise.
    """
    # 1. PictoSync settings
    try:
        from settings import get_settings
        configured = get_settings().settings.external_tools.mmdc_path
        if configured and os.path.isfile(configured):
            return configured
    except Exception:
        pass

    # 2. Environment variable
    env_path = os.environ.get("MMDC_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    # 3. System PATH
    path_exe = shutil.which("mmdc")
    if path_exe:
        return path_exe

    return None


_C4_DIAGRAM_TYPES = {"C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment"}


def _is_c4_source(source: str) -> bool:
    """Return True if *source* starts with a C4 diagram keyword."""
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        return any(stripped.startswith(dt) for dt in _C4_DIAGRAM_TYPES)
    return False


def _maybe_inject_layout_config(mmd: Path, tmp_dir: str) -> tuple[Path, bool]:
    """Ensure C4 diagrams use the PictoSync layout settings.

    Strips any existing ``UpdateLayoutConfig`` from the source and
    appends a fresh one driven by settings.  PictoSync settings always
    win over source-embedded directives.

    Returns:
        ``(input_path, is_c4)`` — *input_path* is the file to pass to
        mmdc (original or temp copy); *is_c4* indicates whether the
        Puppeteer headed-mode workaround should be used.
    """
    from settings import get_settings

    ext_settings = get_settings().settings.external_tools
    shapes = ext_settings.c4_shapes_per_row
    boundaries = ext_settings.c4_boundaries_per_row

    source = mmd.read_text(encoding="utf-8")

    if not _is_c4_source(source):
        return mmd, False

    has_existing = "UpdateLayoutConfig" in source
    is_default = shapes == 4 and boundaries == 2

    # Nothing to do when source has no config and user hasn't changed settings
    if not has_existing and is_default:
        return mmd, True

    # Strip any existing UpdateLayoutConfig — PictoSync settings take over
    import re as _re
    patched = _re.sub(
        r'\n?[ \t]*UpdateLayoutConfig\([^)]*\)[ \t]*\n?',
        '\n',
        source,
    )

    from debug_trace import trace

    if is_default:
        # Defaults match Mermaid's own natural layout — just strip the
        # source directive so Mermaid auto-arranges freely.
        trace("Stripped source UpdateLayoutConfig; using Mermaid defaults", "MMDC")
    else:
        # User chose non-default values — inject them explicitly.
        trace(
            f"Injecting C4 layout: c4ShapeInRow={shapes}, c4BoundaryInRow={boundaries}",
            "MMDC",
        )
        layout_line = (
            f'\n    UpdateLayoutConfig($c4ShapeInRow="{shapes}"'
            f', $c4BoundaryInRow="{boundaries}")\n'
        )
        patched = patched + layout_line

    patched_path = Path(tmp_dir) / mmd.name
    patched_path.write_text(patched, encoding="utf-8")
    return patched_path, True


def _render_mmd(mmd_path: str, fmt: str, output_path: str | None = None) -> str:
    """Render a .mmd/.mermaid file to the specified format using mmdc.

    Args:
        mmd_path: Path to the Mermaid source file.
        fmt: Output format (``png`` or ``svg``).
        output_path: Optional explicit output path.  If None, the output is
            placed next to the source file using the file stem as name.

    Returns:
        Path to the generated output file.

    Raises:
        RuntimeError: If mmdc cannot be found or rendering fails.
    """
    mmdc = find_mmdc()
    if mmdc is None:
        raise RuntimeError(
            "Mermaid CLI (mmdc) not found.\n\n"
            "Install with:  npm install -g @mermaid-js/mermaid-cli\n\n"
            "Or set the MMDC_PATH environment variable to the mmdc executable."
        )

    mmd = Path(mmd_path).resolve()
    if not mmd.is_file():
        raise RuntimeError(f"Mermaid file not found: {mmd}")

    tmp_dir = tempfile.mkdtemp(prefix="pictosync_mmd_")
    tmp_output = str(Path(tmp_dir) / f"output.{fmt}")

    # Inject C4 layout settings when configured
    input_file, is_c4 = _maybe_inject_layout_config(mmd, tmp_dir)

    cmd = [mmdc, "-i", str(input_file), "-o", tmp_output]
    if fmt == "png":
        from settings import get_settings
        scale = get_settings().settings.external_tools.mmdc_png_scale
        cmd += ["-s", str(scale)]

    # Workaround for mermaid-cli bug: C4 UpdateLayoutConfig and
    # c4ShapeInRow are ignored in headless Puppeteer mode.
    # Using headed mode fixes the layout.  The browser window is
    # moved off-screen so it doesn't distract the user.
    # See: https://github.com/mermaid-js/mermaid-cli/issues/440
    if is_c4:
        puppeteer_cfg = Path(tmp_dir) / "puppeteerrc.json"
        puppeteer_cfg.write_text(
            json.dumps({
                "headless": False,
                "args": ["--window-position=-9999,-9999"],
            }),
            encoding="utf-8",
        )
        cmd += ["-p", str(puppeteer_cfg)]

    from debug_trace import trace
    trace(f"mmdc command: {' '.join(cmd)}", "MMDC")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"mmdc rendering failed (exit {result.returncode}):\n"
            f"{result.stderr.strip()}"
        )

    # Verify output was created
    if not Path(tmp_output).is_file():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"mmdc ran successfully but produced no {fmt.upper()} output.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout: {result.stdout.strip()}\n"
            f"stderr: {result.stderr.strip()}"
        )

    # Decide final destination
    if output_path:
        final = Path(output_path).resolve()
    else:
        final = mmd.with_suffix(f".{fmt}")

    shutil.copy2(tmp_output, str(final))
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return str(final)


def render_mmd_to_png(mmd_path: str, output_png: str | None = None) -> str:
    """Render a .mmd/.mermaid file to PNG using mmdc.

    Args:
        mmd_path: Path to the Mermaid source file.
        output_png: Optional explicit output path.  If None, the PNG is
            placed next to the source file using the file stem as name.

    Returns:
        Path to the generated PNG file.

    Raises:
        RuntimeError: If mmdc cannot be found or rendering fails.
    """
    return _render_mmd(mmd_path, "png", output_png)


def render_mmd_to_svg(mmd_path: str, output_svg: str | None = None) -> str:
    """Render a .mmd/.mermaid file to SVG using mmdc.

    Args:
        mmd_path: Path to the Mermaid source file.
        output_svg: Optional explicit output path.  If None, the SVG is
            placed next to the source file using the file stem as name.

    Returns:
        Path to the generated SVG file.

    Raises:
        RuntimeError: If mmdc cannot be found or rendering fails.
    """
    return _render_mmd(mmd_path, "svg", output_svg)


def render_svg_to_png(svg_path: str, scale: float = 2.0) -> str:
    """Render an SVG file to a PNG in a temporary directory.

    Pre-processes the SVG to replace ``<foreignObject>`` text with
    native SVG ``<text>`` elements that Qt can render, then rasterises
    with ``QSvgRenderer``.

    Args:
        svg_path: Path to the ``.svg`` file.
        scale: Scale factor applied to the SVG's default size.
            ``2.0`` (default) produces a crisp 2x raster.

    Returns:
        Path to the generated PNG file in a temp directory.

    Raises:
        RuntimeError: If the SVG cannot be loaded or rendered.
    """
    fixed_svg = _preprocess_svg_for_qt(svg_path)

    renderer = QSvgRenderer(fixed_svg)
    if not renderer.isValid():
        raise RuntimeError(f"QSvgRenderer could not load SVG: {svg_path}")

    default_size = renderer.defaultSize()
    if default_size.isEmpty():
        raise RuntimeError(f"SVG has no intrinsic size: {svg_path}")

    target_w = int(default_size.width() * scale)
    target_h = int(default_size.height() * scale)

    image = QImage(
        QSize(target_w, target_h),
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    image.fill(Qt.GlobalColor.white)

    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    # Write to temp directory
    tmp_dir = tempfile.mkdtemp(prefix="pictosync_svg_")
    stem = Path(svg_path).stem
    png_path = str(Path(tmp_dir) / f"{stem}.png")

    if not image.save(png_path, "PNG"):
        raise RuntimeError(f"Failed to save rendered PNG: {png_path}")

    return png_path


# ─────────────────────────────────────────────────────────
# SVG pre-processing for Qt compatibility
# ─────────────────────────────────────────────────────────


def _inline_css_classes(root: ET.Element, ns: str) -> None:
    """Inline CSS class rules as SVG presentation attributes on matching elements.

    Qt's ``QSvgRenderer`` does not apply ``<style>`` rules.  This function
    parses SVG-namespace ``<style>`` text, builds a class→properties map,
    then sets matching presentation attributes on every element that carries
    the corresponding ``class`` token.

    Modifies *root* in-place and removes the ``<style>`` elements.

    Args:
        root: Root ``<svg>`` ``Element``.
        ns: SVG namespace string.
    """
    # Presentation attributes that Qt's SVG renderer honours
    _SVG_ATTRS = {
        "stroke", "fill", "stroke-width", "stroke-dasharray",
        "stroke-linecap", "stroke-linejoin", "stroke-opacity",
        "fill-opacity", "opacity", "font-size", "font-family",
        "font-weight", "font-style", "text-anchor",
        "dominant-baseline", "visibility",
    }

    # Collect and remove all SVG-namespace <style> elements
    style_text_parts: List[str] = []
    parent_map = {c: p for p in root.iter() for c in p}
    for style_el in list(root.iter(f"{{{ns}}}style")):
        if style_el.text:
            style_text_parts.append(style_el.text)
        parent = parent_map.get(style_el)
        if parent is not None:
            parent.remove(style_el)

    if not style_text_parts:
        return

    css_text = "\n".join(style_text_parts)

    # Parse class rules — handles selectors like ".edge" or "#mermaid-svg .edge"
    # Captures the last class token and the declaration block
    class_map: Dict[str, Dict[str, str]] = {}
    for m in re.finditer(r'\.([a-zA-Z0-9_-]+)\s*\{([^}]+)\}', css_text):
        cls_name = m.group(1)
        decl_block = m.group(2)
        props: Dict[str, str] = {}
        for prop_m in re.finditer(r'([\w-]+)\s*:\s*([^;]+)', decl_block):
            prop_name = prop_m.group(1).strip()
            prop_val = prop_m.group(2).strip()
            if prop_name in _SVG_ATTRS:
                props[prop_name] = prop_val
        if props:
            if cls_name not in class_map:
                class_map[cls_name] = {}
            class_map[cls_name].update(props)

    if not class_map:
        return

    # Apply to elements
    for el in root.iter():
        cls_attr = el.get("class", "")
        if not cls_attr:
            continue
        for token in cls_attr.split():
            css_props = class_map.get(token)
            if not css_props:
                continue
            for prop, val in css_props.items():
                # Only set if the element doesn't already have an explicit attribute
                if el.get(prop) is None:
                    el.set(prop, val)


def _preprocess_svg_for_qt(svg_path: str) -> str:
    """Create a Qt-compatible copy of a Mermaid SVG.

    Mermaid uses ``<foreignObject>`` with XHTML ``<div>/<span>/<p>``
    for all text labels.  Qt's SVG renderer ignores these entirely.
    This function replaces each ``<foreignObject>`` with a native
    SVG ``<text>`` element positioned at the centre of the original
    foreignObject bounding box.

    Also strips XHTML ``<style>`` elements (e.g. Font Awesome
    ``@import``) that Qt cannot process.

    Args:
        svg_path: Path to the original SVG file.

    Returns:
        Path to a temporary SVG file with the replacements applied.
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # ── Ensure the SVG has a viewBox so Qt can determine its size ──
    # ZenUML and some diagrams use width="100%" with no viewBox;
    # actual pixel dimensions live in the root style attribute.
    if not root.get("viewBox"):
        style_attr = root.get("style", "")
        m_w = re.search(r"width:\s*([\d.]+)px", style_attr)
        m_h = re.search(r"height:\s*([\d.]+)px", style_attr)
        if m_w and m_h:
            sw, sh = m_w.group(1), m_h.group(1)
            root.set("viewBox", f"0 0 {sw} {sh}")
            root.set("width", sw)
            root.set("height", sh)

    # ── Inline CSS class rules as SVG presentation attributes ──
    # Qt's QSvgRenderer ignores <style> blocks, so elements styled
    # only via CSS classes (e.g. .edge, .node-bkg) are invisible.
    _inline_css_classes(root, _SVG_NS)

    # Build parent map (child → parent) for tree surgery
    parent_map = {c: p for p in root.iter() for c in p}

    # ── Remove XHTML <style> elements (e.g. @import Font Awesome) ──
    for style_el in list(root.iter(f"{{{_XHTML_NS}}}style")):
        parent = parent_map.get(style_el)
        if parent is not None:
            parent.remove(style_el)

    # ── Replace each <foreignObject> with a native <text> ──
    for fo in list(root.iter(f"{{{_SVG_NS}}}foreignObject")):
        parent = parent_map.get(fo)
        if parent is None:
            continue

        # Extract human-readable text from XHTML content
        text_content = _extract_fo_text(fo)

        # Get foreignObject dimensions for centring (handle "100%" etc.)
        fo_w_str = fo.get("width", "0") or "0"
        fo_h_str = fo.get("height", "0") or "0"
        fo_w = 0.0 if fo_w_str.endswith("%") else float(fo_w_str)
        fo_h = 0.0 if fo_h_str.endswith("%") else float(fo_h_str)

        # Remember position, remove the foreignObject
        idx = list(parent).index(fo)
        parent.remove(fo)

        # Skip if no text or zero-size (empty label placeholder)
        if not text_content or fo_w < 1 or fo_h < 1:
            continue

        # Determine font size from context
        font_size = _guess_font_size(parent)

        # Create centred <text> replacement
        text_el = ET.Element(f"{{{_SVG_NS}}}text")
        text_el.set("x", str(round(fo_w / 2, 2)))
        text_el.set("y", str(round(fo_h / 2, 2)))
        text_el.set("text-anchor", "middle")
        text_el.set("dominant-baseline", "central")
        text_el.set("font-family", "trebuchet ms, verdana, arial, sans-serif")
        text_el.set("font-size", str(font_size))
        text_el.set("fill", "#333")
        text_el.text = text_content

        parent.insert(idx, text_el)

    # Write the fixed SVG to a temp file
    tmp_dir = tempfile.mkdtemp(prefix="pictosync_svgfix_")
    fixed_path = str(Path(tmp_dir) / "fixed.svg")
    tree.write(fixed_path, xml_declaration=True, encoding="utf-8")
    return fixed_path


def _extract_fo_text(fo: ET.Element) -> str:
    """Extract readable text from a ``<foreignObject>``'s XHTML children.

    Skips the ``.text`` of Font Awesome icon elements (``<i class="fa ...">``),
    but still collects their ``.tail`` (the text after ``</i>``).
    """
    texts: List[str] = []
    for el in fo.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        # Skip .text of icon elements, but still collect .tail
        is_icon = tag == "i" and "fa" in el.get("class", "")
        if not is_icon and el.text and el.text.strip():
            texts.append(el.text.strip())
        if el.tail and el.tail.strip():
            texts.append(el.tail.strip())
    return " ".join(texts)


def _guess_font_size(label_g: ET.Element) -> int:
    """Guess an appropriate font size based on the label context.

    Edge labels use a slightly smaller font than node labels.
    """
    cls = label_g.get("class", "")
    # Walk up: if any ancestor has class "edgeLabel" → smaller text
    if "edgeLabel" in cls:
        return 12
    # Check the data-id pattern for edge labels (L_..._...)
    data_id = label_g.get("data-id", "")
    if data_id.startswith("L_"):
        return 12
    return 14
