
import json
from pathlib import Path
import config

def get_settings_file():
    """Return path to user settings JSON file."""
    return Path(config.get_data_path()) / "user_settings.json"

def load_settings():
    """Load settings from disk."""
    path = get_settings_file()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def get_setting(section, key, default=None):
    """Get a setting value by section and key."""
    settings = load_settings()
    return settings.get(section, {}).get(key, default)

def save_setting(section, key, value):
    """Save a setting value."""
    settings = load_settings()
    if section not in settings:
        settings[section] = {}
    settings[section][key] = value
    try:
        get_settings_file().write_text(json.dumps(settings, indent=2))
    except Exception:
        pass

def should_show_feature(feature_key: str) -> bool:
    """
    Check if a UI feature should be shown based on user settings.
    Default is True for most features unless explicitly disabled.
    """
    settings = load_settings()
    # Check specific feature flag relative to "features" section if exists
    # Or just check top-level for now
    features = settings.get("features", {})
    return features.get(feature_key, True)
