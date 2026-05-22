import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pandas as pd

SCHEMA_VERSION_CURRENT = 1

MIN_DURATION = 45
MAX_DURATION = 120
MIN_DRILLS = 3
MAX_DRILLS = 8
MIN_PLAYERS = 6
MAX_PLAYERS = 30


@dataclass
class Drill:
    """
    Core drill definition loaded from CSV/Excel.

    Mirrors columns like drill_id, drill_name, category, players_min/max, duration_minutes,
    and keeps any extra columns in extra_data for forward compatibility.
    """
    drill_id: str
    name: str
    category: str
    age_group_min: Optional[int] = None
    age_group_max: Optional[int] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    tags: Optional[List[str]] = None
    description: str = ""
    field_type: str = ""
    equipment: str = ""
    setup_data: str = ""
    coaching_points: str = ""
    difficulty: Optional[str] = None
    is_favorite: bool = False
    position_relevance: Optional[List[str]] = None
    skill_category: str = "Technical"
    solo_possible: bool = True
    min_equipment: str = "Ball only"
    game_application: str = "Game application notes coming soon"
    video_url: str = ""
    video_thumbnail: str = ""
    coaching_cues: Optional[List[str]] = None
    position_track: str = ""
    drill_type: str = "Isolation"
    series_name: str = ""
    series_order: int = 0
    rrs_benchmark: str = "Club Level"
    space_required: str = "Small area"
    position_primary: str = ""
    presenter_id: str = ""
    college_context: str = ""
    pro_context: str = ""
    variations: str = ""
    prerequisite_drill: str = ""
    next_drill: str = ""
    status: str = "Published"
    video_url_short: str = ""
    video_url_full: str = ""
    video_status: str = "Not Filmed"
    filming_date: str = ""
    filming_notes: str = ""
    beta_ready: bool = False
    date_published: str = ""
    slug: str = ""
    common_mistakes: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_record(self, preferred_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Return a flat dict suitable for DataFrame construction, preserving extra columns.
        """
        base = {
            "drill_id": self.drill_id,
            "drill_name": self.name,
            "category": self.category,
            "players_min": self.min_players,
            "players_max": self.max_players,
            "duration_minutes": self.duration_minutes,
            "field_type": self.field_type,
            "setup_data": self.setup_data,
            "equipment": self.equipment,
            "coaching_points": self.coaching_points,
            "description": self.description,
            "difficulty": self.difficulty,
            "intensity": self.intensity,
            "is_favorite": self.is_favorite,
            "skill_category": self.skill_category,
            "solo_possible": self.solo_possible,
            "min_equipment": self.min_equipment,
            "game_application": self.game_application,
            "video_url": self.video_url,
            "video_thumbnail": self.video_thumbnail,
            "position_track": self.position_track,
            "drill_type": self.drill_type,
            "series_name": self.series_name,
            "series_order": self.series_order,
            "rrs_benchmark": self.rrs_benchmark,
            "space_required": self.space_required,
            "position_primary": self.position_primary,
            "presenter_id": self.presenter_id,
            "college_context": self.college_context,
            "pro_context": self.pro_context,
            "variations": self.variations,
            "prerequisite_drill": self.prerequisite_drill,
            "next_drill": self.next_drill,
            "status": self.status,
            "video_url_short": self.video_url_short,
            "video_url_full": self.video_url_full,
            "video_status": self.video_status,
            "filming_date": self.filming_date,
            "filming_notes": self.filming_notes,
            "beta_ready": self.beta_ready,
            "date_published": self.date_published,
            "slug": self.slug,
            "common_mistakes": self.common_mistakes,
        }
        if self.tags is not None:
            base["tags"] = "|".join(self.tags)
        if self.position_relevance is not None:
            base["position_relevance"] = "|".join(self.position_relevance)
        if self.coaching_cues is not None:
            base["coaching_cues"] = "|".join(self.coaching_cues)
        if self.age_group_min is not None:
            base["age_group_min"] = self.age_group_min
        if self.age_group_max is not None:
            base["age_group_max"] = self.age_group_max
        # Preserve any extra columns that were present on load
        for key, value in (self.extra_data or {}).items():
            if key not in base:
                base[key] = value
        if preferred_fields:
            for key in preferred_fields:
                base.setdefault(key, None)
        return base


@dataclass
class PracticeBlock:
    """
    A single block inside a practice session (warmup, technical, etc.).
    """
    block_id: str
    block_type: str
    order_index: int
    duration_minutes: int
    drill_id: str
    notes: Optional[str] = None
    auto_inserted: bool = False


@dataclass
class TeamProfile:
    """
    Structured representation of a team profile row from CSV/Excel.
    """
    schema_version: int
    team_id: str
    team_name: str
    age_group: str
    club_id: Optional[str] = None
    gender: Optional[str] = None
    level: Optional[str] = None
    sessions_per_week: Optional[int] = None
    default_practice_duration_minutes: Optional[int] = None
    preferred_formation: Optional[str] = None
    style_of_play: Optional[str] = None
    season_objective: Optional[str] = None
    skill_level: Optional[str] = None
    typical_roster_size: Optional[int] = None
    notes: str = ""
    focus_areas: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_record(self, preferred_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        record = {
            "schema_version": self.schema_version,
            "club_id": self.club_id,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "age_group": self.age_group,
            "skill_level": self.skill_level,
            "typical_roster_size": self.typical_roster_size,
            "notes": self.notes,
            "preferred_formation": self.preferred_formation,
            "play_style": self.style_of_play,
            "season_objectives": self.season_objective,
            "focus_areas": self.focus_areas,
        }
        if preferred_fields:
            for key in preferred_fields:
                record.setdefault(key, None)
        for key, value in (self.extra_data or {}).items():
            if key not in record:
                record[key] = value
        return record


@dataclass
class PracticeConfig:
    duration_minutes: int
    num_players: int
    num_drills: int
    selected_categories: List[str]
    session_date: str
    session_notes: str
    focus_tags: List[str] = field(default_factory=list)
    favorites_only: bool = False
    use_team_profile: bool = True
    template_blocks: Optional[Dict[str, List[str]]] = None
    focus_boost_categories: List[str] = field(default_factory=list)

    def validate(self):
        if not self.selected_categories:
            raise ValueError("At least one category must be selected")
        if not (MIN_DURATION <= self.duration_minutes <= MAX_DURATION):
            raise ValueError("Duration outside allowed range")
        if not (MIN_PLAYERS <= self.num_players <= MAX_PLAYERS):
            raise ValueError("Player count outside allowed range")
        if not (MIN_DRILLS <= self.num_drills <= MAX_DRILLS):
            raise ValueError("Number of drills outside allowed range")
        return self

    def to_dict(self):
        return asdict(self)


@dataclass
class SessionDrill:
    drill_id: str
    drill_name: str
    category: str
    intensity: str
    players_min: int
    players_max: int
    field_type: str
    description: str
    coaching_points: str
    equipment: str
    setup_data: str
    allocated_time: int
    target_intensity: str
    recency_label: str = "New"
    fallback: bool = False
    position_relevance: Optional[List[str]] = None
    skill_category: str = "Technical"
    solo_possible: bool = True
    min_equipment: str = "Ball only"
    game_application: str = "Game application notes coming soon"
    video_url: str = ""
    video_thumbnail: str = ""
    coaching_cues: Optional[List[str]] = None
    extras: Dict[str, Any] = field(default_factory=dict)
    diagram_path: str = ""
    diagram_metadata: Dict[str, Any] = field(default_factory=dict)
    block_type: Optional[str] = None
    block_index: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base_fields = {
            "drill_id": data.get("drill_id", ""),
            "drill_name": data.get("drill_name", ""),
            "category": data.get("category", ""),
            "intensity": data.get("intensity", ""),
            "players_min": int(data.get("players_min", 0) or 0),
            "players_max": int(data.get("players_max", 0) or 0),
            "field_type": data.get("field_type", ""),
            "description": data.get("description", ""),
            "coaching_points": data.get("coaching_points", ""),
            "equipment": data.get("equipment", ""),
            "setup_data": data.get("setup_data", ""),
            "allocated_time": int(data.get("allocated_time", 0) or 0),
            "target_intensity": data.get("target_intensity", ""),
            "recency_label": data.get("recency_label", "New"),
            "fallback": bool(data.get("fallback", False)),
            "position_relevance": data.get("position_relevance") if isinstance(data.get("position_relevance"), list) else ([t.strip() for t in str(data.get("position_relevance", "")).split("|") if t.strip()] if data.get("position_relevance") else []),
            "skill_category": data.get("skill_category", "Technical"),
            "solo_possible": bool(data.get("solo_possible") if data.get("solo_possible") is not None else True),
            "min_equipment": data.get("min_equipment", "Ball only"),
            "game_application": data.get("game_application", "Game application notes coming soon"),
            "video_url": data.get("video_url") or data.get("video_youtube_url") or "",
            "video_thumbnail": data.get("video_thumbnail", ""),
            "coaching_cues": data.get("coaching_cues") if isinstance(data.get("coaching_cues"), list) else ([t.strip() for t in str(data.get("coaching_cues", "")).split("|") if t.strip()] if data.get("coaching_cues") else []),
            "diagram_path": data.get("diagram_path", ""),
            "diagram_metadata": data.get("diagram_metadata") if isinstance(data.get("diagram_metadata"), dict) else {},
            "block_type": data.get("block_type"),
            "block_index": data.get("block_index"),
        }
        extras = {
            key: value
            for key, value in data.items()
            if key not in base_fields
        }
        return cls(**base_fields, extras=extras)

    def to_dict(self):
        payload = asdict(self)
        extras = payload.pop("extras", {}) or {}
        payload.update(extras)
        return payload


@dataclass
class DrillScoreBreakdown:
    drill_id: str
    total_score: float
    recency_penalty: float = 0.0
    focus_match: float = 0.0
    intensity_match: float = 0.0
    player_fit_score: float = 0.0
    category_match: float = 0.0
    block_alignment: float = 0.0
    rating_adjustment: float = 0.0
    other_factors: Dict[str, float] = field(default_factory=dict)


@dataclass
class PracticeSession:
    """
    Rich practice session used throughout the app. The generator relies on drills and config,
    while schema_version/blocks/metadata support migration and validation.
    """
    session_id: str
    team_id: str
    team_name: str
    session_date: str
    config: PracticeConfig
    duration_minutes: int
    num_players: int
    num_drills: int
    selected_categories: List[str]
    drills: List[SessionDrill] = field(default_factory=list)
    team_profile_summary: Dict[str, Any] = field(default_factory=dict)
    equipment_needed: List[str] = field(default_factory=list)
    category_summary: Dict[str, int] = field(default_factory=dict)
    intensity_summary: Dict[str, int] = field(default_factory=dict)
    manual_adjustments: Dict[str, int] = field(default_factory=lambda: {"reordered": 0, "replaced": 0})
    block_duration_summaries: List[Any] = field(default_factory=list)
    template_notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION_CURRENT
    club_id: Optional[str] = None
    blocks: List[PracticeBlock] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source: Optional[str] = None
    primary_focus: Optional[str] = None
    num_players_expected: Optional[int] = None
    formation: Optional[str] = None

    @classmethod
    def create(cls, team_name: str, team_id: str, session_date: str, config: PracticeConfig,
               drills: List[SessionDrill], team_profile_summary=None,
               equipment_needed=None, category_summary=None, intensity_summary=None):
        return cls(
            session_id=str(uuid.uuid4()),
            team_id=team_id,
            team_name=team_name,
            session_date=session_date,
            config=config,
            duration_minutes=config.duration_minutes,
            num_players=config.num_players,
            num_drills=len(drills),
            selected_categories=list(config.selected_categories),
            drills=drills,
            team_profile_summary=team_profile_summary or {},
            equipment_needed=equipment_needed or [],
            category_summary=category_summary or {},
            intensity_summary=intensity_summary or {}
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        cfg = data.get("config", {}) or {}
        drills_data = data.get("drills", []) or []
        drills = [SessionDrill.from_dict(d) for d in drills_data]
        config = PracticeConfig(
            duration_minutes=cfg.get("duration_minutes", data.get("duration_minutes", 0)),
            num_players=cfg.get("num_players", data.get("num_players", 0)),
            num_drills=cfg.get("num_drills", len(drills)),
            selected_categories=cfg.get("selected_categories", data.get("selected_categories", [])),
            session_date=cfg.get("session_date", data.get("session_date", "")),
            session_notes=cfg.get("session_notes", ""),
            focus_tags=cfg.get("focus_tags", []),
            favorites_only=cfg.get("favorites_only", False),
            use_team_profile=cfg.get("use_team_profile", True),
            template_blocks=cfg.get("template_blocks"),
            focus_boost_categories=cfg.get("focus_boost_categories", []),
        )
        session = cls(
            session_id=data.get("session_id", ""),
            team_id=data.get("team_id", ""),
            team_name=data.get("team_name", ""),
            session_date=data.get("session_date", cfg.get("session_date", "")),
            config=config,
            duration_minutes=data.get("duration_minutes", config.duration_minutes),
            num_players=data.get("num_players", config.num_players),
            num_drills=data.get("num_drills", len(drills)),
            selected_categories=data.get("selected_categories", config.selected_categories),
            drills=drills,
            team_profile_summary=data.get("team_profile_summary", {}),
            equipment_needed=data.get("equipment_needed", []),
            category_summary=data.get("category_summary", {}),
            intensity_summary=data.get("intensity_summary", {}),
            manual_adjustments=data.get("manual_adjustments", {"reordered": 0, "replaced": 0}),
            block_duration_summaries=data.get("block_duration_summaries", []),
            template_notes=data.get("template_notes", []),
            warnings=data.get("warnings", []),
            schema_version=int(data.get("schema_version", SCHEMA_VERSION_CURRENT) or SCHEMA_VERSION_CURRENT),
            club_id=data.get("club_id"),
            blocks=[PracticeBlock(**b) if isinstance(b, dict) else b for b in data.get("blocks", []) or []],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            source=data.get("source"),
            primary_focus=data.get("primary_focus"),
            num_players_expected=data.get("num_players_expected"),
            formation=data.get("formation"),
        )
        # Optional extra metadata
        session.event_id = data.get("event_id", "")
        return session

    def compute_avg_intensity(self):
        """
        Compute time-weighted average intensity across drills.

        Supports numeric intensities or string labels ("low"/"medium"/"high").
        Uses allocated_time if available, else duration_minutes; skips drills
        without usable duration or intensity.
        """
        intensity_map = {
            "low": 1.0,
            "medium": 3.0,
            "high": 5.0,
        }
        total_minutes = 0.0
        weighted_sum = 0.0
        for drill in self.drills:
            minutes = getattr(drill, "allocated_time", None) or getattr(drill, "duration_minutes", None)
            try:
                minutes = float(minutes)
            except Exception:
                minutes = 0.0
            if not minutes or pd.isna(minutes):
                continue
            intensity = getattr(drill, "intensity", None)
            intensity_val = None
            # Try numeric first
            try:
                intensity_val = float(intensity)
            except Exception:
                pass
            # Fall back to string label mapping
            if intensity_val is None and isinstance(intensity, str):
                key = intensity.strip().lower()
                intensity_val = intensity_map.get(key)
            if intensity_val is None or pd.isna(intensity_val):
                continue
            total_minutes += minutes
            weighted_sum += minutes * intensity_val
        if total_minutes <= 0:
            return None
        return weighted_sum / total_minutes

    @staticmethod
    def classify_intensity(score: float):
        """
        Map a numeric intensity score to a label.
        Thresholds can be tuned; defaults assume a 1-5 scale.
        """
        if score is None or pd.isna(score):
            return ""
        if score <= 2.3:
            return "Low"
        if score <= 3.7:
            return "Medium"
        return "High"

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "session_date": self.session_date,
            "config": self.config.to_dict(),
            "duration_minutes": self.duration_minutes,
            "num_players": self.num_players,
            "num_drills": self.num_drills,
            "selected_categories": self.selected_categories,
            "drills": [drill.to_dict() for drill in self.drills],
            "team_profile_summary": self.team_profile_summary,
            "equipment_needed": self.equipment_needed,
            "category_summary": self.category_summary,
            "intensity_summary": self.intensity_summary,
            "manual_adjustments": self.manual_adjustments,
            "block_duration_summaries": [
                summary if isinstance(summary, dict) else asdict(summary)
                for summary in self.block_duration_summaries
            ],
            "template_notes": self.template_notes,
            "schema_version": self.schema_version,
            "club_id": self.club_id,
            "blocks": [
                asdict(block) if hasattr(block, "__dict__") else block
                for block in (self.blocks or [])
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source": self.source,
            "primary_focus": self.primary_focus,
            "num_players_expected": self.num_players_expected,
            "formation": self.formation,
        }

    def validate(self):
        """
        Validate high-level practice integrity. Returns list of errors.
        Also emits Streamlit errors when available.
        """
        import practice_generator

        errors = []
        if not self.drills:
            errors.append("Session has no drills.")
            return errors

        # Ensure warmup first and cooldown last
        first_block = getattr(self.drills[0], "block_type", None) or practice_generator.CATEGORY_TO_BLOCK.get(
            getattr(self.drills[0], "category", None), "technical"
        )
        last_block = getattr(self.drills[-1], "block_type", None) or practice_generator.CATEGORY_TO_BLOCK.get(
            getattr(self.drills[-1], "category", None), "technical"
        )
        if first_block != "warmup":
            errors.append("Warmup block must be first.")
        if last_block != "cooldown":
            errors.append("Cool Down block must be last.")

        # No empty blocks (any block type should contain at least one drill if present)
        block_counts = {}
        total_allocated = 0
        for drill in self.drills:
            block = getattr(drill, "block_type", None) or practice_generator.CATEGORY_TO_BLOCK.get(
                getattr(drill, "category", None), "technical"
            )
            block_counts[block] = block_counts.get(block, 0) + 1
            dur = getattr(drill, "allocated_time", 0) or 0
            total_allocated += dur
            if dur <= 0:
                errors.append(f"Drill {drill.drill_name or drill.drill_id} has non-positive duration.")
        for required in ["warmup", "cooldown"]:
            if block_counts.get(required, 0) == 0:
                errors.append(f"Missing {required} block.")

        # Total duration consistency
        if self.duration_minutes and total_allocated != self.duration_minutes:
            errors.append(
                f"Total allocated time ({total_allocated} min) must equal session duration ({self.duration_minutes} min)."
            )

        try:
            import streamlit as st

            for msg in errors:
                st.error(msg)
        except Exception:
            pass
        return errors

    def collect_warnings(self, drills_df=None, team_profile=None, history_df=None, template_blocks=None):
        """
        Generate non-fatal warnings about the session: recency, age-group mismatch, field size, intensity curve deviation.
        """
        warnings = []
        if not self.drills:
            return warnings

        # Recency checks
        if history_df is not None:
            try:
                recency_table = practice_history.compute_recency_table(history_df)
                recent_ids = set(
                    recency_table[recency_table['label'] == "Recent"]['drill_id'].tolist()
                )
                for drill in self.drills:
                    if drill.drill_id in recent_ids:
                        warnings.append(f"Drill {drill.drill_id} was used very recently.")
            except Exception:
                pass

        # Age group mismatch
        team_age = None
        if team_profile:
            team_age = str(team_profile.get("age_group", "")).lower()
        if drills_df is not None and team_age:
            age_map = drills_df.set_index('drill_id')['age_groups'].to_dict()
            for drill in self.drills:
                allowed = str(age_map.get(drill.drill_id, "")).lower()
                if allowed and team_age not in allowed and allowed != "":
                    warnings.append(f"Drill {drill.drill_id} may not match team age group ({team_age}).")

        # Field size mismatch (simple presence check)
        if drills_df is not None and team_profile:
            field_pref = str(team_profile.get("field_size", "")).lower()
            if field_pref:
                size_map = drills_df.set_index('drill_id')['recommended_field_size'].to_dict()
                for drill in self.drills:
                    rec_size = str(size_map.get(drill.drill_id, "")).lower()
                    if rec_size and rec_size not in field_pref:
                        warnings.append(f"Drill {drill.drill_id} uses {rec_size} field; team pref is {field_pref}.")

        # Intensity curve deviation
        if self.drills:
            actual_curve = [str(d.intensity).lower() for d in self.drills]
            try:
                expected_curve = practice_generator.define_balanced_intensity_curve(len(self.drills))
            except Exception:
                expected_curve = []
            if actual_curve and actual_curve[0] == "high":
                warnings.append("First block is high intensity; consider starting lower.")
            if expected_curve:
                mismatches = sum(1 for a, e in zip(actual_curve, expected_curve) if a != e)
                if mismatches > 0:
                    warnings.append(f"Intensity curve deviates from expected pattern in {mismatches} spot(s).")

        # Template drift warnings
        if template_blocks:
            try:
                warnings.extend(practice_generator._analyze_template_drift(template_blocks, self.drills))
            except Exception:
                pass

        self.warnings = warnings
        return warnings


def validate_session_consistency(session: PracticeSession, drills_df=None, duration_tolerance: int = 2) -> List[str]:
    """
    Validate session structure and timings without raising.

    Returns:
        list of error strings (empty means valid).
    """
    errors: List[str] = []
    if not session or not session.drills:
        return ["Session has no drills."]

    # Duration and positive allocation
    total_allocated = 0
    for idx, drill in enumerate(session.drills, start=1):
        if not drill.drill_id:
            errors.append(f"Drill {idx} is missing a drill ID.")
        if not drill.category:
            errors.append(f"Drill {idx} has no category.")
        allocated = getattr(drill, "allocated_time", 0) or 0
        if allocated <= 0:
            errors.append(f"Drill {idx} has invalid duration.")
        total_allocated += allocated

    # Config duration tolerance (allow small rounding differences)
    if session.duration_minutes and total_allocated:
        if abs(total_allocated - session.duration_minutes) > duration_tolerance:
            errors.append(
                f"Allocated minutes ({total_allocated}) do not match session duration ({session.duration_minutes})."
            )

    # Warmup/cooldown presence
    try:
        import practice_generator

        block_types = [
            getattr(d, "block_type", None)
            or practice_generator.CATEGORY_TO_BLOCK.get(getattr(d, "category", None), "technical")
            for d in session.drills
        ]
        if "warmup" not in block_types:
            errors.append("Warmup block is missing.")
        if "cooldown" not in block_types:
            errors.append("Cool Down block is missing.")
    except Exception:
        # Do not fail validation because of import issues
        pass

    # Library integrity check
    if drills_df is not None:
        try:
            library_ids = set(drills_df.get("drill_id", []))
            for idx, drill in enumerate(session.drills, start=1):
                if library_ids and drill.drill_id not in library_ids:
                    errors.append(f"Drill {drill.drill_id or idx} is missing from the drill library.")
        except Exception:
            pass

    return errors


def move_drill_within_block(session: PracticeSession, block_type: str, idx_in_block: int, direction: str) -> None:
    """
    Move a drill one position within its block, respecting boundaries.

    Args:
        session: PracticeSession containing drills
        block_type: block identifier (e.g., "warmup")
        idx_in_block: index of the drill within that block
        direction: "up" or "down"
    """
    if not session or not session.drills:
        return
    indices = [i for i, d in enumerate(session.drills) if getattr(d, "block_type", None) == block_type]
    if not indices or idx_in_block < 0 or idx_in_block >= len(indices):
        return
    current_global = indices[idx_in_block]
    if direction == "up":
        if idx_in_block == 0:
            return
        target_global = indices[idx_in_block - 1]
    elif direction == "down":
        if idx_in_block == len(indices) - 1:
            return
        target_global = indices[idx_in_block + 1]
    else:
        return
    session.drills[current_global], session.drills[target_global] = session.drills[target_global], session.drills[current_global]


def move_drill_in_session(session: PracticeSession, global_index: int, direction: str) -> None:
    """
    Move a drill one position up or down in session.drills (simple neighbor swap).
    """
    drills = getattr(session, "drills", None)
    if not drills:
        return False
    n = len(drills)
    if not (0 <= global_index < n):
        return False

    # Enforce boundary rules: first/last immovable, second/second-to-last one-way.
    can_up, can_down = can_move_up_down(n, global_index)
    if direction == "up" and not can_up:
        return False
    if direction == "down" and not can_down:
        return False

    if direction == "up":
        target_index = global_index - 1
    elif direction == "down":
        target_index = global_index + 1
    else:
        return False

    drills_list = list(drills)
    drills_list[global_index], drills_list[target_index] = drills_list[target_index], drills_list[global_index]
    session.drills = drills_list
    try:
        session.manual_adjustments["reordered"] = session.manual_adjustments.get("reordered", 0) + 1
    except Exception:
        pass
    return True


def can_move_up_down(n: int, index: int) -> tuple[bool, bool]:
    """
    Given total drills n and a 0-based index, return (can_up, can_down):
    - first/last: (False, False)
    - second: (False, True)
    - second-to-last: (True, False)
    - middle: (True, True)
    """
    if n <= 1:
        return False, False
    if index == 0 or index == n - 1:
        return False, False
    if index == 1:
        return False, True
    if index == n - 2:
        return True, False
    return True, True


@dataclass
class PlayerAttributeMetric:
    """
    Placeholder model for player attribute tracking (future use).
    """
    metric_id: str
    schema_version: int
    club_id: Optional[str]
    team_id: str
    session_id: str
    player_id: Optional[str]
    attribute: str
    value: float
    timestamp: datetime
