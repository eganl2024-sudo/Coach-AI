"""
Central validation and migration helpers for Coach AI domain models.

These helpers normalize raw CSV/JSON rows into typed models and surface
clear ValueError messages so bad data is quarantined early.
"""
from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import pandas as pd

from models import (
    Drill,
    PracticeBlock,
    PracticeSession,
    PracticeConfig,
    SessionDrill,
    TeamProfile,
    SCHEMA_VERSION_CURRENT,
)


def _strip(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    return str(value).strip()


def _coerce_int(value: Any, field: str, allow_none: bool = True) -> Optional[int]:
    if value is None:
        return None if allow_none else 0
    try:
        if isinstance(value, str) and value.strip() == "":
            return None if allow_none else 0
        return int(float(value))
    except Exception:
        raise ValueError(f"Invalid integer for {field}: {value!r}")


def _coerce_float(value: Any, field: str, allow_none: bool = True) -> Optional[float]:
    if value is None:
        return None if allow_none else 0.0
    try:
        if isinstance(value, str) and value.strip() == "":
            return None if allow_none else 0.0
        return float(value)
    except Exception:
        raise ValueError(f"Invalid number for {field}: {value!r}")


def _parse_tags(raw: Any) -> Optional[List[str]]:
    if raw is None:
        return None
    text = str(raw)
    if not text.strip():
        return []
    delimiter = "|" if "|" in text else ","
    return [t.strip() for t in text.split(delimiter) if t.strip()]


def migrate_practice_session_raw(data: dict) -> dict:
    """
    Upgrade a raw practice session dict to the latest schema shape.
    """
    migrated = dict(data or {})
    migrated.setdefault("schema_version", SCHEMA_VERSION_CURRENT)
    migrated.setdefault("club_id", None)

    # Normalize date fields to ISO strings
    for key in ("session_date", "date"):
        if key in migrated and migrated.get(key):
            try:
                dt_val = pd.to_datetime(migrated[key])
                migrated["session_date"] = dt_val.date().isoformat()
            except Exception:
                migrated["session_date"] = str(migrated.get(key))
            break

    # Normalize timestamps
    for stamp in ("created_at", "updated_at"):
        if stamp in migrated and migrated.get(stamp):
            try:
                migrated[stamp] = pd.to_datetime(migrated[stamp]).isoformat()
            except Exception:
                migrated[stamp] = str(migrated[stamp])

    return migrated


def migrate_team_profile_raw(data: dict) -> dict:
    """
    Upgrade a raw team profile dict to the latest schema shape.
    """
    migrated = dict(data or {})
    migrated.setdefault("schema_version", SCHEMA_VERSION_CURRENT)
    migrated.setdefault("club_id", None)
    if "age_group" in migrated and migrated.get("age_group") is not None:
        migrated["age_group"] = str(migrated["age_group"]).strip()
    return migrated


def validate_drill(data: dict) -> Drill:
    """
    Convert a raw drill row to a Drill instance with type coercion and trimming.
    """
    if not isinstance(data, dict):
        raise ValueError("Drill data must be a dict")
    drill_id = _strip(data.get("drill_id") or data.get("id") or data.get("drillID"))
    if not drill_id:
        raise ValueError("Missing drill_id")
    name = _strip(data.get("drill_name") or data.get("name"))
    if not name:
        raise ValueError(f"Drill {drill_id}: missing name")

    category = _strip(data.get("category")) or ""
    age_group_min = _coerce_int(data.get("age_group_min"), "age_group_min") if "age_group_min" in data else None
    age_group_max = _coerce_int(data.get("age_group_max"), "age_group_max") if "age_group_max" in data else None
    min_players = _coerce_int(data.get("players_min") or data.get("min_players"), "players_min")
    max_players = _coerce_int(data.get("players_max") or data.get("max_players"), "players_max")
    duration_minutes = _coerce_int(data.get("duration_minutes"), "duration_minutes")
    intensity = _strip(data.get("intensity"))
    tags = _parse_tags(data.get("tags"))

    position_relevance = _parse_tags(data.get("position_relevance"))
    skill_category = _strip(data.get("skill_category")) or "Technical"
    solo_possible = bool(data.get("solo_possible") if data.get("solo_possible") is not None else True)
    if isinstance(data.get("solo_possible"), str):
        solo_possible = data.get("solo_possible").strip().lower() in {"1", "true", "yes", "y"}
    min_equipment = _strip(data.get("min_equipment")) or "Ball only"
    game_application = _strip(data.get("game_application")) or "Game application notes coming soon"
    video_url = _strip(data.get("video_url") or data.get("video_youtube_url") or "")
    video_thumbnail = _strip(data.get("video_thumbnail") or "")
    coaching_cues = _parse_tags(data.get("coaching_cues") or data.get("coach_cues"))

    # Content architecture
    position_track   = _strip(data.get("position_track"))    or ""
    drill_type       = _strip(data.get("drill_type"))         or "Isolation"
    series_name      = _strip(data.get("series_name"))        or ""
    series_order     = _coerce_int(data.get("series_order"), "series_order") or 0
    rrs_benchmark    = _strip(data.get("rrs_benchmark"))      or "Club Level"
    space_required   = _strip(data.get("space_required"))     or "Small area"
    position_primary = _strip(data.get("position_primary"))   or ""
    presenter_id     = _strip(data.get("presenter_id"))       or ""

    # Rich content
    college_context    = _strip(data.get("college_context"))    or ""
    pro_context        = _strip(data.get("pro_context"))         or ""
    variations         = _strip(data.get("variations"))          or ""
    prerequisite_drill = _strip(data.get("prerequisite_drill")) or ""
    next_drill         = _strip(data.get("next_drill"))          or ""

    # Production workflow
    status          = _strip(data.get("status"))           or "Published"
    video_url_short = _strip(data.get("video_url_short"))  or ""
    video_url_full  = _strip(data.get("video_url_full"))   or ""
    video_status    = _strip(data.get("video_status"))     or "Not Filmed"
    filming_date    = _strip(data.get("filming_date"))     or ""
    filming_notes   = _strip(data.get("filming_notes"))    or ""
    date_published  = _strip(data.get("date_published"))   or ""
    slug            = _strip(data.get("slug"))             or ""
    common_mistakes = _strip(data.get("common_mistakes"))  or ""

    beta_ready = bool(data.get("beta_ready", False))
    if isinstance(data.get("beta_ready"), str):
        beta_ready = data["beta_ready"].strip().lower() in {"1","true","yes","y"}

    known_keys = {
        "drill_id",
        "drill_name",
        "name",
        "category",
        "players_min",
        "players_max",
        "min_players",
        "max_players",
        "duration_minutes",
        "age_group_min",
        "age_group_max",
        "intensity",
        "tags",
        "description",
        "field_type",
        "equipment",
        "setup_data",
        "coaching_points",
        "difficulty",
        "is_favorite",
        "position_relevance",
        "skill_category",
        "solo_possible",
        "min_equipment",
        "game_application",
        "video_url",
        "video_youtube_url",
        "video_thumbnail",
        "coaching_cues",
        "coach_cues",
        "position_track",
        "drill_type",
        "series_name",
        "series_order",
        "rrs_benchmark",
        "space_required",
        "position_primary",
        "presenter_id",
        "college_context",
        "pro_context",
        "variations",
        "prerequisite_drill",
        "next_drill",
        "status",
        "video_url_short",
        "video_url_full",
        "video_status",
        "filming_date",
        "filming_notes",
        "beta_ready",
        "date_published",
        "slug",
        "common_mistakes",
    }
    extra_data = {k: v for k, v in data.items() if k not in known_keys}

    return Drill(
        drill_id=drill_id,
        name=name,
        category=category,
        age_group_min=age_group_min,
        age_group_max=age_group_max,
        min_players=min_players,
        max_players=max_players,
        duration_minutes=duration_minutes,
        intensity=intensity,
        tags=tags,
        description=_strip(data.get("description")) or "",
        field_type=_strip(data.get("field_type")) or "",
        equipment=_strip(data.get("equipment")) or "",
        setup_data=_strip(data.get("setup_data")) or "",
        coaching_points=_strip(data.get("coaching_points")) or "",
        difficulty=_strip(data.get("difficulty")),
        is_favorite=bool(data.get("is_favorite", False)),
        position_relevance=position_relevance,
        skill_category=skill_category,
        solo_possible=solo_possible,
        min_equipment=min_equipment,
        game_application=game_application,
        video_url=video_url,
        video_thumbnail=video_thumbnail,
        coaching_cues=coaching_cues,
        position_track=position_track,
        drill_type=drill_type,
        series_name=series_name,
        series_order=series_order,
        rrs_benchmark=rrs_benchmark,
        space_required=space_required,
        position_primary=position_primary,
        presenter_id=presenter_id,
        college_context=college_context,
        pro_context=pro_context,
        variations=variations,
        prerequisite_drill=prerequisite_drill,
        next_drill=next_drill,
        status=status,
        video_url_short=video_url_short,
        video_url_full=video_url_full,
        video_status=video_status,
        filming_date=filming_date,
        filming_notes=filming_notes,
        beta_ready=beta_ready,
        date_published=date_published,
        slug=slug,
        common_mistakes=common_mistakes,
        extra_data=extra_data,
    )


def validate_team_profile(data: dict) -> TeamProfile:
    """
    Validate a team profile row. Required: team_id, team_name, age_group.
    """
    migrated = migrate_team_profile_raw(data)
    team_id = _strip(migrated.get("team_id"))
    if not team_id:
        raise ValueError("Team profile missing team_id")
    team_name = _strip(migrated.get("team_name"))
    if not team_name:
        raise ValueError(f"Team {team_id}: missing team_name")
    age_group = _strip(migrated.get("age_group"))
    if not age_group:
        raise ValueError(f"Team {team_id}: missing age_group")

    roster_size = _coerce_int(migrated.get("typical_roster_size"), "typical_roster_size")

    known_keys = {
        "schema_version",
        "club_id",
        "team_id",
        "team_name",
        "age_group",
        "gender",
        "level",
        "sessions_per_week",
        "default_practice_duration_minutes",
        "preferred_formation",
        "style_of_play",
        "season_objective",
        "skill_level",
        "typical_roster_size",
        "notes",
        "focus_areas",
    }
    extra_data = {k: v for k, v in migrated.items() if k not in known_keys}

    return TeamProfile(
        schema_version=int(migrated.get("schema_version", SCHEMA_VERSION_CURRENT) or SCHEMA_VERSION_CURRENT),
        club_id=migrated.get("club_id"),
        team_id=team_id,
        team_name=team_name,
        age_group=age_group,
        gender=_strip(migrated.get("gender")),
        level=_strip(migrated.get("level") or migrated.get("skill_level")),
        sessions_per_week=_coerce_int(migrated.get("sessions_per_week"), "sessions_per_week"),
        default_practice_duration_minutes=_coerce_int(
            migrated.get("default_practice_duration_minutes"),
            "default_practice_duration_minutes",
        ),
        preferred_formation=_strip(migrated.get("preferred_formation") or migrated.get("formation")),
        style_of_play=_strip(migrated.get("style_of_play") or migrated.get("play_style")),
        season_objective=_strip(migrated.get("season_objective") or migrated.get("season_objectives")),
        skill_level=_strip(migrated.get("skill_level")),
        typical_roster_size=roster_size,
        notes=_strip(migrated.get("notes")) or "",
        focus_areas=_strip(migrated.get("focus_areas")),
        extra_data=extra_data,
    )


def validate_practice_block(data: dict) -> PracticeBlock:
    """
    Validate a single practice block dict.
    """
    if not isinstance(data, dict):
        raise ValueError("Practice block must be a dict")
    block_type = _strip(data.get("block_type")) or "technical"
    duration_minutes = _coerce_int(data.get("duration_minutes"), "duration_minutes", allow_none=False)
    drill_id = _strip(data.get("drill_id")) or ""
    block_id = _strip(data.get("block_id")) or str(uuid.uuid4())
    order_index = _coerce_int(data.get("order_index"), "order_index", allow_none=False) or 0
    return PracticeBlock(
        block_id=block_id,
        block_type=block_type,
        order_index=order_index,
        duration_minutes=duration_minutes,
        drill_id=drill_id,
        notes=_strip(data.get("notes")),
        auto_inserted=bool(data.get("auto_inserted", False)),
    )


def validate_practice_session(data: dict) -> PracticeSession:
    """
    Validate a full practice session structure, migrate legacy payloads,
    and return a PracticeSession object.
    """
    migrated = migrate_practice_session_raw(data)
    team_id = _strip(migrated.get("team_id"))
    if not team_id:
        raise ValueError("Practice session missing team_id")
    team_name = _strip(migrated.get("team_name")) or ""
    session_date = _strip(migrated.get("session_date") or migrated.get("date")) or ""
    duration_minutes = _coerce_int(migrated.get("duration_minutes"), "duration_minutes", allow_none=False) or 0
    num_players = _coerce_int(migrated.get("num_players"), "num_players") or 0

    blocks_raw = migrated.get("blocks", []) or []
    blocks = []
    for idx, blk in enumerate(blocks_raw):
        try:
            block_obj = validate_practice_block(blk)
        except ValueError as exc:
            raise ValueError(f"Practice session block {idx}: {exc}") from exc
        blocks.append(block_obj)

    drills_raw = migrated.get("drills", []) or []
    drills = [SessionDrill.from_dict(d) for d in drills_raw]
    config_raw = migrated.get("config") or {}
    config = PracticeConfig(
        duration_minutes=int(config_raw.get("duration_minutes", duration_minutes)),
        num_players=int(config_raw.get("num_players", num_players)),
        num_drills=int(config_raw.get("num_drills", migrated.get("num_drills", len(drills)) or len(drills))),
        selected_categories=config_raw.get("selected_categories", migrated.get("selected_categories", [])) or [],
        session_date=config_raw.get("session_date", session_date),
        session_notes=config_raw.get("session_notes", migrated.get("session_notes", "")),
        focus_tags=config_raw.get("focus_tags", []),
        favorites_only=bool(config_raw.get("favorites_only", False)),
        use_team_profile=bool(config_raw.get("use_team_profile", True)),
        template_blocks=config_raw.get("template_blocks"),
        focus_boost_categories=config_raw.get("focus_boost_categories", []),
    )

    schema_version = int(migrated.get("schema_version", SCHEMA_VERSION_CURRENT) or SCHEMA_VERSION_CURRENT)
    session_id = _strip(migrated.get("session_id")) or str(uuid.uuid4())

    created_at_val = migrated.get("created_at")
    updated_at_val = migrated.get("updated_at")
    try:
        created_at = pd.to_datetime(created_at_val) if created_at_val else None
    except Exception:
        created_at = None
    try:
        updated_at = pd.to_datetime(updated_at_val) if updated_at_val else None
    except Exception:
        updated_at = None

    return PracticeSession(
        session_id=session_id,
        team_id=team_id,
        team_name=team_name,
        session_date=session_date,
        config=config,
        duration_minutes=duration_minutes,
        num_players=num_players,
        num_drills=int(migrated.get("num_drills", config.num_drills)),
        selected_categories=migrated.get("selected_categories", config.selected_categories),
        drills=drills,
        team_profile_summary=migrated.get("team_profile_summary", {}),
        equipment_needed=migrated.get("equipment_needed", []),
        category_summary=migrated.get("category_summary", {}),
        intensity_summary=migrated.get("intensity_summary", {}),
        manual_adjustments=migrated.get("manual_adjustments", {"reordered": 0, "replaced": 0}),
        block_duration_summaries=migrated.get("block_duration_summaries", []),
        template_notes=migrated.get("template_notes", []),
        warnings=migrated.get("warnings", []),
        schema_version=schema_version,
        club_id=migrated.get("club_id"),
        blocks=blocks,
        created_at=created_at,
        updated_at=updated_at,
        source=_strip(migrated.get("source")),
        primary_focus=_strip(migrated.get("primary_focus")),
        num_players_expected=_coerce_int(migrated.get("num_players_expected"), "num_players_expected"),
        formation=_strip(migrated.get("formation")),
    )
