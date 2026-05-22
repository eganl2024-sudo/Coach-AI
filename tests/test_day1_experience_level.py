"""
Day 1 Test Script: Experience Level System
==========================================

This script tests the experience level system without running Streamlit.
Run this with: python test_day1_experience_level.py

Tests:
1. Module imports correctly
2. Default level is 'essential'
3. Can set and get experience levels
4. Level validation works
5. Tier comparison functions work
6. Level info retrieval works
7. Upgrade benefits retrieval works
"""

import sys
from pathlib import Path

# Add src to path (same as Streamlit pages do)
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock streamlit.session_state for testing
class MockSessionState:
    def __init__(self):
        self._state = {}
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __contains__(self, key):
        return key in self._state
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __repr__(self):
        return f"MockSessionState({self._state})"

# Create mock streamlit module
class MockStreamlit:
    session_state = MockSessionState()
    
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Now import our module
import experience_level

def test_imports():
    """Test 1: Module imports correctly"""
    print("✅ TEST 1: Module imports successfully")
    return True

def test_default_level():
    """Test 2: Default level is 'essential'"""
    level = experience_level.get_experience_level()
    assert level == "essential", f"Expected 'essential', got '{level}'"
    print(f"✅ TEST 2: Default level is 'essential' ✓")
    return True

def test_set_get_level():
    """Test 3: Can set and get experience levels"""
    # Test setting to advanced
    changed = experience_level.set_experience_level("advanced")
    assert changed == True, "Should return True when level changes"
    level = experience_level.get_experience_level()
    assert level == "advanced", f"Expected 'advanced', got '{level}'"
    print(f"✅ TEST 3a: Set to 'advanced' ✓")
    
    # Test setting to expert
    experience_level.set_experience_level("expert")
    level = experience_level.get_experience_level()
    assert level == "expert", f"Expected 'expert', got '{level}'"
    print(f"✅ TEST 3b: Set to 'expert' ✓")
    
    # Test setting to same level returns False
    changed = experience_level.set_experience_level("expert")
    assert changed == False, "Should return False when level doesn't change"
    print(f"✅ TEST 3c: Setting same level returns False ✓")
    
    # Reset to essential for other tests
    experience_level.set_experience_level("essential")
    return True

def test_level_validation():
    """Test 4: Level validation works"""
    try:
        experience_level.set_experience_level("invalid_level")
        print("❌ TEST 4: Should have raised ValueError for invalid level")
        return False
    except ValueError as e:
        print(f"✅ TEST 4: Invalid level raises ValueError ✓")
        return True

def test_tier_functions():
    """Test 5: Tier comparison functions work"""
    # Set to essential
    experience_level.set_experience_level("essential")
    assert experience_level.is_essential_mode() == True
    assert experience_level.is_advanced_mode() == False
    assert experience_level.is_expert_mode() == False
    assert experience_level.is_at_least_advanced() == False
    print(f"✅ TEST 5a: Essential mode checks work ✓")
    
    # Set to advanced
    experience_level.set_experience_level("advanced")
    assert experience_level.is_essential_mode() == False
    assert experience_level.is_advanced_mode() == True
    assert experience_level.is_expert_mode() == False
    assert experience_level.is_at_least_advanced() == True
    print(f"✅ TEST 5b: Advanced mode checks work ✓")
    
    # Set to expert
    experience_level.set_experience_level("expert")
    assert experience_level.is_essential_mode() == False
    assert experience_level.is_advanced_mode() == False
    assert experience_level.is_expert_mode() == True
    assert experience_level.is_at_least_advanced() == True
    assert experience_level.is_at_least_expert() == True
    print(f"✅ TEST 5c: Expert mode checks work ✓")
    
    return True

def test_can_access_page():
    """Test 6: Page access control works"""
    # Essential user
    experience_level.set_experience_level("essential")
    assert experience_level.can_access_page("essential") == True
    assert experience_level.can_access_page("advanced") == False
    assert experience_level.can_access_page("expert") == False
    print(f"✅ TEST 6a: Essential user access control ✓")
    
    # Advanced user
    experience_level.set_experience_level("advanced")
    assert experience_level.can_access_page("essential") == True
    assert experience_level.can_access_page("advanced") == True
    assert experience_level.can_access_page("expert") == False
    print(f"✅ TEST 6b: Advanced user access control ✓")
    
    # Expert user
    experience_level.set_experience_level("expert")
    assert experience_level.can_access_page("essential") == True
    assert experience_level.can_access_page("advanced") == True
    assert experience_level.can_access_page("expert") == True
    print(f"✅ TEST 6c: Expert user access control ✓")
    
    return True

def test_level_info():
    """Test 7: Level info retrieval works"""
    essential_info = experience_level.get_level_info("essential")
    assert "label" in essential_info
    assert "icon" in essential_info
    assert "description" in essential_info
    assert essential_info["label"] == "Essential Mode"
    print(f"✅ TEST 7a: Level info structure correct ✓")
    
    # Test getting current level info
    experience_level.set_experience_level("advanced")
    current_info = experience_level.get_level_info()
    assert current_info["label"] == "Advanced Mode"
    print(f"✅ TEST 7b: Current level info works ✓")
    
    return True

def test_upgrade_benefits():
    """Test 8: Upgrade benefits retrieval works"""
    essential_benefits = experience_level.get_upgrade_benefits("essential")
    assert len(essential_benefits) > 0
    assert all(isinstance(b, str) for b in essential_benefits)
    print(f"✅ TEST 8a: Essential upgrade benefits: {len(essential_benefits)} items ✓")
    
    advanced_benefits = experience_level.get_upgrade_benefits("advanced")
    assert len(advanced_benefits) > 0
    print(f"✅ TEST 8b: Advanced upgrade benefits: {len(advanced_benefits)} items ✓")
    
    return True

def test_level_change_tracking():
    """Test 9: Level change history is tracked"""
    # Clear history
    st.session_state['level_change_history'] = []
    
    # Make some changes
    experience_level.set_experience_level("essential")
    experience_level.set_experience_level("advanced")
    experience_level.set_experience_level("expert")
    
    history = st.session_state.get('level_change_history', [])
    assert len(history) == 2, f"Expected 2 changes, got {len(history)}"  # essential->advanced, advanced->expert
    assert history[0]['from'] == 'essential'
    assert history[0]['to'] == 'advanced'
    assert history[1]['from'] == 'advanced'
    assert history[1]['to'] == 'expert'
    
    print(f"✅ TEST 9: Level change tracking works ({len(history)} changes tracked) ✓")
    return True

def test_analytics():
    """Test 10: Analytics function works"""
    analytics = experience_level.get_level_analytics()
    assert "current_level" in analytics
    assert "change_history" in analytics
    assert "total_changes" in analytics
    print(f"✅ TEST 10: Analytics retrieval works ✓")
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("DAY 1 TEST SUITE: Experience Level System")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_default_level,
        test_set_get_level,
        test_level_validation,
        test_tier_functions,
        test_can_access_page,
        test_level_info,
        test_upgrade_benefits,
        test_level_change_tracking,
        test_analytics,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 60)
    
    if failed == 0:
        print()
        print("🎉 ALL TESTS PASSED! Day 1 foundation is solid.")
        print()
        print("Next steps:")
        print("1. Start your Streamlit app: streamlit run app.py")
        print("2. Verify experience level initializes to 'essential'")
        print("3. Test that session state persists across page navigation")
        print()
    else:
        print()
        print(f"⚠️  {failed} test(s) failed. Please fix before proceeding.")
        print()
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
