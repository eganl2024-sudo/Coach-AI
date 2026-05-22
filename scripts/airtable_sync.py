#!/usr/bin/env python
"""
Airtable Sync Pipeline for Player Development Platform.

Synchronizes the Drill Library and Presenters tables from Airtable into 
local CSV files (data/drill_library.csv and data/presenters.csv) with robust
validation and schema checking.
"""
import os
import sys
import pandas as pd
import requests
from pathlib import Path

# Add src to python path to import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from data_loader import DRILL_COLUMNS, DRILL_DEFAULTS, PRESENTER_COLUMNS, PRESENTER_DEFAULTS
    from validation import validate_drill
except ImportError as exc:
    print(f"Error importing modules: {exc}")
    sys.exit(1)

DRILL_FIELD_MAP = {
    "Drill ID": "drill_id",
    "Drill Name": "drill_name",
    "Category": "category",
    "Description": "description",
    "Players Min": "players_min",
    "Players Max": "players_max",
    "Duration Minutes": "duration_minutes",
    "Field Type": "field_type",
    "Setup Data": "setup_data",
    "Equipment": "equipment",
    "Coaching Points": "coaching_points",
    "Difficulty": "difficulty",
    "Intensity": "intensity",
    "Coach Rating": "coach_rating",
    "Personal Notes": "personal_notes",
    "Times Used": "times_used",
    "Last Used Date": "last_used_date",
    "Tags": "tags",
    "Is Favorite": "is_favorite",
    "Diagram Path": "diagram_path",
    "Diagram Metadata": "diagram_metadata",
    "Positions": "positions",
    "Age Groups": "age_groups",
    "Coach Cues": "coach_cues",
    "Progression": "progression",
    "Recommended Field Size": "recommended_field_size",
    "Diagram URL": "diagram_url",
    "Video YouTube URL": "video_youtube_url",
    "Video Local URL": "video_local_url",
    "Video Start Time": "video_start_time",
    "Position Relevance": "position_relevance",
    "Skill Category": "skill_category",
    "Solo Possible": "solo_possible",
    "Min Equipment": "min_equipment",
    "Game Application": "game_application",
    "Video URL": "video_url",
    "Video Thumbnail": "video_thumbnail",
    "Coaching Cues": "coaching_cues",
    "Position Track": "position_track",
    "Drill Type": "drill_type",
    "Series Name": "series_name",
    "Series Order": "series_order",
    "RRS Benchmark": "rrs_benchmark",
    "Space Required": "space_required",
    "Position Primary": "position_primary",
    "Presenter ID": "presenter_id",
    "College Context": "college_context",
    "Pro Context": "pro_context",
    "Variations": "variations",
    "Prerequisite Drill": "prerequisite_drill",
    "Next Drill": "next_drill",
    "Status": "status",
    "Video URL Short": "video_url_short",
    "Video URL Full": "video_url_full",
    "Video Status": "video_status",
    "Filming Date": "filming_date",
    "Filming Notes": "filming_notes",
    "Beta Ready": "beta_ready",
    "Date Published": "date_published",
    "Slug": "slug",
    "Common Mistakes": "common_mistakes"
}

PRESENTER_FIELD_MAP = {
    "Presenter ID": "presenter_id",
    "Full Name": "full_name",
    "Display Name": "display_name",
    "Current Team": "current_team",
    "Team Level": "team_level",
    "Position": "position",
    "College": "college",
    "Graduation Year": "graduation_year",
    "Bio Short": "bio_short",
    "Headshot URL": "headshot_url",
    "Active": "active",
    "Position Tracks": "position_tracks"
}

def fetch_table_records(api_key: str, base_id: str, table_name: str) -> list:
    """Fetch all records from an Airtable table handling pagination."""
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {"Authorization": f"Bearer {api_key}"}
    records = []
    offset = None
    
    while True:
        params = {}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise RuntimeError(f"Error fetching from table {table_name}: {response.status_code} - {response.text}")
            
        data = response.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
            
    return records

def sync_drills(api_key: str, base_id: str, table_name: str, output_path: Path):
    """Sync drills table from Airtable, validate, and write to CSV."""
    print(f"Syncing drills from Airtable table '{table_name}'...")
    records = fetch_table_records(api_key, base_id, table_name)
    print(f"Fetched {len(records)} records from Airtable.")
    
    rows = []
    errors = 0
    for record in records:
        fields = record.get("fields", {})
        # Map fields to our CSV columns using field map
        mapped_data = {}
        for airtable_name, csv_name in DRILL_FIELD_MAP.items():
            mapped_data[csv_name] = fields.get(airtable_name, DRILL_DEFAULTS.get(csv_name))
            
        # Convert lists to pipe-delimited strings (e.g. for tags, cues)
        for key in ["tags", "coaching_cues", "coach_cues", "position_relevance", "age_groups", "positions"]:
            val = mapped_data.get(key)
            if isinstance(val, list):
                mapped_data[key] = "|".join([str(v) for v in val])
                
        # Validate drill using central validation helper
        try:
            drill_obj = validate_drill(mapped_data)
            rows.append(drill_obj.to_record(preferred_fields=DRILL_COLUMNS))
        except ValueError as exc:
            print(f"Validation failed for drill {mapped_data.get('drill_id', 'UNKNOWN')} ({mapped_data.get('drill_name', 'UNKNOWN')}): {exc}")
            errors += 1
            
    if rows:
        df = pd.DataFrame(rows)
        # Ensure all columns exist and are ordered correctly
        for col in DRILL_COLUMNS:
            if col not in df.columns:
                df[col] = DRILL_DEFAULTS.get(col, "")
        df = df[DRILL_COLUMNS]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Successfully wrote {len(rows)} validated drills to {output_path} ({errors} validation failures).")
    else:
        print("No valid drill rows found to write.")

def sync_presenters(api_key: str, base_id: str, table_name: str, output_path: Path):
    """Sync presenters table from Airtable and write to CSV."""
    print(f"Syncing presenters from Airtable table '{table_name}'...")
    records = fetch_table_records(api_key, base_id, table_name)
    print(f"Fetched {len(records)} presenter records from Airtable.")
    
    rows = []
    for record in records:
        fields = record.get("fields", {})
        mapped_data = {}
        for airtable_name, csv_name in PRESENTER_FIELD_MAP.items():
            mapped_data[csv_name] = fields.get(airtable_name, PRESENTER_DEFAULTS.get(csv_name))
            
        # Handle position_tracks if passed as a list
        if isinstance(mapped_data.get("position_tracks"), list):
            mapped_data["position_tracks"] = "|".join([str(v) for v in mapped_data["position_tracks"]])
            
        rows.append(mapped_data)
        
    if rows:
        df = pd.DataFrame(rows)
        # Ensure all columns exist and are ordered correctly
        for col in PRESENTER_COLUMNS:
            if col not in df.columns:
                df[col] = PRESENTER_DEFAULTS.get(col, "")
        df = df[PRESENTER_COLUMNS]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Successfully wrote {len(rows)} presenters to {output_path}.")
    else:
        print("No presenter rows found to write.")

def main():
    """Main CLI execution."""
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    
    if not api_key:
        print("ERROR: AIRTABLE_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please export or set it in your environment before running this script.", file=sys.stderr)
        sys.exit(1)
        
    if not base_id:
        print("ERROR: AIRTABLE_BASE_ID environment variable is not set.", file=sys.stderr)
        print("Please export or set it in your environment before running this script.", file=sys.stderr)
        sys.exit(1)
        
    drills_table = os.environ.get("AIRTABLE_TABLE_DRILLS", "Drill Library")
    presenters_table = os.environ.get("AIRTABLE_TABLE_PRESENTERS", "Presenters")
    
    project_root = Path(__file__).parent.parent
    drills_csv_path = project_root / "data" / "drill_library.csv"
    presenters_csv_path = project_root / "data" / "presenters.csv"
    
    try:
        sync_presenters(api_key, base_id, presenters_table, presenters_csv_path)
        sync_drills(api_key, base_id, drills_table, drills_csv_path)
        print("\nAirtable sync pipeline completed successfully.")
    except Exception as exc:
        print(f"\nERROR running sync pipeline: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
