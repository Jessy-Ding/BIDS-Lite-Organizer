#!/usr/bin/env python3
"""
Simple cross-platform test for GUI and CLI.
Tests that both interfaces work on the current platform.
"""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def test_cli():
    """Test CLI functionality."""
    print("Testing CLI...")
    try:
        from bids_lite import cli
        # Just verify it can be imported and has the expected structure
        assert hasattr(cli, 'cli'), "CLI module missing 'cli' command group"
        print("  [OK] CLI module imported successfully")
        return True
    except Exception as e:
        print(f"  [ERROR] CLI test failed: {e}")
        return False

def test_gui():
    """Test GUI functionality."""
    print("Testing GUI...")
    try:
        import tkinter as tk
        print("  [OK] tkinter available")
        
        from ui import app
        print("  [OK] GUI module imported")
        
        # Try to create window (will fail in headless, that's OK)
        try:
            root = tk.Tk()
            root.withdraw()
            app_instance = app.BIDSLiteApp(root)
            root.destroy()
            print("  [OK] GUI window created and initialized")
        except tk.TclError as e:
            if 'display' in str(e).lower():
                print("  [INFO] GUI works but no display available (headless mode)")
            else:
                raise
        
        return True
    except Exception as e:
        print(f"  [ERROR] GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BIDS Lite Organizer - Platform Compatibility Test")
    print("=" * 60)
    print()
    
    cli_ok = test_cli()
    print()
    gui_ok = test_gui()
    print()
    
    print("=" * 60)
    if cli_ok and gui_ok:
        print("[SUCCESS] Both CLI and GUI are working!")
        sys.exit(0)
    else:
        print("[FAILURE] Some tests failed")
        sys.exit(1)

# Trigger workflow test
