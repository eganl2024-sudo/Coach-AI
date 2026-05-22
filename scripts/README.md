# Airtable Integration & Sync Pipeline

This directory contains the sync pipeline and data migration tools for the Player Development Platform.

---

## 1. Airtable Sync Script

The `airtable_sync.py` script synchronizes the Drill Library and Presenters tables from Airtable into local CSV files (`data/drill_library.csv` and `data/presenters.csv`) that are loaded directly by the Streamlit application.

### Prerequisites

You must set up your environment variables before running the script.

#### Environment Variables

- `AIRTABLE_API_KEY`: Your personal Airtable token (bearer token).
- `AIRTABLE_BASE_ID`: The base ID of the player development content base.
- `AIRTABLE_TABLE_DRILLS` (Optional): Name of the drills table in Airtable (defaults to `"Drill Library"`).
- `AIRTABLE_TABLE_PRESENTERS` (Optional): Name of the presenters table in Airtable (defaults to `"Presenters"`).

### How to Run

1. **Set Environment Variables (Windows PowerShell):**
   ```powershell
   $env:AIRTABLE_API_KEY="your-airtable-token-here"
   $env:AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"
   ```

2. **Set Environment Variables (Unix/macOS Bash/Zsh):**
   ```bash
   export AIRTABLE_API_KEY="your-airtable-token-here"
   export AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"
   ```

3. **Execute the Sync Script:**
   ```bash
   python scripts/airtable_sync.py
   ```

The script will fetch all records from Airtable, perform pagination automatically, apply the strict schema mappings, validate each drill record via `validate_drill()`, and overwrite the local CSV files only with validated rows.

---

## 2. One-Time Schema Migration Script

The `migrate_existing_drills.py` script upgrades your existing local `data/drill_library.csv` file by appending the 23 new schema columns (initialized with their correct default values) in a backward-compatible manner.

### How to Run

```bash
python scripts/migrate_existing_drills.py
```

This guarantees that all 45 seed drills are fully repaired and compatible with the new presenter lookup and data models.
