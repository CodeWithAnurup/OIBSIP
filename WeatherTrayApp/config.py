"""
Configuration manager for Weather Tray App.
Saves/loads user preferences (city, refresh interval) to a JSON file.
"""

import json
import os

# Config file lives next to the script
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CONFIG_DIR, "weather_config.json")

DEFAULT_CONFIG = {
    "city": "Kolkata",
    "refresh_interval_minutes": 30,
    "temperature_unit": "celsius",  # "celsius" or "fahrenheit"
}


def load_config() -> dict:
    """Load configuration from JSON file, or return defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge with defaults so new keys are always present
            config = {**DEFAULT_CONFIG, **saved}
            return config
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Warning: Could not save config: {e}")
