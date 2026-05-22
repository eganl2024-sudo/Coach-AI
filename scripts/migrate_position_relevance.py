"""
Position Relevance Migration Script
Updates existing drill_library.csv files to use the new position taxonomy.

Old values → New values:
  Forward    → Striker, Winger      (split — forwards can be either)
  Midfielder → Central Midfielder, Attacking Midfielder, Defensive Midfielder
  Defender   → Center Back, Full Back
  Goalkeeper → Goalkeeper (unchanged)

Drills tagged with multiple old values get all corresponding new values.
Universal/empty tags are preserved as-is.

Run from the Coach AI root directory:
    python scripts/migrate_position_relevance.py
"""
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "src"))

# ── Position mapping ───────────────────────────────────────────
# Maps old lowercase tag → list of new tags to replace it with
POSITION_MAP = {
    "forward":     ["Striker", "Winger"],
    "midfielder":  ["Central Midfielder", "Attacking Midfielder", "Defensive Midfielder"],
    "defender":    ["Center Back", "Full Back"],
    "goalkeeper":  ["Goalkeeper"],
    # Handle partial/variant spellings
    "gk":          ["Goalkeeper"],
    "cb":          ["Center Back"],
    "fb":          ["Full Back"],
    "mid":         ["Central Midfielder", "Attacking Midfielder"],
    "winger":      ["Winger"],
    "striker":     ["Striker"],
    "forward/winger": ["Striker", "Winger"],
    "midfield":    ["Central Midfielder", "Attacking Midfielder", "Defensive Midfielder"],
}

# Tags that mean "all positions" — preserve as empty (universal)
UNIVERSAL_TAGS = {"all", "universal", "any", "all positions", "", "nan", "none"}


def migrate_position_relevance(raw_value: str) -> str:
    """
    Convert a pipe-delimited position_relevance string from old to new taxonomy.
    Returns a pipe-delimited string of new position values.
    Preserves ordering and deduplicates.
    """
    if not raw_value or str(raw_value).strip().lower() in UNIVERSAL_TAGS:
        return ""

    parts = [p.strip() for p in str(raw_value).split("|") if p.strip()]
    new_positions = []

    for part in parts:
        part_lower = part.lower()

        # Already a new-taxonomy value — keep as-is
        new_taxonomy = {
            "goalkeeper", "center back", "full back",
            "defensive midfielder", "central midfielder", "attacking midfielder",
            "winger", "striker",
        }
        if part_lower in new_taxonomy:
            if part not in new_positions:
                new_positions.append(part)
            continue

        # Map old value to new
        mapped = POSITION_MAP.get(part_lower)
        if mapped:
            for m in mapped:
                if m not in new_positions:
                    new_positions.append(m)
        elif part_lower in UNIVERSAL_TAGS:
            # Skip — universal drills get empty string
            continue
        else:
            # Unknown value — preserve it as-is with a warning
            print(f"  WARNING: Unknown position tag '{part}' — preserved unchanged")
            if part not in new_positions:
                new_positions.append(part)

    return "|".join(new_positions)


def migrate_csv(csv_path: Path) -> int:
    """Migrate a single drill CSV. Returns number of rows updated."""
    print(f"\nProcessing: {csv_path}")
    df = pd.read_csv(csv_path, dtype=str)

    if "position_relevance" not in df.columns:
        print("  No position_relevance column found — skipping.")
        return 0

    updated = 0
    for i, row in df.iterrows():
        old_val = str(row.get("position_relevance", "")).strip()
        new_val = migrate_position_relevance(old_val)
        if old_val != new_val:
            df.at[i, "position_relevance"] = new_val
            updated += 1

    df.to_csv(csv_path, index=False)
    print(f"  Updated {updated} of {len(df)} drills.")
    return updated


def main():
    data_dir = ROOT / "data"
    if not data_dir.exists():
        print(f"ERROR: data directory not found at {data_dir}")
        sys.exit(1)

    csv_paths = list(data_dir.glob("**/drill_library.csv"))

    if not csv_paths:
        print("No drill_library.csv files found.")
        sys.exit(0)

    print("Position Relevance Migration")
    print("-" * 40)
    print(f"Found {len(csv_paths)} CSV file(s) to migrate.")

    total_updated = 0
    for path in csv_paths:
        total_updated += migrate_csv(path)

    print("\n" + "-" * 40)
    print(f"Migration complete. {total_updated} drill(s) updated total.")
    print("\nPosition mapping applied:")
    print("  Forward    -> Striker, Winger")
    print("  Midfielder -> Central Midfielder, Attacking Midfielder, Defensive Midfielder")
    print("  Defender   -> Center Back, Full Back")
    print("  Goalkeeper -> Goalkeeper (unchanged)")


if __name__ == "__main__":
    main()
