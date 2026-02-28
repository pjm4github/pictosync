"""
domains/__init__.py

Domain registry for plug-in tool folders.

Each domain lives in a subfolder of ``domains/`` and contains a
``tools.json`` file that lists the DSL tool definitions for that domain.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DomainTool:
    """A single DSL tool definition within a domain.

    Attributes:
        name: Internal tool name (e.g. "node").
        label: Display label (e.g. "Node").
        tooltip: Tooltip text for the toolbar button.
        icon: Icon name used by generate_icons (e.g. "dsl_node").
        base_kind: The annotation kind this tool creates (e.g. "roundedrect").
        defaults: Default values for geom, meta, and style dicts.
    """

    name: str
    label: str
    tooltip: str
    icon: str
    base_kind: str
    defaults: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainInfo:
    """Metadata for a discovered domain plug-in folder.

    Attributes:
        name: Folder name (e.g. "ns3").
        display_name: Human-readable name (e.g. "NS3").
        tools: List of tool definitions loaded from tools.json.
    """

    name: str
    display_name: str
    tools: List[DomainTool] = field(default_factory=list)


def scan_domains() -> List[DomainInfo]:
    """Scan ``domains/*/tools.json`` and return loaded domain descriptors.

    Returns:
        Sorted list of :class:`DomainInfo` instances (sorted by folder name).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    domains: List[DomainInfo] = []

    for entry in sorted(os.listdir(base_dir)):
        entry_path = os.path.join(base_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        tools_path = os.path.join(entry_path, "tools.json")
        if not os.path.isfile(tools_path):
            continue

        try:
            with open(tools_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(raw, list):
            continue

        tools: List[DomainTool] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            try:
                tools.append(DomainTool(
                    name=str(item["name"]),
                    label=str(item["label"]),
                    tooltip=str(item.get("tooltip", "")),
                    icon=str(item.get("icon", "")),
                    base_kind=str(item["base_kind"]),
                    defaults=item.get("defaults", {}),
                ))
            except (KeyError, TypeError):
                continue

        if tools:
            display_name = entry.upper()
            domains.append(DomainInfo(name=entry, display_name=display_name, tools=tools))

    return domains
