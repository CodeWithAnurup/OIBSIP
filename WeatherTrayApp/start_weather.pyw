"""
Weather Tray App — Silent Launcher (no console window).
Double-click this file to start the weather app in the background.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tray_app import run

if __name__ == "__main__":
    run()
