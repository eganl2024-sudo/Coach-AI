
import sys
import os
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# Setup paths
sys.path.insert(0, os.path.abspath("src"))
import schedule

def test_smart_default_logic():
    print("🧪 Starting Schedule Sync Logic Test...")
    
    # 1. Setup Mock Data
    data_path = Path("./tmp_test_data")
    data_path.mkdir(parents=True, exist_ok=True)
    team_id = "test_team_123"
    
    today = date.today()
    # Scenario: Today is NOT a practice. Next practice is in 2 days.
    next_practice_date = today + timedelta(days=2)
    
    # Create valid schedule dataframe
    df = pd.DataFrame([
        {
            "event_date": next_practice_date.strftime("%Y-%m-%d"),
            "start_time": "18:00",
            "event_type": "Practice",
            "notes": "Test Practice"
        }
    ])
    
    # Save it using the actual module to ensure format matches app
    print(f"📝 Saving mock schedule for {team_id}...")
    schedule.save_team_schedule(data_path, team_id, df)
    
    # 2. Run the Logic (Copied from Practice Generator)
    print("⚙️ Running Generator Date Logic...")
    best_date = date.today()
    
    # --- LOGIC START ---
    try:
        # Load schedule
        sched_df = schedule.load_team_schedule(team_id, data_path)
        
        if not sched_df.empty:
            today_ts = pd.Timestamp.today().normalize()
            
            # Debug: Print loaded dates
            # print("Loaded events:", sched_df["event_date"].tolist())
            
            # Look for practices today or in future
            future_practices = sched_df[
                (pd.to_datetime(sched_df["event_date"], errors="coerce") >= today_ts) &
                (sched_df["event_type"].str.lower() == "practice")
            ].sort_values("event_date")
            
            if not future_practices.empty:
                # found the next one!
                next_practice = future_practices.iloc[0]["event_date"]
                best_date = pd.to_datetime(next_practice).date()
                print(f"✅ Logic found next practice: {best_date}")
            else:
                print("❌ Logic found NO future practices")
    except Exception as e:
        print(f"❌ Logic crashed: {e}")
    # --- LOGIC END ---
    
    # 3. Validation
    if best_date == next_practice_date:
        print(f"🏆 SUCCESS: Generator picked {best_date} (Next Scheduled Slot)")
    else:
        print(f"💀 FAILURE: Generator picked {best_date}, expected {next_practice_date}")
        exit(1)

    # Cleanup
    import shutil
    try:
        shutil.rmtree(data_path)
    except:
        pass

if __name__ == "__main__":
    test_smart_default_logic()
