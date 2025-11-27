"""Utilities for managing filter preset files with versioning."""
import json
from pathlib import Path

PRESETS_VERSION = 1


def load_presets(path: Path | None):
    """
    Load filter presets from disk with error handling.

    Returns:
        dict with keys: presets (list), warning (str|None)
    """
    if path is None:
        return {"presets": [], "warning": "Preset path not available."}
    if not path.exists():
        return {"presets": [], "warning": None}
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
    except Exception:
        return {"presets": [], "warning": "Filter presets were corrupted and reset."}

    version = data.get("version")
    presets = data.get("presets", [])
    if version != PRESETS_VERSION:
        return {"presets": [], "warning": "Filter presets were from an older version and have been reset."}
    if not isinstance(presets, list):
        return {"presets": [], "warning": "Filter presets were invalid and reset."}
    return {"presets": presets, "warning": None}


def save_presets(path: Path | None, presets):
    """Persist filter presets in versioned format."""
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": PRESETS_VERSION, "presets": presets}
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2)
