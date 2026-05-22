"""Utilities for block template storage and retrieval."""
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List
from datetime import datetime, UTC

import config
from utils import sanitize_filename

@dataclass
class BlockTemplate:
    name: str
    description: str
    blocks: dict
    block_durations: dict = field(default_factory=dict)
    repair_notes: list = field(default_factory=list)


def _template_path(data_path=None):
    base_path = Path(data_path) if data_path else config.get_data_path()
    template_dir = base_path / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    return template_dir / "block_templates.json"


def _backup_dir(data_path=None):
    base_path = Path(data_path) if data_path else config.get_data_path()
    backup_dir = base_path / "templates" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def _resolve_template_path(data_path=None):
    """
    Call _template_path, tolerating monkeypatched versions that take no args.
    """
    try:
        return _template_path(data_path)
    except TypeError:
        return _template_path()


def _resolve_backup_dir(data_path=None):
    """
    Call _backup_dir, tolerating monkeypatched versions that take no args.
    """
    try:
        return _backup_dir(data_path)
    except TypeError:
        return _backup_dir()


def save_template_backup(template: BlockTemplate, data_path=None):
    """
    Save a per-template backup under backups/{template_id}/{timestamp}.json.
    """
    safe_name = sanitize_filename(template.name)
    backup_root = _backup_dir(data_path) / safe_name
    backup_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    backup_path = backup_root / f"{safe_name}_{timestamp}.json"
    record = asdict(template)
    record.setdefault("block_durations", template.block_durations or {})
    with backup_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return backup_path


def load_block_templates(data_path=None) -> List[BlockTemplate]:
    path = _resolve_template_path(data_path)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    templates = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        blocks = entry.get("blocks", {}) or {}
        durations = entry.get("block_durations", {}) or {}
        # Normalize durations: ensure every block has a non-negative int duration
        normalized_durations = {}
        repair_notes = []
        for block, ids in blocks.items():
            try:
                normalized_durations[block] = max(0, int(durations.get(block, 0)))
            except Exception:
                normalized_durations[block] = 0
                repair_notes.append(f"Duration for {block} was invalid; set to 0.")
        # Enforce warmup first / cooldown last ordering in repair notes only
        block_order = list(blocks.keys())
        if block_order:
            if "warmup" in block_order and block_order[0] != "warmup":
                repair_notes.append("Warmup was not first; please reorder.")
            if "cooldown" in block_order and block_order[-1] != "cooldown":
                repair_notes.append("Cooldown was not last; please reorder.")
        templates.append(
            BlockTemplate(
                name=entry.get("name", "Untitled"),
                description=entry.get("description", ""),
                blocks=blocks,
                block_durations=normalized_durations,
                repair_notes=repair_notes,
            )
        )
    return templates


def save_block_templates(templates: List[BlockTemplate], data_path=None) -> None:
    """
    Persist templates and keep a backup of the previous file.
    """
    path = _resolve_template_path(data_path)
    backup_dir = _resolve_backup_dir(data_path)
    if path.exists():
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
            backup_path = backup_dir / f"block_templates_{timestamp}.json"
            backup_path.write_bytes(path.read_bytes())
        except Exception:
            pass
    payload = []
    for tpl in templates:
        record = asdict(tpl)
        record.setdefault("block_durations", tpl.block_durations or {})
        payload.append(record)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def validate_templates(templates_list, drills_df) -> dict:
    """
    Validate templates against drill library and durations.

    Returns mapping: template_name -> {"missing_drill_ids": [...], "bad_durations": [...], "total_out_of_range": bool}
    """
    issues = {}
    library_ids = set(drills_df.get("drill_id", [])) if drills_df is not None else set()
    for tpl in templates_list or []:
        missing = []
        bad_durations = []
        total_out_of_range = False
        for block, ids in (tpl.blocks or {}).items():
            for drill_id in ids or []:
                if library_ids and drill_id not in library_ids:
                    missing.append(drill_id)
            duration = tpl.block_durations.get(block, 0) if isinstance(tpl.block_durations, dict) else 0
            try:
                if int(duration) <= 0:
                    bad_durations.append(block)
            except Exception:
                bad_durations.append(block)
        try:
            total = sum(int(tpl.block_durations.get(b, 0) or 0) for b in tpl.blocks.keys())
            if total and (total < 20 or total > 200):
                total_out_of_range = True
        except Exception:
            total_out_of_range = True
        issues[tpl.name] = {
            "missing_drill_ids": sorted(set(missing)),
            "bad_durations": sorted(set(bad_durations)),
            "total_out_of_range": total_out_of_range,
        }
    return issues
