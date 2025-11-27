"""Test script for Phase 2 backend changes - Session structure, titles, and tags"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pandas as pd
from src import practice_history, config


def test_schema_extension():
    """Test that new Phase 2 columns are added correctly"""
    print("\n[TEST] Schema Extension")

    # Get demo team
    data_path = config.get_data_path()
    team_id = "U14_BOYS"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    # Check new columns exist
    required_columns = ['session_title', 'session_tags', 'session_structure']
    missing = [col for col in required_columns if col not in history_df.columns]

    assert not missing, f"Missing columns: {missing}"

    print("[PASS] All Phase 2 columns present")

    # Check column types
    for col in required_columns:
        if history_df[col].dtype != 'object':
            print(f"[WARN] Column {col} is not string type: {history_df[col].dtype}")

    print("[PASS] Column types validated")
    # No explicit return; pytest handles assertions


def test_parse_session_tags():
    """Test session tags parsing"""
    print("\n[TEST] Parse Session Tags")

    # Test empty/None
    assert practice_history.parse_session_tags('') == []
    assert practice_history.parse_session_tags(None) == []
    print("[PASS] Empty/None handling")

    # Test single tag
    assert practice_history.parse_session_tags('passing') == ['passing']
    print("[PASS] Single tag")

    # Test multiple tags
    assert practice_history.parse_session_tags('passing|shooting|defending') == ['passing', 'shooting', 'defending']
    print("[PASS] Multiple tags")

    # Test with spaces
    assert practice_history.parse_session_tags(' passing | shooting ') == ['passing', 'shooting']
    print("[PASS] Tag trimming")

    # Implicit pass


def test_update_session_title():
    """Test updating session title"""
    print("\n[TEST] Update Session Title")

    data_path = config.get_data_path()
    team_id = "U14_BOYS"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    if len(history_df) == 0:
        print("[SKIP] No history to test with")
        return

    # Get first session
    first_session = history_df.iloc[0]
    session_date = first_session['session_date']
    session_name = first_session['session_name']

    # Update title
    new_title = "Test Title - Phase 2"
    success = practice_history.update_session_title(
        team_id, session_date, session_name, new_title, data_path
    )

    assert success, "Failed to update session title"

    # Reload and verify
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)
    first_session = history_df.iloc[0]

    assert str(first_session['session_title']).strip() == new_title, f"Title not updated correctly: {first_session['session_title']}"

    print(f"[PASS] Title updated to: {new_title}")

    # Clear title
    practice_history.update_session_title(
        team_id, session_date, session_name, "", data_path
    )

    # Implicit pass


def test_update_session_tags():
    """Test updating session tags"""
    print("\n[TEST] Update Session Tags")

    data_path = config.get_data_path()
    team_id = "U14_BOYS"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    if len(history_df) == 0:
        print("[SKIP] No history to test with")
        return

    # Get first session
    first_session = history_df.iloc[0]
    session_date = first_session['session_date']
    session_name = first_session['session_name']

    # Update tags
    test_tags = ["passing", "shooting", "tactical"]
    success = practice_history.update_session_tags(
        team_id, session_date, session_name, test_tags, data_path
    )

    assert success, "Failed to update session tags"

    # Reload and verify
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)
    first_session = history_df.iloc[0]

    saved_tags = practice_history.parse_session_tags(first_session['session_tags'])

    assert saved_tags == test_tags, f"Tags not saved correctly: {saved_tags} != {test_tags}"

    print(f"[PASS] Tags updated to: {test_tags}")

    # Clear tags
    practice_history.update_session_tags(
        team_id, session_date, session_name, [], data_path
    )

    # Implicit pass


def test_session_structure_persistence():
    """Test saving and loading session structure"""
    print("\n[TEST] Session Structure Persistence")

    data_path = config.get_data_path()
    team_id = "U14_BOYS"

    # Load history
    mtime = practice_history.get_history_mtime(team_id, data_path)
    history_df = practice_history.load_practice_history(team_id, data_path, mtime)

    if len(history_df) == 0:
        print("[SKIP] No history to test with")
        return

    # Get first session
    first_session = history_df.iloc[0]
    session_date = first_session['session_date']
    session_name = first_session['session_name']

    # Check if structure exists
    session_structure = first_session.get('session_structure', '')

    if session_structure and session_structure != '':
        print("[PASS] Session structure found")
        print(f"[INFO] Structure size: {len(session_structure)} characters")

        # Try to parse it as JSON
        import json
        try:
            structure_data = json.loads(session_structure)
            print(f"[PASS] Valid JSON structure")

            # Check for expected keys
            if 'drills' in structure_data:
                print(f"[PASS] Found {len(structure_data['drills'])} drills in structure")
            else:
                print("[WARN] No drills key in structure")

        except json.JSONDecodeError as e:
            assert False, f"Invalid JSON in structure: {e}"
    else:
        print("[INFO] No structure saved (session created before Phase 2)")
        print("[INFO] Generate a new practice to test structure saving")

    # Implicit pass


def main():
    """Run all Phase 2 backend tests"""
    print("=" * 60)
    print("PHASE 2 BACKEND TESTS")
    print("=" * 60)

    tests = [
        ("Schema Extension", test_schema_extension),
        ("Parse Session Tags", test_parse_session_tags),
        ("Update Session Title", test_update_session_title),
        ("Update Session Tags", test_update_session_tags),
        ("Session Structure Persistence", test_session_structure_persistence),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] Test {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All Phase 2 backend tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
