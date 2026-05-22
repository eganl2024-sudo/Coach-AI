"""Systematic drill addition utilities"""
import pandas as pd
from pathlib import Path
from drills import (
    validate_drill_on_submit,
    validate_drill_schema,
    check_duplicate_id,
    suggest_next_drill_id
)


def add_single_drill(drill_dict, drills_df, data_path):
    errors = validate_drill_on_submit(drill_dict)
    is_valid = len(errors) == 0
    
    if not is_valid:
        error_messages = [f"{field}: {msg}" for field, msg in errors.items()]
        return False, "Validation failed: " + "; ".join(error_messages), None

    try:
        validate_drill_schema(drill_dict)
    except Exception as exc:
        return False, f"Schema validation failed: {exc}", None
    
    drill_id = drill_dict['drill_id']
    is_duplicate = check_duplicate_id(drill_id, drills_df)
    
    if is_duplicate:
        return False, f"Duplicate drill ID: {drill_id} already exists", None
    
    new_row = pd.DataFrame([drill_dict])
    updated_df = pd.concat([drills_df, new_row], ignore_index=True)
    
    try:
        drill_library_file = Path(data_path) / 'drill_library.csv'
        updated_df.to_csv(drill_library_file, index=False)
        return True, f"Drill {drill_id} added successfully!", updated_df
    except Exception as e:
        return False, f"Error saving: {e}", None
