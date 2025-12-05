#!/usr/bin/env python3
"""
BIDS Lite Organizer - GUI Launcher
Cross-platform launcher script for the GUI application.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Launch the GUI
if __name__ == "__main__":
    try:
        from ui.app import run_app
        run_app()
    except ImportError as e:
        print("Error: Could not import GUI module.")
        print(f"Details: {e}")
        print("\nPlease make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

