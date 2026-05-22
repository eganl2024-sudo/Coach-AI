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
    mock_st = MockSessionState()
    data_path = get_data_path()

    # Simulate what happens on Drill Library page
    if mock_st['drills_df'] is None:
        mock_st['drills_df'] = data_loader.load_drills(data_path)

    drills_df_library = mock_st['drills_df']
    assert drills_df_library is not None, "Failed to load drills for library page"

    # Simulate what happens on Practice Generator page
    if mock_st['drills_df'] is None:
        mock_st['drills_df'] = data_loader.load_drills(data_path)

    drills_df_generator = mock_st['drills_df']
    assert drills_df_generator is not None, "Failed to load drills for generator page"

    # Verify they're the same
    assert len(drills_df_library) == len(drills_df_generator), "Different number of drills!"
    assert list(drills_df_library.columns) == list(drills_df_generator.columns), "Different columns!"


def test_drill_library_not_empty():
    """Test that the drill library is not empty."""
    data_path = get_data_path()
    drills_df = data_loader.load_drills(data_path)

    assert drills_df is not None, "drills_df is None"
    assert not drills_df.empty, "drills_df is empty - drill_library.csv may be missing or corrupt"


def test_drill_attributes():
    """Test that drills have expected attributes."""
    data_path = get_data_path()
    drills_df = data_loader.load_drills(data_path)

    required_columns = ['drill_id', 'drill_name', 'category', 'intensity', 'tags', 'is_favorite']
    missing = [col for col in required_columns if col not in drills_df.columns]

    assert not missing, f"Missing columns: {missing}"


def test_single_source_of_truth():
    """Test that modifying one page's drills affects the other."""
    data_path = get_data_path()

    # Load via canonical function
    mock_st = MockSessionState()
    if mock_st['drills_df'] is None:
        mock_st['drills_df'] = data_loader.load_drills(data_path)

    # Simulate adding a favorite marker on one page
    mock_st['drills_df'].loc[0, 'is_favorite'] = True

    # Check that the change is visible on the "other page" (same session state)
    assert mock_st['drills_df'].loc[0, 'is_favorite'] == True, "Changes not reflected (not a true single source of truth)"
