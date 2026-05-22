"""Intelligent practice generation engine"""
from dataclasses import dataclass, asdict
import pandas as pd
from drills import (
    calculate_drill_score,
    define_balanced_intensity_curve
)
from config import PLAYER_TOLERANCE
from models import PracticeConfig, PracticeSession, SessionDrill, DrillScoreBreakdown, validate_session_consistency
import practice_history

CATEGORY_TO_BLOCK = {
    "Warmup": "warmup",
    "Technical": "technical",
    "Tactical": "tactical",
    "Small Sided Games": "ssg",
    "Conditioning": "conditioning",
    "Cool Down": "cooldown",
}
BLOCK_TO_CATEGORY = {block: category for category, block in CATEGORY_TO_BLOCK.items()}

BLOCK_ORDER = ["warmup", "technical", "tactical", "ssg", "conditioning", "cooldown"]
BLOCK_DURATION_TARGETS = {
    "warmup": (8, 12),
    "technical": (15, 25),
    "tactical": (20, 30),
    "ssg": (12, 20),
    "conditioning": (4, 8),
    "cooldown": (5, 8),
}


def _resolve_block(drill):
    block_type = getattr(drill, "block_type", None)
    if block_type:
        return block_type
    if isinstance(drill, dict):
        block_type = drill.get("block_type")
        if block_type:
            return block_type
        category = drill.get("category")
    else:
        category = getattr(drill, "category", None)
    return CATEGORY_TO_BLOCK.get(category, "technical")


def _analyze_template_drift(template_blocks, session_drills):
    """
    Compare template expectations to actual session drills and return warnings.
    """
    warnings = []
    if not template_blocks:
        return warnings
    block_counts = {}
    for drill in session_drills:
        b = _resolve_block(drill)
        block_counts[b] = block_counts.get(b, 0) + 1
    for block_type, drill_ids in template_blocks.items():
        expected = len(drill_ids)
        actual = block_counts.get(block_type, 0)
        if actual < expected:
            warnings.append(f"Template block {block_type} expected {expected} drill(s), found {actual}.")
    # Order check
    if session_drills:
        if _resolve_block(session_drills[0]) != "warmup":
            warnings.append("Warmup is not first; template may be drifting.")
        if _resolve_block(session_drills[-1]) != "cooldown":
            warnings.append("Cooldown is not last; template may be drifting.")
    return warnings


def score_drill_candidate(drill_dict,
                          block_type,
                          team_profile,
                          practice_config: PracticeConfig,
                          history_df=None,
                          target_intensity=None,
                          focus_tags=None,
                          recent_usage=None):
    """
    Score a candidate drill with a unified pipeline, returning a detailed breakdown.

    Components include: base scoring, block alignment, player fit, focus match,
    intensity match, category match, rating adjustment, and recency penalty.
    """
    focus_tags = {tag.lower() for tag in (focus_tags or [])}
    num_players = practice_config.num_players
    target_intensity = target_intensity or drill_dict.get("target_intensity") or drill_dict.get("intensity") or "medium"

    recency_map = recent_usage or (practice_history.get_recent_drill_usage(history_df) if history_df is not None else {})
    base_score, _base = calculate_drill_score(
        drill_dict,
        team_profile.get("skill_level", "intermediate"),
        recency_map,
        target_intensity,
        practice_config.selected_categories,
    )

    # Components
    candidate_block = CATEGORY_TO_BLOCK.get(drill_dict.get("category"), "technical")
    block_alignment = 10.0 if candidate_block == block_type else -5.0

    try:
        players_min = int(drill_dict.get("players_min", 0) or 0)
        players_max = int(drill_dict.get("players_max", 0) or 0)
        player_fit_score = 5.0 if players_min <= num_players <= players_max else -10.0
    except Exception:
        player_fit_score = 0.0

    drill_tags = {
        tag.strip().lower()
        for tag in str(drill_dict.get("tags", "") or "").split("|")
        if tag.strip()
    }
    focus_match = 5.0 if focus_tags and drill_tags.intersection(focus_tags) else 0.0

    intensity_match = 5.0 if str(drill_dict.get("intensity", "")).lower() == str(target_intensity).lower() else -2.5

    category_match = 5.0 if drill_dict.get("category") in practice_config.selected_categories else -5.0

    # Category boost from Focus Tracker
    category_boost = 0.0
    if practice_config.focus_boost_categories:
        drill_category = drill_dict.get("category", "")
        if drill_category in practice_config.focus_boost_categories:
            category_boost = 15.0  # Significant boost for under-trained categories

    rating_adjustment = 0.0
    try:
        rating_adjustment = (float(drill_dict.get("coach_rating", 3)) - 3.0) * 2.0
    except Exception:
        rating_adjustment = 0.0

    recency_penalty = 0.0
    if history_df is not None:
        last_used = practice_history.get_recent_use(drill_dict.get("drill_id"), history_df)
        if last_used is not None:
            try:
                days_ago = (pd.Timestamp.now(tz="UTC").normalize() - pd.to_datetime(last_used).normalize()).days
                if days_ago <= 7:
                    recency_penalty = -15.0
                elif days_ago <= 14:
                    recency_penalty = -5.0
            except Exception:
                recency_penalty = 0.0

    total_score = base_score + block_alignment + player_fit_score + focus_match + intensity_match + category_match + category_boost + rating_adjustment + recency_penalty

    other_factors = {
        "base_score": float(base_score),
        "category_boost": float(category_boost)
    }

    breakdown = DrillScoreBreakdown(
        drill_id=drill_dict.get("drill_id", ""),
        total_score=float(total_score),
        recency_penalty=float(recency_penalty),
        focus_match=float(focus_match),
        intensity_match=float(intensity_match),
        player_fit_score=float(player_fit_score),
        category_match=float(category_match),
        block_alignment=float(block_alignment),
        rating_adjustment=float(rating_adjustment),
        other_factors=other_factors,
    )
    return breakdown


def build_scoring_narrative(breakdown: DrillScoreBreakdown):
    """
    Generate a human-friendly explanation of why a drill was selected.
    """
    parts = []
    if breakdown.focus_match:
        parts.append(f"matches focus (+{breakdown.focus_match:.0f})")
    if breakdown.intensity_match > 0:
        parts.append(f"intensity aligned (+{breakdown.intensity_match:.0f})")
    if breakdown.intensity_match < 0:
        parts.append(f"intensity off ({breakdown.intensity_match:.0f})")
    if breakdown.player_fit_score:
        parts.append(f"fits players (+{breakdown.player_fit_score:.0f})")
    if breakdown.category_match > 0:
        parts.append("in selected category")
    if breakdown.block_alignment > 0:
        parts.append("matches block type")
    if breakdown.recency_penalty < 0:
        parts.append(f"recently used ({breakdown.recency_penalty:.0f})")
    if breakdown.rating_adjustment:
        parts.append(f"coach rating adj ({breakdown.rating_adjustment:+.0f})")
    if not parts:
        parts.append("solid overall score")
    return f"Selected because it " + ", ".join(parts) + f" - total {breakdown.total_score:.0f}."


@dataclass
class BlockDurationSummary:
    block_type: str
    total_minutes: int
    target_min: int
    target_max: int
    status: str  # "ok", "low", "high"


@dataclass
class ReplacementExplanation:
    matches_intensity: bool
    matches_players: bool
    matches_block_type: bool
    matches_focus_tags: bool
    underused_recently: bool


@dataclass
class ReplacementCandidate:
    drill: dict
    score: float
    explanation: ReplacementExplanation


def sort_session_drills(drills):
    block_rank = {b: i for i, b in enumerate(BLOCK_ORDER)}
    intensity_rank = {"low": 0, "medium": 1, "high": 2}

    def sort_key(sd: SessionDrill):
        block_pos = block_rank.get((sd.block_type or "technical"), 999)
        intensity_value = str(getattr(sd, "intensity", "medium") or "medium").lower()
        intensity_pos = intensity_rank.get(intensity_value, 1)
        extras = getattr(sd, "extras", {}) or {}
        original_index = extras.get("original_index", getattr(sd, "position", 0))
        return (block_pos, intensity_pos, original_index)

    sorted_drills = sorted(drills, key=sort_key)

    counters = {}
    for sd in sorted_drills:
        block_key = sd.block_type or "technical"
        counters.setdefault(block_key, 0)
        sd.block_index = counters[block_key]
        counters[block_key] += 1

    return sorted_drills


def summarize_block_durations(drills):
    totals = {}
    for sd in drills:
        block = getattr(sd, "block_type", None)
        if not block:
            continue
        minutes = getattr(sd, "allocated_time", None) or 0
        totals[block] = totals.get(block, 0) + minutes

    summaries = []
    for block_type in BLOCK_ORDER:
        total = totals.get(block_type)
        if total is None:
            continue
        target_min, target_max = BLOCK_DURATION_TARGETS.get(block_type, (0, 9999))
        if total < target_min:
            status = "low"
        elif total > target_max:
            status = "high"
        else:
            status = "ok"
        summaries.append(
            BlockDurationSummary(
                block_type=block_type,
                total_minutes=total,
                target_min=target_min,
                target_max=target_max,
                status=status,
            )
        )
    return summaries


def _intensity_value(value):
    return str(value or "").strip().lower()


def _apply_recency_metadata(drill, drill_recency, team_summary):
    label = "New"
    if drill_recency:
        label = drill_recency.get(drill.get('drill_id'), {}).get("label", "New")
    drill['recency_label'] = label
    if not team_summary:
        return label
    if label == "Fresh":
        team_summary["fresh_selected"] += 1
    elif label == "Neutral":
        team_summary["neutral_selected"] += 1
    elif label == "Recent":
        team_summary["recent_selected"] += 1
    return label


def _refresh_recency_totals(drills, team_summary):
    mapping = {
        "Fresh": "fresh_selected",
        "Neutral": "neutral_selected",
        "Recent": "recent_selected"
    }
    for key in mapping.values():
        team_summary[key] = 0
    for drill in drills:
        label = drill.get("recency_label")
        target = mapping.get(label)
        if target:
            team_summary[target] += 1


def _find_block_candidate(drills_df, block_type, num_players, exclude_ids):
    category = BLOCK_TO_CATEGORY.get(block_type)
    if not category:
        return None
    candidates = drills_df[drills_df['category'] == category].copy()
    if candidates.empty:
        return None
    candidates = candidates[
        (candidates['players_min'] <= num_players + PLAYER_TOLERANCE) &
        (candidates['players_max'] >= num_players - PLAYER_TOLERANCE)
    ]
    if candidates.empty:
        return None
    candidates = candidates[~candidates['drill_id'].isin(exclude_ids)]
    if candidates.empty:
        return None

    def score(intensity):
        value = _intensity_value(intensity)
        if value == "low":
            return 0
        if value == "medium":
            return 1
        return 2

    candidates = candidates.assign(
        _intensity_score=candidates['intensity'].apply(score)
    ).sort_values(by=['_intensity_score', 'coach_rating'], ascending=[True, False])
    return candidates.iloc[0].to_dict()


def _remove_low_intensity_technical(drills, selected_ids, team_summary=None):
    for idx, drill in enumerate(drills):
        block = drill.get('block_type') or CATEGORY_TO_BLOCK.get(drill.get('category'), "technical")
        intensity = _intensity_value(drill.get('intensity'))
        if block == "technical" and intensity in {"low", "medium"}:
            removed = drills.pop(idx)
            if selected_ids is not None:
                selected_ids.discard(removed.get('drill_id'))
            if team_summary is not None:
                team_summary["auto_removed_drills"] = team_summary.get("auto_removed_drills", 0) + 1
            return removed
    for idx, drill in enumerate(drills):
        block = drill.get('block_type') or CATEGORY_TO_BLOCK.get(drill.get('category'), "technical")
        if block not in {"warmup", "cooldown"}:
            removed = drills.pop(idx)
            if selected_ids is not None:
                selected_ids.discard(removed.get('drill_id'))
            return removed
    if drills:
        removed = drills.pop()
        if selected_ids is not None:
            selected_ids.discard(removed.get('drill_id'))
        if team_summary is not None:
            team_summary["auto_removed_drills"] = team_summary.get("auto_removed_drills", 0) + 1
        return removed
    return None


def generate_practice_plan(config: PracticeConfig,
                           team_profile,
                           drills_df,
                           recent_usage,
                           team_profile_context=None,
                           drill_recency=None,
                           template_blocks=None,
                           history_df=None,
                           debug=False,
                           debug_top_n=5):
    """
    Generate an intelligent practice plan.

    Args:
        team_profile: Dict with team info (team_name, skill_level, etc.)
        duration_minutes: Total practice duration
        num_players: Number of players attending
        selected_categories: List of category names to include
        num_drills: Number of drills to select
        drills_df: DataFrame with all available drills
        recent_usage: Dict of {drill_id: sessions_ago} from practice history

    Returns:
        dict with:
            - success: bool
            - session: PracticeSession
            - debug: optional scoring payload when debug=True
            - error/suggestion when failing
    """

    config.validate()
    selected_categories = config.selected_categories
    duration_minutes = config.duration_minutes
    num_players = config.num_players
    num_drills = config.num_drills
    use_team_profile = config.use_team_profile

    # Filter drills by selected categories
    category_filtered = drills_df[drills_df['category'].isin(selected_categories)].copy()

    # Filter by player count (with tolerance)
    player_filtered = category_filtered[
        (category_filtered['players_min'] <= num_players + PLAYER_TOLERANCE) &
        (category_filtered['players_max'] >= num_players - PLAYER_TOLERANCE)
    ].copy()

    # Check if we have enough drills
    available_count = len(player_filtered)
    if available_count < num_drills:
        max_players = drills_df['players_max'].max()
        min_players = drills_df['players_min'].min()

        return {
            'success': False,
            'error': f'Only {available_count} drills available in selected categories, need {num_drills}',
            'suggestion': f'Enable more categories, reduce number of drills to {available_count}, or add more drills to your library' if available_count > 0 else f'No drills support {num_players} players (drills range: {min_players}-{max_players} players). Try adjusting player count to between {min_players} and {max_players}, or add drills that support {num_players} players'
        }

    # Generate intensity curve
    intensity_curve = define_balanced_intensity_curve(num_drills)

    # Select drills for each position
    template_blocks = template_blocks or config.template_blocks or {}
    if template_blocks:
        missing_from_template = []
        library_ids = set(drills_df.get("drill_id", [])) if drills_df is not None else set()
        for ids in template_blocks.values():
            for drill_id in ids or []:
                if library_ids and drill_id not in library_ids:
                    missing_from_template.append(drill_id)
        if missing_from_template:
            return {
                'success': False,
                'error': "Template references missing drills: " + ", ".join(sorted(set(missing_from_template))),
                'suggestion': "Repair the template in Template Studio or add the missing drills."
            }
    selected_drills = []
    available_pool = player_filtered.copy()
    team_level = team_profile['skill_level']
    selected_ids = set()

    team_summary = {
        "used_profile": bool(use_team_profile and team_profile_context),
        "focus_matches": 0,
        "playstyle_matches": 0,
        "objective_matches": 0,
        "injury_penalties": 0,
        "focus_tags": team_profile_context.get("focus_tags", []) if team_profile_context else [],
        "play_style": team_profile_context.get("play_style") if team_profile_context else "",
        "season_objectives": team_profile_context.get("season_objectives") if team_profile_context else "",
        "fresh_selected": 0,
        "neutral_selected": 0,
        "recent_selected": 0,
        "recent_skipped": 0,
        "auto_inserted_blocks": [],
        "auto_removed_drills": 0,
    }

    recent_ids = set()
    if drill_recency:
        recent_ids = {
            drill_id for drill_id, info in drill_recency.items()
            if info.get("label") == "Recent"
        }

    def _append_drill(drill_dict, position, target_intensity, fallback_flag=False):
        drill_dict['position'] = position
        drill_dict['original_index'] = position
        drill_dict['block_type'] = CATEGORY_TO_BLOCK.get(drill_dict.get('category'), "technical")
        drill_dict['target_intensity'] = target_intensity
        if fallback_flag:
            drill_dict['fallback'] = True
        drill_dict['diagram_path'] = drill_dict.get('diagram_path', '')
        if team_summary["used_profile"]:
            if drill_dict.get('_profile_focus_match'):
                team_summary["focus_matches"] += 1
            if drill_dict.get('_profile_playstyle_match'):
                team_summary["playstyle_matches"] += 1
            if drill_dict.get('_profile_objective_match'):
                team_summary["objective_matches"] += 1
            if drill_dict.get('_profile_injury_penalty'):
                team_summary["injury_penalties"] += 1
        _apply_recency_metadata(drill_dict, drill_recency, team_summary)
        selected_drills.append(drill_dict)
        selected_ids.add(drill_dict['drill_id'])

    template_notes = []
    if template_blocks:
        for block_type, drill_ids in template_blocks.items():
            for drill_id in drill_ids:
                matches = drills_df[drills_df['drill_id'] == drill_id]
                if matches.empty:
                    template_notes.append(f"{drill_id} not found")
                    continue
                drill_row = matches.iloc[0].to_dict()
                drill_row['block_type'] = block_type
                position = len(selected_drills)
                if position < len(intensity_curve):
                    target_for_position = intensity_curve[position]
                else:
                    target_for_position = drill_row.get('target_intensity', 'medium')
                _append_drill(drill_row, position, target_for_position)

    template_count = len(selected_drills)
    debug_payload = []
    for position in range(template_count, num_drills):
        target_intensity = intensity_curve[position]
        fallback_flag = False
        working_pool = available_pool
        if len(working_pool) == 0:
            fallback_pool = category_filtered[
                ~category_filtered['drill_id'].isin(selected_ids)
            ]
            if fallback_pool.empty:
                fallback_pool = drills_df[
                    ~drills_df['drill_id'].isin(selected_ids)
                ]
            if fallback_pool.empty:
                return {
                    'success': False,
                    'error': f'Ran out of available drills at position {position + 1}',
                    'suggestion': 'Enable more categories or reduce number of drills'
                }
            working_pool = fallback_pool
            fallback_flag = True

        if recent_ids:
            non_recent_pool = working_pool[
                ~working_pool['drill_id'].isin(recent_ids)
            ]
            if not non_recent_pool.empty:
                team_summary["recent_skipped"] += len(working_pool) - len(non_recent_pool)
                working_pool = non_recent_pool

        # Score all available drills for this position using unified scorer
        ranked = []
        focus_tags = team_profile_context.get("focus_tags", []) if (use_team_profile and team_profile_context) else []
        for _, candidate in working_pool.iterrows():
            candidate_dict = candidate.to_dict()
            candidate_dict["target_intensity"] = target_intensity
            breakdown = score_drill_candidate(
                candidate_dict,
                block_type=CATEGORY_TO_BLOCK.get(candidate_dict.get("category"), "technical"),
                team_profile=team_profile,
                practice_config=config,
                history_df=history_df,
                target_intensity=target_intensity,
                focus_tags=focus_tags,
                recent_usage=recent_usage,
            )
            ranked.append((breakdown.total_score, candidate_dict, breakdown))

        if not ranked:
            return {
                'success': False,
                'error': 'No suitable drills after filtering/scoring.',
                'suggestion': 'Relax filters or add drills.'
            }

        ranked.sort(key=lambda item: item[0], reverse=True)
        best_score, best_drill, best_breakdown = ranked[0]
        best_drill["_score_breakdown"] = best_breakdown

        _append_drill(best_drill, position, target_intensity, fallback_flag=fallback_flag)

        if debug:
            top_candidates = []
            for score, cand, breakdown in ranked[:max(1, debug_top_n)]:
                top_candidates.append({
                    "drill_id": cand.get("drill_id"),
                    "drill_name": cand.get("drill_name"),
                    "score": float(score),
                    "breakdown": asdict(breakdown),
                })
            debug_payload.append({
                "position": position,
                "block_type": best_drill.get("block_type"),
                "chosen": best_drill.get("drill_id"),
                "candidates": top_candidates,
            })

        # Remove from pool to avoid duplicates
        available_pool = available_pool[available_pool['drill_id'] != best_drill['drill_id']]

    required_blocks = [("warmup", "Warmup"), ("cooldown", "Cool Down")]
    for block_type, label in required_blocks:
        if not any((drill.get('block_type') == block_type) for drill in selected_drills):
            candidate = _find_block_candidate(drills_df, block_type, num_players, selected_ids)
            if candidate is None:
                return {
                    'success': False,
                    'error': f"Could not find a suitable {label} drill in the library.",
                    'suggestion': f"Add at least one {label} drill or adjust filters to include that category."
                }
            candidate['block_type'] = block_type
            candidate['position'] = len(selected_drills)
            candidate['original_index'] = len(selected_drills)
            candidate['target_intensity'] = _intensity_value(candidate.get('intensity')) or 'low'
            _apply_recency_metadata(candidate, drill_recency, team_summary)
            selected_drills.append(candidate)
            selected_ids.add(candidate['drill_id'])
            team_summary["auto_inserted_blocks"].append(block_type)
            if len(selected_drills) > num_drills:
                _remove_low_intensity_technical(selected_drills, selected_ids, team_summary)

    _refresh_recency_totals(selected_drills, team_summary)

    # Calculate timing for each drill
    base_time = duration_minutes // len(selected_drills)
    remainder = duration_minutes % len(selected_drills)

    for i, drill in enumerate(selected_drills):
        allocated_time = base_time + (1 if i < remainder else 0)
        drill['allocated_time'] = allocated_time

    # Aggregate equipment needed
    all_equipment = set()
    for drill in selected_drills:
        equipment = str(drill.get('equipment', ''))
        if equipment and equipment != 'nan':
            items = [e.strip() for e in equipment.split(',')]
            all_equipment.update(items)

    equipment_list = sorted([e for e in all_equipment if e and e.lower() != 'none'])

    # Category summary
    category_summary = {}
    for drill in selected_drills:
        cat = drill['category']
        category_summary[cat] = category_summary.get(cat, 0) + 1

    # Intensity summary
    intensity_summary = {}
    for drill in selected_drills:
        intensity = drill['intensity']
        intensity_summary[intensity] = intensity_summary.get(intensity, 0) + 1

    session_drills = [SessionDrill.from_dict(drill) for drill in selected_drills]
    session_drills = sort_session_drills(session_drills)
    practice_session = PracticeSession.create(
        team_name=team_profile['team_name'],
        team_id=team_profile['team_id'],
        session_date=config.session_date,
        config=config,
        drills=session_drills,
        team_profile_summary=team_summary,
        equipment_needed=equipment_list,
        category_summary=category_summary,
        intensity_summary=intensity_summary
    )
    validation_errors = validate_session_consistency(practice_session, drills_df=drills_df)
    if validation_errors:
        return {
            'success': False,
            'error': "Session failed validation: " + "; ".join(validation_errors),
            'suggestion': "Adjust drill selections or durations and try again."
        }
    practice_session.template_notes = template_notes
    practice_session.block_duration_summaries = summarize_block_durations(session_drills)
    return {
        'success': True,
        'session': practice_session,
        'debug': debug_payload if debug else None,
    }


def generate_multiweek_cycle(base_config: PracticeConfig,
                             team_profile,
                             drills_df,
                             recent_usage,
                             team_profile_context=None,
                             drill_recency=None,
                             template_blocks=None,
                             weeks: int = 4,
                             history_df=None):
    """
    Build a multi-week practice cycle (2 sessions/week) blending modular and scripted blocks.

    Modular: standard generator (75% of sessions). Scripted: honor provided template_blocks when available.
    Returns dict with weeks, sessions, and per-week metrics.
    """
    total_sessions = max(1, weeks) * 2
    if template_blocks:
        library_ids = set(drills_df.get("drill_id", [])) if drills_df is not None else set()
        missing_from_template = []
        for ids in template_blocks.values():
            for drill_id in ids or []:
                if library_ids and drill_id not in library_ids:
                    missing_from_template.append(drill_id)
        if missing_from_template:
            return {
                'success': False,
                'error': "Template references missing drills: " + ", ".join(sorted(set(missing_from_template))),
                'suggestion': "Repair the template in Template Studio or add the missing drills."
            }
    modular_target = max(1, int(round(total_sessions * 0.75)))
    sessions = []
    week_entries = []

    for week in range(1, weeks + 1):
        week_sessions = []
        for slot in range(1, 3):
            session_index = len(sessions)
            use_scripted = session_index >= modular_target
            config_copy = PracticeConfig(**base_config.to_dict())
            # Ensure stable intensity curve per week by reusing base config values
            config_copy.session_notes = f"Week {week} - Session {slot}"
            result = generate_practice_plan(
                config_copy,
                team_profile,
                drills_df,
                recent_usage,
                team_profile_context=team_profile_context,
                drill_recency=drill_recency,
                template_blocks=template_blocks if use_scripted else None,
                history_df=history_df,
            )
            if not result.get('success'):
                return {'success': False, 'error': result.get('error'), 'suggestion': result.get('suggestion')}
            session = result['session']
            validation_errors = validate_session_consistency(session, drills_df=drills_df)
            if validation_errors:
                return {
                    'success': False,
                    'error': "Generated session failed validation: " + "; ".join(validation_errors),
                    'suggestion': "Repair or adjust template/drill pool and retry."
                }
            sessions.append(session)
            week_sessions.append(session)

        # Per-week metrics
        category_counts = {}
        intensity_counts = {}
        total_minutes = 0
        for sess in week_sessions:
            total_minutes += sess.duration_minutes
            for cat, count in (sess.category_summary or {}).items():
                category_counts[cat] = category_counts.get(cat, 0) + count
            for inten, count in (sess.intensity_summary or {}).items():
                intensity_counts[inten] = intensity_counts.get(inten, 0) + count
        week_entries.append({
            "week": week,
            "sessions": week_sessions,
            "category_counts": category_counts,
            "intensity_counts": intensity_counts,
            "total_minutes": total_minutes
        })

    return {
        'success': True,
        'weeks': week_entries,
        'total_sessions': len(sessions)
    }


def find_best_replacement_for_block(block_type,
                                    session,
                                    drills_df,
                                    team_profile,
                                    practice_config: PracticeConfig,
                                    history_df=None,
                                    recency_map=None,
                                    debug=False,
                                    debug_top_n=5):
    """
    Find the best replacement drill for a given block considering duplicates, block alignment, intensity, players, recency.
    """
    recency_map = recency_map or {}
    existing_ids = {d.drill_id for d in session.drills}
    category = BLOCK_TO_CATEGORY.get(block_type)
    if not category:
        return None
    candidates = drills_df[drills_df['category'] == category].copy()
    if candidates.empty:
        return None

    num_players = practice_config.num_players
    candidates = candidates[
        (candidates['players_min'] <= num_players + PLAYER_TOLERANCE) &
        (candidates['players_max'] >= num_players - PLAYER_TOLERANCE)
    ]
    candidates = candidates[~candidates['drill_id'].isin(existing_ids)]
    if candidates.empty:
        return None

    ranked = []
    focus_tags = getattr(practice_config, "focus_tags", []) or []
    for _, candidate in candidates.iterrows():
        candidate_dict = candidate.to_dict()
        candidate_dict["target_intensity"] = candidate_dict.get("intensity", "medium")
        breakdown = score_drill_candidate(
            candidate_dict,
            block_type=block_type,
            team_profile=team_profile,
            practice_config=practice_config,
            history_df=history_df,
            target_intensity=candidate_dict.get("target_intensity"),
            focus_tags=focus_tags,
            recent_usage=None,
        )
        # penalize recency label "Recent"
        rec_label = recency_map.get(candidate_dict.get("drill_id"), {}).get("label", "New")
        if rec_label == "Recent":
            breakdown.total_score -= 10
            breakdown.recency_penalty -= 10
        ranked.append((breakdown.total_score, candidate_dict, breakdown))

    ranked.sort(key=lambda item: item[0], reverse=True)
    if not ranked:
        return None
    _, best_dict, best_breakdown = ranked[0]
    best_dict['block_type'] = block_type
    best_dict["_score_breakdown"] = best_breakdown
    debug_bundle = None
    if debug:
        candidates_debug = []
        for score, cand, bd in ranked[:max(1, debug_top_n)]:
            candidates_debug.append({
                "drill_id": cand.get("drill_id"),
                "drill_name": cand.get("drill_name"),
                "score": float(score),
                "breakdown": asdict(bd),
            })
        debug_bundle = {
            "block_type": block_type,
            "chosen": best_dict.get("drill_id"),
            "candidates": candidates_debug,
        }
    return SessionDrill.from_dict(best_dict), debug_bundle


def auto_repair_session(session: PracticeSession, drills_df, templates=None):
    """
    Attempt to repair a session: ensure warmup/cooldown order, insert missing blocks, adjust durations,
    and replace missing drills with nearest matches where possible.
    Returns (repaired_session, applied_changes[list]).
    """
    changes = []
    drills_list = list(session.drills)

    # Ensure warmup first, cooldown last
    if drills_list:
        if drills_list[0].block_type != "warmup":
            drills_list.sort(key=lambda d: 0 if d.block_type == "warmup" else 1)
            changes.append("Moved warmup to first position.")
        if drills_list[-1].block_type != "cooldown":
            drills_list.sort(key=lambda d: 0 if d.block_type == "warmup" else (2 if d.block_type == "cooldown" else 1))
            changes.append("Moved cooldown to last position.")

    # Insert missing warmup/cooldown if absent
    existing_ids = {d.drill_id for d in drills_list}
    def _insert_block(block_type, label):
        candidate = _find_block_candidate(drills_df, block_type, session.num_players, existing_ids)
        if candidate:
            candidate['block_type'] = block_type
            candidate['target_intensity'] = candidate.get('intensity', 'low')
            drills_list.append(SessionDrill.from_dict(candidate))
            changes.append(f"Inserted {label} drill {candidate.get('drill_id')}.")
    has_warmup = any(d.block_type == "warmup" for d in drills_list)
    has_cooldown = any(d.block_type == "cooldown" for d in drills_list)
    if not has_warmup:
        _insert_block("warmup", "warmup")
    if not has_cooldown:
        _insert_block("cooldown", "cooldown")

    # Remove drills that are missing from library
    library_ids = set(drills_df['drill_id'])
    repaired = []
    for d in drills_list:
        if d.drill_id not in library_ids:
            changes.append(f"Removed missing drill {d.drill_id}.")
            continue
        repaired.append(d)
    drills_list = repaired

    # Recompute durations to match session duration
    if drills_list:
        total_alloc = sum(getattr(d, "allocated_time", 0) or 0 for d in drills_list)
        if total_alloc != session.duration_minutes and total_alloc > 0:
            factor = session.duration_minutes / total_alloc
            for d in drills_list:
                d.allocated_time = max(1, int(round((d.allocated_time or 0) * factor)))
            changes.append("Rescaled drill durations to match session length.")

    repaired_session = PracticeSession(
        session_id=session.session_id,
        team_id=session.team_id,
        team_name=session.team_name,
        session_date=session.session_date,
        config=session.config,
        duration_minutes=session.duration_minutes,
        num_players=session.num_players,
        num_drills=len(drills_list),
        selected_categories=session.selected_categories,
        drills=drills_list,
        team_profile_summary=session.team_profile_summary,
        equipment_needed=session.equipment_needed,
        category_summary=session.category_summary,
        intensity_summary=session.intensity_summary,
        manual_adjustments=session.manual_adjustments,
        block_duration_summaries=session.block_duration_summaries,
        template_notes=session.template_notes,
    )
    return repaired_session, changes
