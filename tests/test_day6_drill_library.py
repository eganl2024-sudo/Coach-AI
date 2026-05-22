"""
Day 6 Testing Script - Drill Library Enhancements
Tests the new features without launching the full app
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_imports():
    """Test that all active player platform imports work"""
    import streamlit as st
    import pandas as pd
    import config
    import data_loader
    import session_state
    import ui_components
    import experience_level
    from auth import require_auth


def test_filter_defaults():
    """Test that FILTER_DEFAULTS constant is properly defined in Drill Library"""
    drill_library_file = Path(__file__).parent.parent / "pages" / "1_Drill_Library.py"
    assert drill_library_file.exists(), f"Drill Library file not found at {drill_library_file}"
    
    with open(drill_library_file, 'r', encoding='utf-8') as f:
        code = f.read()
        
    # Check that FILTER_DEFAULTS is present
    assert "FILTER_DEFAULTS" in code, "FILTER_DEFAULTS should be defined in 1_Drill_Library.py"
    assert "solo_only" in code, "solo_only filter option should be defined"
    assert "position_relevance" in code, "position relevance filter should be defined"


def test_session_state_tracking():
    """Test that session state has drill_library_visited tracking"""
    import session_state
    import inspect
    
    source = inspect.getsource(session_state.init_session_state)
    assert "drill_library_visited" in source, "Missing drill_library_visited in init_session_state"


def test_file_syntax():
    """Test that the Drill Library file has valid Python syntax and imports"""
    drill_library_file = Path(__file__).parent.parent / "pages" / "1_Drill_Library.py"
    assert drill_library_file.exists(), f"Drill Library file not found at {drill_library_file}"
    
    with open(drill_library_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Try to compile the code to check for syntax validity
    compile(code, str(drill_library_file), 'exec')
    
    # Check for player platform focus additions
    assert "import experience_level" in code, "Missing experience_level import"
    assert "FILTER_DEFAULTS" in code, "Missing FILTER_DEFAULTS constant"
    assert "st.session_state.drills_browsed = True" in code, "Missing drills browsed session state tracking"
