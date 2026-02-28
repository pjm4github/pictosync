"""
editor/schema_checker.py

Pure-function module for comparing annotations against the expected schema.
Derives the expected field set directly from ``annotation_schema.json`` —
no hand-maintained Python defaults.

Finds missing fields (in schema but not annotation) and extra fields
(in annotation but not schema), and locates their character ranges in
formatted JSON text.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

from schemas import (
    get_annotation_schema,
    build_expected_from_schema,
    _resolve_ref,
    _zero_for_type,
    _extract_defaults,
    _parse_kind_overrides,
)


# Preferred key ordering for merged annotations
KEY_ORDER = ["id", "kind", "geom", "meta", "style", "z"]


# -------------------------------------------------------------------------
# Field diff
# -------------------------------------------------------------------------

@dataclass
class FieldDiff:
    """Result of comparing an annotation dict against the expected schema."""

    missing_paths: Set[str] = field(default_factory=set)
    """Dot-paths present in schema but absent in the annotation."""

    extra_paths: Set[str] = field(default_factory=set)
    """Dot-paths present in annotation but absent in the schema."""


def compute_field_diff(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    prefix: str = "",
) -> FieldDiff:
    """Recursively compare *actual* vs *expected* annotation dicts.

    - Keys in expected but not actual -> missing
    - Keys in actual but not expected -> extra
    - Both present and both dicts -> recurse with dot-path prefix
    - ``id`` and ``kind`` are skipped at top level.
    """
    diff = FieldDiff()
    skip = {"id", "kind"} if not prefix else set()

    for key in expected:
        if key in skip:
            continue
        path = f"{prefix}.{key}" if prefix else key
        if key not in actual:
            diff.missing_paths.add(path)
        elif isinstance(expected[key], dict) and isinstance(actual[key], dict):
            sub = compute_field_diff(actual[key], expected[key], path)
            diff.missing_paths |= sub.missing_paths
            diff.extra_paths |= sub.extra_paths

    for key in actual:
        if key in skip:
            continue
        path = f"{prefix}.{key}" if prefix else key
        if key not in expected:
            diff.extra_paths.add(path)

    return diff


# -------------------------------------------------------------------------
# Merge
# -------------------------------------------------------------------------

def _ordered_merge(actual: Dict, expected: Dict) -> OrderedDict:
    """Deep-merge *actual* into *expected*, preserving KEY_ORDER at top level."""
    merged = OrderedDict()

    all_keys: list[str] = []
    for k in KEY_ORDER:
        if k in expected or k in actual:
            all_keys.append(k)
    for k in expected:
        if k not in all_keys:
            all_keys.append(k)
    for k in actual:
        if k not in all_keys:
            all_keys.append(k)

    for key in all_keys:
        if key in actual and key in expected:
            if isinstance(actual[key], dict) and isinstance(expected[key], dict):
                merged[key] = _ordered_merge(actual[key], expected[key])
            else:
                merged[key] = actual[key]
        elif key in actual:
            merged[key] = actual[key]
        else:
            merged[key] = expected[key]

    return merged


def build_merged_annotation(
    annotation: Dict[str, Any],
    kind: str,
) -> Tuple[Dict[str, Any], FieldDiff]:
    """Build a complete annotation with all schema fields filled in.

    Derives the expected template from ``annotation_schema.json`` via
    :func:`build_expected_from_schema`, then deep-merges the actual
    annotation on top.

    Args:
        annotation: The annotation dict from the editor.
        kind: The annotation kind (rect, line, etc.).

    Returns:
        ``(merged_dict, diff)`` — *merged_dict* has all fields from both
        actual and expected; *diff* records which paths are missing/extra.
    """
    expected = build_expected_from_schema(kind)

    # Carry over id from actual if present
    if "id" in annotation:
        expected["id"] = annotation["id"]

    # Dynamically populate optional schema objects that are present in
    # the actual annotation so their sub-fields get validated rather than
    # flagged as "extra".  These are stripped from the default template
    # by build_expected_from_schema to avoid gray noise on non-DSL items.
    actual_meta = annotation.get("meta", {})
    if "dsl" in actual_meta and isinstance(actual_meta["dsl"], dict):
        schema = get_annotation_schema()
        defs = schema.get("$defs", {})
        dsl_def = defs.get("dslMetadata", {})
        if dsl_def:
            expected.setdefault("meta", {})["dsl"] = _extract_defaults(
                dsl_def, defs,
            )

    diff = compute_field_diff(annotation, expected)
    merged = _ordered_merge(annotation, expected)

    return dict(merged), diff


# -------------------------------------------------------------------------
# Character-range finder
# -------------------------------------------------------------------------

def find_key_ranges_in_json(
    text: str,
    obj_start: int,
    obj_end: int,
    target_paths: Set[str],
) -> List[Tuple[int, int]]:
    """Find character ranges of key-value pairs matching dot-paths.

    Scans the JSON text between *obj_start* and *obj_end* line-by-line.
    For each line that begins a key matching one of the *target_paths*,
    returns the ``(start, end)`` character range covering the full key-value
    pair (including the trailing comma if present).

    The text is assumed to be ``json.dumps(..., indent=2)`` formatted.

    Args:
        text: The full editor text.
        obj_start: Character offset of the annotation's opening ``{``.
        obj_end: Character offset of the annotation's closing ``}``.
        target_paths: Set of dot-paths to find.

    Returns:
        List of ``(start_char, end_char)`` ranges (inclusive start, exclusive end).
    """
    if not target_paths:
        return []

    region = text[obj_start:obj_end + 1]
    ranges: List[Tuple[int, int]] = []

    key_re = re.compile(r'^(\s*)"([^"]+)"\s*:')

    lines = region.split("\n")
    depth = 0
    depth_stack: List[str] = []
    line_offset = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        abs_offset = obj_start + line_offset

        m = key_re.match(line)
        if m:
            key_name = m.group(2)

            while len(depth_stack) >= depth:
                if depth_stack:
                    depth_stack.pop()
                else:
                    break

            current_path = ".".join(depth_stack + [key_name]) if depth_stack else key_name

            if current_path in target_paths:
                range_start = abs_offset
                after_colon = line[m.end():]
                rest = after_colon.strip()

                if rest.startswith("{") or rest.startswith("["):
                    open_char = rest[0]
                    close_char = "}" if open_char == "{" else "]"
                    brace_count = 0
                    j = i
                    scan_offset = line_offset
                    found_end = False
                    while j < len(lines):
                        for ch in lines[j]:
                            if ch == open_char:
                                brace_count += 1
                            elif ch == close_char:
                                brace_count -= 1
                                if brace_count == 0:
                                    found_end = True
                                    break
                        scan_offset += len(lines[j]) + 1
                        if found_end:
                            range_end = obj_start + scan_offset - 1
                            ranges.append((range_start, range_end))
                            break
                        j += 1
                    if not found_end:
                        range_end = abs_offset + len(line)
                        ranges.append((range_start, range_end))
                else:
                    range_end = abs_offset + len(line)
                    ranges.append((range_start, range_end))

        in_string = False
        for ch in line:
            if ch == '"':
                in_string = not in_string
            elif not in_string:
                if ch in "{[":
                    depth += 1
                    if m and ch in "{[":
                        key_name_for_stack = m.group(2)
                        while len(depth_stack) >= depth:
                            if depth_stack:
                                depth_stack.pop()
                            else:
                                break
                        depth_stack.append(key_name_for_stack)
                        m = None
                elif ch in "}]":
                    depth -= 1
                    while len(depth_stack) > depth:
                        depth_stack.pop()

        line_offset += len(line) + 1
        i += 1

    return ranges
