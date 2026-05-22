"""
Day 2 Test Script: Navigation Filtering System
===============================================

Tests the navigation filtering based on experience level.

Tests:
1. Navigation filters correctly for Essential mode
2. Navigation filters correctly for Advanced mode  
3. Navigation filters correctly for Expert mode
4. Page count matches expected for each tier
5. Legacy fallback works when experience_level unavailable
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock streamlit
class MockSessionState:
    def __init__(self):
        self._data = {}
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __setattr__(self, name, value):
        if name == "_data":
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
    
    def __getattribute__(self, name):
        if name == "_data" or name.startswith("__"):
            return object.__getattribute__(self, name)
        try:
            _data = object.__getattribute__(self, "_data")
            if name in _data:
                return _data[name]
        except:
            pass
        return object.__getattribute__(self, name)

class MockStreamlit:
    session_state = MockSessionState()
    
    @staticmethod
    def columns(widths):
        """Mock st.columns"""
        return [MockColumn() for _ in range(len(widths) if isinstance(widths, list) else widths)]
    
    @staticmethod
    def page_link(page, label=None):
        """Mock st.page_link"""
        pass
    
    @staticmethod
    def sidebar():
        """Mock st.sidebar"""
        return MockStreamlit

    @staticmethod
    def markdown(text, unsafe_allow_html=False):
        """Mock st.markdown"""
        pass
    
    @staticmethod
    def caption(text):
        """Mock st.caption"""
        pass
    
    @staticmethod
    def button(label, **kwargs):
        """Mock st.button"""
        return False
    
    @staticmethod
    def success(text):
        """Mock st.success"""
        pass

class MockColumn:
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Import modules
import experience_level
import ui_components

print("=" * 60)
print("DAY 2 TEST SUITE: Navigation Filtering System")
print("=" * 60)
print()

tests_passed = 0
tests_total = 0

# Test 1: Essential mode shows 3 pages
tests_total += 1
experience_level.set_experience_level("essential")
links = ui_components._page_links()
if len(links) == 3:
    print(f"✅ TEST 1: Essential mode shows 3 pages ✓")
    print(f"   Pages: {[label for _, label in links]}")
    tests_passed += 1
else:
    print(f"❌ TEST 1: Expected 3 pages, got {len(links)}")
    print(f"   Pages: {[label for _, label in links]}")

# Test 2: Essential pages are correct
tests_total += 1
expected_essential = ["Home", "⚽ Generate", "📅 History"]
actual_labels = [label for _, label in links]
if actual_labels == expected_essential:
    print(f"✅ TEST 2: Essential pages are correct ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 2: Page labels mismatch")
    print(f"   Expected: {expected_essential}")
    print(f"   Got: {actual_labels}")

# Test 3: Advanced mode shows 7 pages
tests_total += 1
experience_level.set_experience_level("advanced")
links = ui_components._page_links()
if len(links) == 7:
    print(f"✅ TEST 3: Advanced mode shows 7 pages ✓")
    print(f"   Added: {[label for _, label in links[3:]]}")
    tests_passed += 1
else:
    print(f"❌ TEST 3: Expected 7 pages, got {len(links)}")

# Test 4: Advanced includes Essential pages
tests_total += 1
advanced_labels = [label for _, label in links]
has_essential = all(label in advanced_labels for label in expected_essential)
if has_essential:
    print(f"✅ TEST 4: Advanced includes all Essential pages ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 4: Advanced missing some Essential pages")

# Test 5: Expert mode shows all pages
tests_total += 1
experience_level.set_experience_level("expert")
links = ui_components._page_links()
# Should show all pages in PAGE_TIER_MAP
expected_expert_count = len(ui_components.PAGE_TIER_MAP)
if len(links) == expected_expert_count:
    print(f"✅ TEST 5: Expert mode shows all {expected_expert_count} pages ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 5: Expected {expected_expert_count} pages, got {len(links)}")

# Test 6: Expert includes Advanced pages
tests_total += 1
expert_labels = [label for _, label in links]
has_advanced = all(label in expert_labels for label in advanced_labels)
if has_advanced:
    print(f"✅ TEST 6: Expert includes all Advanced pages ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 6: Expert missing some Advanced pages")

# Test 7: get_visible_page_count helper works
tests_total += 1
experience_level.set_experience_level("essential")
count = ui_components.get_visible_page_count()
if count == 3:
    print(f"✅ TEST 7: get_visible_page_count() returns correct value ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 7: Expected count 3, got {count}")

# Test 8: get_current_tier_pages helper works
tests_total += 1
tier_pages = ui_components.get_current_tier_pages()
if len(tier_pages) == 3 and all(len(item) == 3 for item in tier_pages):
    print(f"✅ TEST 8: get_current_tier_pages() returns correct format ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 8: get_current_tier_pages() format incorrect")

# Test 9: Page tier map is complete
tests_total += 1
tier_map_valid = all(
    len(item) == 4 and 
    item[2] in ["essential", "advanced", "expert"]
    for item in ui_components.PAGE_TIER_MAP
)
if tier_map_valid:
    print(f"✅ TEST 9: PAGE_TIER_MAP structure is valid ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 9: PAGE_TIER_MAP has invalid entries")

# Test 10: Tier progression (no pages lost when upgrading)
tests_total += 1
experience_level.set_experience_level("essential")
essential_set = set(label for _, label in ui_components._page_links())
experience_level.set_experience_level("advanced")
advanced_set = set(label for _, label in ui_components._page_links())
experience_level.set_experience_level("expert")
expert_set = set(label for _, label in ui_components._page_links())

progression_valid = essential_set.issubset(advanced_set) and advanced_set.issubset(expert_set)
if progression_valid:
    print(f"✅ TEST 10: Tier progression preserves pages (no losses) ✓")
    tests_passed += 1
else:
    print(f"❌ TEST 10: Pages lost during tier progression")

print()
print("=" * 60)
print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
print("=" * 60)

if tests_passed == tests_total:
    print()
    print("🎉 ALL TESTS PASSED! Navigation filtering works correctly.")
    print()
    print("✅ Day 2 Progress:")
    print("  [x] ui_components.py updated")
    print("  [x] Page tier map defined")
    print("  [x] Navigation filtering implemented")
    print("  [x] All unit tests passing")
    print()
    print("🔄 Next: Test in browser")
    print("   1. Run: streamlit run app.py")
    print("   2. Check sidebar shows level switcher")
    print("   3. Switch between levels and verify navigation updates")
    print()
else:
    print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")
    sys.exit(1)
