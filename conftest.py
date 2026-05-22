collect_ignore_glob = [
    "tests/test_day1_experience_level.py",
    "tests/test_day1_manual.py",
    "tests/test_day2_manual.py",
    "tests/test_day2_navigation.py",
    "tests/test_switch_level.py",
]


import shutil
import sys
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def tmp_path():
    """
    Use a workspace-safe temporary directory instead of pytest's default temp root.
    """
    base_dir = ROOT / "temp"
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"coach_ai_{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
