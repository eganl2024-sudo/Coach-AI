import sys
import pandas as pd
from pathlib import Path

# Add src to python path to import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from data_loader import DRILL_COLUMNS, DRILL_DEFAULTS
    from utils import ensure_columns
except ImportError as exc:
    print(f"Error importing / loading modules: {exc}")
    sys.exit(1)

def migrate():
    """Migrates all local drill CSV files to the latest schema version."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        sys.exit(1)
        
    # Find all CSV files named drill_library.csv or drills.csv under data
    csv_paths = list(data_dir.glob("**/drill_library.csv")) + list(data_dir.glob("**/drills.csv"))
    
    if not csv_paths:
        print(f"No drill CSV files found under {data_dir}")
        sys.exit(0)
        
    for csv_path in csv_paths:
        print(f"\nLoading {csv_path} for schema migration...")
        df = pd.read_csv(csv_path)
        
        print("Applying ensure_columns to add safe defaults...")
        repairs, df = ensure_columns(df, DRILL_DEFAULTS)
        
        # Ensure columns order is exactly DRILL_COLUMNS
        df = df[DRILL_COLUMNS]
        
        # Save back to same file
        df.to_csv(csv_path, index=False)
        print(f"Successfully migrated {len(df)} drills in {csv_path}.")
        print(f"Added columns: {repairs.get('added_columns', [])}")

if __name__ == "__main__":
    migrate()
