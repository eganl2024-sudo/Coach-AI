"""Test script for backend changes - Task 1 & Task 4"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pandas as pd
from src import practice_history, config

def test_history_schema_extension():
    """Test that new columns are added correctly"""
    print("\n=== Testing History Schema Extension ===")

    data_path = config.get_data_path()
    team_id = "team_a"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    print(f"Loaded {len(history_df)} sessions for {team_id}")
    print(f"Columns: {list(history_df.columns)}")

    # Check new columns exist
    assert 'is_favorite' in history_df.columns, "is_favorite column missing!"
    assert 'coach_notes' in history_df.columns, "coach_notes column missing!"

    # Check defaults
    assert history_df['is_favorite'].dtype == bool, "is_favorite should be boolean!"
    assert all(history_df['coach_notes'].fillna('').astype(str) == history_df['coach_notes']), "coach_notes should be string!"

    print("[PASS] Schema extension passed!")

def test_set_favorite():
    """Test toggling favorite status"""
    print("\n=== Testing Set Favorite ===")

    data_path = config.get_data_path()
    team_id = "team_a"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    if len(history_df) == 0:
        print("[WARN] No sessions to test with")
        return

    # Get first session
    first_session = history_df.iloc[0]
    session_date = str(first_session['session_date'])
    session_name = first_session['session_name']

    print(f"Testing with session: {session_date} - {session_name}")

    # Toggle to True
    result = practice_history.set_session_favorite(
        team_id, session_date, session_name, True, data_path
    )
    assert result, "Failed to set favorite to True"

    # Reload and check
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)
    mask = (history_df['session_date'].astype(str) == session_date) & (history_df['session_name'] == session_name)
    assert history_df.loc[mask, 'is_favorite'].iloc[0] == True, "Favorite not set!"

    # Toggle to False
    result = practice_history.set_session_favorite(
        team_id, session_date, session_name, False, data_path
    )
    assert result, "Failed to set favorite to False"

    # Reload and check
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)
    mask = (history_df['session_date'].astype(str) == session_date) & (history_df['session_name'] == session_name)
    assert history_df.loc[mask, 'is_favorite'].iloc[0] == False, "Favorite not unset!"

    print("[PASS] Set favorite passed!")

def test_update_notes():
    """Test updating session notes"""
    print("\n=== Testing Update Notes ===")

    data_path = config.get_data_path()
    team_id = "team_a"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    if len(history_df) == 0:
        print("[WARN] No sessions to test with")
        return

    # Get first session
    first_session = history_df.iloc[0]
    session_date = str(first_session['session_date'])
    session_name = first_session['session_name']

    test_notes = "Test notes from backend test script!"

    print(f"Testing with session: {session_date} - {session_name}")
    print(f"Setting notes: {test_notes}")

    # Update notes
    result = practice_history.update_session_notes(
        team_id, session_date, session_name, test_notes, data_path
    )
    assert result, "Failed to update notes"

    # Reload and check
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)
    mask = (history_df['session_date'].astype(str) == session_date) & (history_df['session_name'] == session_name)
    saved_notes = history_df.loc[mask, 'coach_notes'].iloc[0]
    assert saved_notes == test_notes, f"Notes mismatch! Expected '{test_notes}', got '{saved_notes}'"

    # Clear notes
    result = practice_history.update_session_notes(
        team_id, session_date, session_name, "", data_path
    )

    print("[PASS] Update notes passed!")

def test_compute_recent_focus():
    """Test analytics function"""
    print("\n=== Testing Compute Recent Focus ===")

    data_path = config.get_data_path()
    team_id = "team_a"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    print(f"Computing focus for {len(history_df)} sessions")

    # Compute focus
    focus = practice_history.compute_recent_focus(history_df, days=28)

    print(f"Total minutes: {focus['total_minutes']}")
    print(f"Category breakdown:")
    for category, minutes in sorted(focus['category_minutes'].items(), key=lambda x: -x[1]):
        print(f"  {category}: {minutes:.1f} minutes")

    # Assertions
    assert 'category_minutes' in focus
    assert 'attribute_minutes' in focus
    assert 'total_minutes' in focus
    assert isinstance(focus['total_minutes'], float)

    print("[PASS] Compute recent focus passed!")

def test_empty_history():
    """Test with non-existent team (empty history)"""
    print("\n=== Testing Empty History ===")

    data_path = config.get_data_path()
    team_id = "nonexistent_team"

    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    assert len(history_df) == 0, "Should have empty history"

    focus = practice_history.compute_recent_focus(history_df)
    assert focus['total_minutes'] == 0.0
    assert len(focus['category_minutes']) == 0

    print("[PASS] Empty history handled correctly!")

if __name__ == "__main__":
    print("Running Backend Tests...")
    print("=" * 60)

    try:
        test_history_schema_extension()
        test_set_favorite()
        test_update_notes()
        test_compute_recent_focus()
        test_empty_history()

        print("\n" + "=" * 60)
        print("SUCCESS: All backend tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
