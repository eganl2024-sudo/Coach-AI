
import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import config
import data_loader

def verify():
    print("Verifying Admin Setup...")
    
    # 1. Simulate data loading to trigger migration
    data_path = config.get_data_path()
    print(f"Loading drills from {data_path}...")
    drills_df = data_loader.load_drills(data_path)
    
    # 2. Check for new columns
    missing_cols = []
    required_cols = ['diagram_url', 'video_youtube_url', 'video_local_url', 'video_start_time']
    for col in required_cols:
        if col not in drills_df.columns:
            missing_cols.append(col)
            
    if missing_cols:
        print(f"❌ FAIL: Missing columns: {missing_cols}")
    else:
        print("✅ PASS: All new columns present in DataFrame")
        
    # 3. Check CSV file content on disk
    csv_path = Path(data_path) / 'drill_library.csv'
    df_disk = pd.read_csv(csv_path)
    disk_missing = [c for c in required_cols if c not in df_disk.columns]
    
    # Note: data_loader doesn't save back to disk immediately on load unless repair happened?
    # Actually data_loader.load_drills returns the DF with new columns (filled with default),
    # but it doesn't forcingly write back to CSV unless 'ensure_columns' triggered a repair AND we save it.
    # Looking at data_loader.py: load_drills calls ensure_columns but returns the DF. It does NOT save.
    # So the CSV on disk might NOT have the columns yet until the Admin App saves it.
    # BUT, the Admin App calls `save_drill_data` which DOES save.
    # So for this test, we should verify the DF returned has them, which confirms logic is correct.
    
    if disk_missing:
        print(f"ℹ️ INFO: Columns not yet in CSV on disk (expected until first save): {disk_missing}")
    else:
        print("✅ PASS: Columns already persisted to CSV")

if __name__ == "__main__":
    verify()
