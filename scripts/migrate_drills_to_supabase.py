import os
import sys
import pandas as pd
from pathlib import Path

# Load local .env variables manually
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# Add src to project path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


import db
import config

def migrate():
    print("Starting Drills Database Migration to Supabase...")
    
    # 1. Load local drills CSV
    csv_path = config.PRODUCTION_DATA_DIR / 'drill_library.csv'
    if not csv_path.exists():
        print(f"Error: Local drill library not found at {csv_path}")
        return
        
    print(f"Loading drills from {csv_path}...")
    df = pd.read_csv(csv_path)
    df = df.fillna("")
    
    drills = df.to_dict(orient="records")
    print(f"Loaded {len(drills)} drills to migrate.")
    
    # 2. Initialize Supabase client
    try:
        client = db.get_client()
    except Exception as e:
        print(f"Error: Failed to initialize Supabase client. {e}")
        return
        
    # 3. Batch/Iterative Upsert
    success_count = 0
    fail_count = 0
    
    for drill in drills:
        drill_id = drill.get("drill_id")
        print(f"Upserting drill: {drill_id} ({drill.get('drill_name')})...")
        
        try:
            # Cast Boolean fields safely
            for col in ["is_favorite", "solo_possible", "beta_ready"]:
                if col in drill:
                    drill[col] = str(drill[col]).strip().lower() in {"1", "true", "yes", "y"}
            
            # Cast Integer fields safely
            for col in ["players_min", "players_max", "duration_minutes", "allocated_time", "coach_rating", "series_order"]:
                if col in drill:
                    try:
                        drill[col] = int(float(drill[col])) if drill[col] != "" else 0
                    except ValueError:
                        drill[col] = 0
            
            # Filter temporary/runtime pandas columns
            drill.pop("_position_matched", None)
            
            client.table("drills").upsert(drill).execute()
            print(f"Drill {drill_id} migrated successfully.")
            success_count += 1
        except Exception as e:
            print(f"Failed to migrate drill {drill_id}: {e}")
            fail_count += 1
            
    print(f"\nMigration Completed! Success: {success_count}/{len(drills)}, Failed: {fail_count}")

if __name__ == "__main__":
    migrate()
