"""Configuration constants for drill scoring and validation"""
from pathlib import Path

# Scoring weights
SCORE_DIFFICULTY_MATCH = 30
SCORE_DIFFICULTY_MISMATCH = -15
SCORE_RECENCY_LAST_SESSION = -50
SCORE_RECENCY_TWO_SESSIONS = -25
SCORE_INTENSITY_MATCH = 20
SCORE_INTENSITY_ONE_OFF = -10
SCORE_INTENSITY_TWO_OFF = -30

# Player tolerance for drill selection
PLAYER_TOLERANCE = 2

# Valid options
DIFFICULTY_LEVELS = ['beginner', 'intermediate', 'advanced']
INTENSITY_LEVELS = ['low', 'medium', 'high']
CATEGORIES = ['Warmup', 'Technical', 'Tactical', 'Small Sided Games', 'Conditioning', 'Cool Down']
EQUIPMENT_TYPES = ['Cones', 'Balls', 'Pinnies', 'Goals', 'Agility Ladder', 'None']
DRILL_TAGS = [
    'Finishing',
    'Passing',
    'Dribbling',
    'Transition',
    'Defending',
    'Conditioning',
    'Positioning',
    '1v1',
    '2v2',
    'Set Pieces'
]
TEAM_PLAY_STYLES = [
    'Possession',
    'Direct Play',
    'Counter Attacking',
    'High Press',
    'Low Block',
    'Wing Focus',
    'Build From Back'
]
TEAM_SEASON_OBJECTIVES = [
    'Player Development',
    'Win League',
    'Top 3 Finish',
    'Tournament Prep',
    'Stay Competitive',
    'Rebuild Season'
]
SEASON_SEGMENTS = [
    'Preseason',
    'Early Season',
    'Mid Season',
    'Late Season',
    'Postseason'
]

# Mode flags (safe defaults for players)
COACH_MODE = True
DEV_MODE = False
# Demo mode — set to True before a partner/beta demo, False after.
# When True, all pages read from data/demo/ instead of data/production/.
# Run scripts/seed_demo.py to reset demo data to a known state.
DEMO_MODE = False

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / 'assets'
DIAGRAMS_DIR = ASSETS_DIR / 'diagrams'
DATA_DIR = PROJECT_ROOT / 'data'
DEMO_DATA_DIR = DATA_DIR / 'demo'
PRODUCTION_DATA_DIR = DATA_DIR / 'production'
SEED_DRILLS_FILE = DEMO_DATA_DIR / 'drill_library.csv'

# Toggle dev-only tools (diagram generator, etc.)
DEV_TOOLS = DEV_MODE
DEVELOPER_MODE = DEV_MODE
# Default user-facing mode
DEFAULT_USER_MODE = "coach"  # "coach" or "developer"


def get_data_path():
    """Return data path based on DEMO_MODE flag."""
    path = DEMO_DATA_DIR if DEMO_MODE else PRODUCTION_DATA_DIR
    return path if path.exists() else DEMO_DATA_DIR


def is_dev() -> bool:
    """Whether the app is running with developer tooling enabled."""
    return DEV_MODE


def is_demo() -> bool:
    """Whether the app should read from demo data paths."""
    return DEMO_MODE


# Pending changes staging file (mirrors other CSV/JSON storage locations)
PENDING_CHANGES_FILE = get_data_path() / 'pending_changes.json'


def get_diagram_file(diagram_path):
    """
    Resolve a diagram path to an absolute Path.
    """
    if not diagram_path:
        return None
    candidate = Path(diagram_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / diagram_path
    return candidate


def get_seed_drills_path() -> Path:
    """
    Return the path to the shipped starter drill library CSV.

    Defaults to the demo drill library bundled in the repo.
    """
    return SEED_DRILLS_FILE

