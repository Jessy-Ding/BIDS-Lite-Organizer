#!/usr/bin/env python3
"""
BIDS Lite Organizer - GUI Launcher
Cross-platform launcher script for the GUI application.

Usage:
    python run_gui.py          # Launch the GUI
    python run_gui.py --help  # Show this help message
    python run_gui.py --test   # Test imports without launching GUI
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def show_help():
    """Display help message."""
    print(__doc__)
    print("\nRequirements:")
    print("  - Python 3.9 or higher")
    print("  - Dependencies: pip install -r requirements.txt")
    print("\nPlatform-specific notes:")
    print("  - Windows: Usually works out of the box")
    print("  - Linux: May need: sudo apt-get install python3-tk")
    print("  - macOS: Usually works out of the box")
    print("\nAlternative launch methods:")
    print("  - Direct: python ui/app.py")
    print("  - As module: python -m ui.app")

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    try:
        import tkinter as tk
        print("  ✓ tkinter")
    except ImportError as e:
        print(f"  ✗ tkinter: {e}")
        print("    On Linux, install: sudo apt-get install python3-tk")
        return False
    
    try:
        from ui import app
        print("  ✓ ui.app")
    except ImportError as e:
        print(f"  ✗ ui.app: {e}")
        print("    Make sure you're in the project root directory")
        return False
    
    try:
        from bids_lite import cli
        print("  ✓ bids_lite.cli")
    except ImportError as e:
        print(f"  ✗ bids_lite.cli: {e}")
        return False
    
    print("\n✓ All imports successful!")
    return True

def test_gui_launch():
    """Test if GUI can actually launch (creates window then closes immediately)."""
    print("\nTesting GUI launch...")
    try:
        import tkinter as tk
        from ui import app
        
        # Try to create GUI window
        print("  Creating GUI window...")
        if app.DND_AVAILABLE and app.TkinterDnD:
            root = app.TkinterDnD.Tk()
        else:
            root = tk.Tk()
        
        root.withdraw()  # Hide window immediately
        print("  ✓ Window created")
        
        # Try to instantiate the app
        print("  Initializing BIDSLiteApp...")
        app_instance = app.BIDSLiteApp(root)
        print("  ✓ BIDSLiteApp initialized")
        
        # Close window immediately
        root.destroy()
        print("  ✓ Window closed")
        
        print("\n✓ GUI launch test successful!")
        print("  The GUI should work correctly when you run it.")
        return True
        
    except tk.TclError as e:
        if 'no display' in str(e).lower() or 'display' in str(e).lower():
            print(f"  ⚠ Display not available: {e}")
            print("  This is normal in headless environments (like SSH).")
            print("  GUI should work when you have a display available.")
            return True  # Not a failure, just no display
        else:
            print(f"  ✗ TclError: {e}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Launch the GUI
if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
            sys.exit(0)
        elif sys.argv[1] in ['--test', '-t', 'test']:
            # Test imports first
            if not test_imports():
                sys.exit(1)
            # Then test GUI launch
            if not test_gui_launch():
                sys.exit(1)
            sys.exit(0)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    
    # Launch GUI
    try:
        from ui.app import run_app
        run_app()
    except ImportError as e:
        print("Error: Could not import GUI module.")
        print(f"Details: {e}")
        print("\nPlease make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        print("\nRun with --test to check imports, or --help for more info.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

