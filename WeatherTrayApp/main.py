"""
Weather Tray App — Entry Point
A lightweight weather application that lives in the Windows system tray.

Features:
  - System tray icon showing current temperature
  - Click to see detailed weather panel
  - Auto-refreshes every 30 minutes
  - Change city, toggle C/F from right-click menu
  - 100% free — uses Open-Meteo API (no API key needed)

Usage:
  python main.py
"""

import sys
import os

# Ensure the script directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tray_app import run


def main():
    print("=" * 45)
    print("  Weather Tray App")
    print("  Free weather in your system tray 24/7")
    print("=" * 45)
    print()
    print("  Left-click tray icon  -> Weather panel")
    print("  Right-click tray icon -> Menu")
    print("  Hover over tray icon  -> Quick info")
    print()
    print("Starting...")
    print()

    try:
        run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
