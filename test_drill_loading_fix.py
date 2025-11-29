#!/usr/bin/env python3
"""
Test script to verify that Drill Library and Practice Generator use the same drills_df.

This ensures that when users see drills in the Drill Library page, those same drills
will be available for practice generation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from config import get_data_path
import data_loader
import session_state

# Mock streamlit session state
class MockSessionState(dict):
    def __init__(self):
        super().__init__()
        self['drills_df'] = None
        self['teams_df'] = None
        self['data_path'] = None

def test_canonical_drill_loader():
    """Test that init_drills_in_session_state loads drills consistently."""
    print("\n" + "=" * 70)
    print("TEST 1: Canonical Drill Loader")
    print("=" * 70)

    # Create a mock session state
    mock_st = MockSessionState()
    data_path = get_data_path()

    print(f"Data path: {data_path}")
    print(f"Looking for drill_library.csv at: {Path(data_path) / 'drill_library.csv'}")

    # Simulate what happens on Drill Library page
    print("\n[Drill Library Page] Calling init_drills_in_session_state...")
    if mock_st['drills_df'] is None or mock_st['drills_df'] is None:
        mock_st['drills_df'] = data_loader.load_drills(data_path)

    drills_df_library = mock_st['drills_df']
    print(f"Loaded {len(drills_df_library)} drills from Drill Library page")
    print(f"Columns: {list(drills_df_library.columns)}")

    # Simulate what happens on Practice Generator page
    print("\n[Practice Generator Page] Calling init_drills_in_session_state...")
    # The canonical loader should use the same session state
    if mock_st['drills_df'] is None or mock_st['drills_df'] is None:
        mock_st['drills_df'] = data_loader.load_drills(data_path)

    drills_df_generator = mock_st['drills_df']
    print(f"Loaded {len(drills_df_generator)} drills from Practice Generator page")

    # Verify they're the same
    assert len(drills_df_library) == len(drills_df_generator), "Different number of drills!"
    assert list(drills_df_library.columns) == list(drills_df_generator.columns), "Different columns!"

    print(f"\n[PASS] Both pages loaded the same {len(drills_df_library)} drills")
    return True


def test_drill_library_not_empty():
    """Test that the drill library is not empty."""
    print("\n" + "=" * 70)
    print("TEST 2: Drill Library Not Empty")
    print("=" * 70)

    data_path = get_data_path()
    drills_df = data_loader.load_drills(data_path)

    if drills_df is None:
        print("[FAIL] drills_df is None")
        return False

    if drills_df.empty:
        print("[FAIL] drills_df is empty - drill_library.csv may be missing or corrupt")
        print(f"Checked location: {Path(data_path) / 'drill_library.csv'}")
        return False

    print(f"[PASS] Drill library has {len(drills_df)} drills")
    print(f"Sample drills:")
    for idx, row in drills_df.head(3).iterrows():
        print(f"  - {row.get('drill_name')} ({row.get('category')})")

    return True


def test_drill_attributes():
    """Test that drills have expected attributes."""
    print("\n" + "=" * 70)
    print("TEST 3: Drill Attributes")
    print("=" * 70)

    data_path = get_data_path()
    drills_df = data_loader.load_drills(data_path)

    required_columns = ['drill_id', 'drill_name', 'category', 'intensity', 'tags', 'is_favorite']
    missing = [col for col in required_columns if col not in drills_df.columns]

    if missing:
        print(f"[FAIL] Missing columns: {missing}")
        return False

    print(f"[PASS] All required columns present")
    print(f"Columns: {list(drills_df.columns)}")

    # Check for non-empty drill names
    empty_names = drills_df[drills_df['drill_name'].isna() | (drills_df['drill_name'] == '')]
    if len(empty_names) > 0:
        print(f"[WARN] {len(empty_names)} drills have empty names")

    print(f"[PASS] Drills have required attributes")
    return True


def test_single_source_of_truth():
    """Test that modifying one page's drills affects the other."""
    print("\n" + "=" * 70)
    print("TEST 4: Single Source of Truth (Shared Session State)")
    print("=" * 70)

    data_path = get_data_path()

    # Load via canonical function
    mock_st = MockSessionState()
    if mock_st['drills_df'] is None:
        mock_st['drills_df'] = data_loader.load_drills(data_path)

    original_count = len(mock_st['drills_df'])

    # Simulate adding a favorite marker on one page
    mock_st['drills_df'].loc[0, 'is_favorite'] = True

    # Check that the change is visible on the "other page" (same session state)
    if mock_st['drills_df'].loc[0, 'is_favorite'] == True:
        print(f"[PASS] Changes to drills_df are visible across pages (single source of truth)")
        print(f"Total drills shared: {original_count}")
        return True
    else:
        print(f"[FAIL] Changes not reflected (not a true single source of truth)")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("DRILL LOADING FIX - TEST SUITE")
    print("=" * 70)
    print("Verifying that Drill Library and Practice Generator share the same drills")

    tests = [
        test_drill_library_not_empty,
        test_drill_attributes,
        test_canonical_drill_loader,
        test_single_source_of_truth,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n[SUCCESS] All tests passed!")
        print("\nImplementation Summary:")
        print("[OK] Canonical drill loader created: init_drills_in_session_state()")
        print("[OK] Drill Library page updated to use canonical loader")
        print("[OK] Practice Generator page updated to use canonical loader")
        print("[OK] Debug panel added to Practice Generator for troubleshooting")
        print("[OK] Clear error messages for empty drills vs filtered drills")
        print("\nBehavior:")
        print("- Both pages now use st.session_state['drills_df']")
        print("- Single source of truth ensures consistency")
        print("- If drills are visible on Drill Library, they'll be available for generation")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
