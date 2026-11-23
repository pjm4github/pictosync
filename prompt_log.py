"""
prompt_log.py

A small persistent log of extraction prompts (the free-text instructions the
user adds alongside an image) so they can be recalled, refined and reused as
different models are tried against the same or modified prompt.

Stored as a JSON array in the user settings directory
(``extraction_prompts.json``), newest first. Each entry records enough context
to reproduce and compare a run:

    {
      "ts": "2026-11-22T14:05:31",
      "provider": "gemini",
      "model": "gemini-2.5-flash-image",
      "image": "C:/.../lodge.png",
      "context": "Ignore the colors; detect rotated rectangles as rect.",
      "full_prompt": "<base extraction prompt + user instructions>",
      "status": "ok" | "failed",
      "annotations": 12,
      "tokens": 3456,
      "error": ""          # short error summary when status == "failed"
    }
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

_FILENAME = "extraction_prompts.json"
_MAX_ENTRIES = 500


class PromptLog:
    """Read/append access to the on-disk extraction-prompt history."""

    def __init__(self, directory: Path):
        """
        Args:
            directory: Directory to store the log file in (created on write).
        """
        self.path = Path(directory) / _FILENAME

    def load(self) -> List[Dict[str, Any]]:
        """Return all entries, newest first. Missing/corrupt file → ``[]``."""
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                return [e for e in data if isinstance(e, dict)]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return []

    def add(self, *, provider: str, model: str, image: str, context: str,
            status: str, annotations: int = 0, tokens: int = 0,
            error: str = "", full_prompt: str = "") -> Dict[str, Any]:
        """Append one entry and persist. Returns the stored entry.

        Entries with empty context are still logged (they document that a bare
        run was tried), but callers may choose to skip those.

        Args:
            full_prompt: The complete prompt actually sent to the model (base
                prompt plus any user instructions). Stored verbatim.
        """
        entry = {
            "id": uuid.uuid4().hex,
            "ts": datetime.now().isoformat(timespec="seconds"),
            "provider": provider,
            "model": model,
            "image": image,
            "context": context,
            "full_prompt": full_prompt or "",
            "status": status,
            "annotations": int(annotations),
            "tokens": int(tokens),
            "error": (error or "")[:300],
        }
        entries = self.load()
        entries.insert(0, entry)
        del entries[_MAX_ENTRIES:]
        self._write(entries)
        return entry

    def delete(self, ids: List[str]) -> None:
        """Remove entries whose ``id`` is in *ids*."""
        drop = set(ids)
        keep = [e for e in self.load() if e.get("id") not in drop]
        self._write(keep)

    def clear(self) -> None:
        """Remove all entries."""
        self._write([])

    def _write(self, entries: List[Dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(entries, fh, indent=2)
        tmp.replace(self.path)


def default_log(settings_manager) -> Optional[PromptLog]:
    """Build a :class:`PromptLog` in the app's user settings directory.

    Args:
        settings_manager: The app SettingsManager (for ``user_settings_dir``).

    Returns:
        A :class:`PromptLog`, or ``None`` if a directory can't be resolved.
    """
    directory = getattr(settings_manager, "user_settings_dir", None)
    if directory is None:
        return None
    return PromptLog(Path(directory))
