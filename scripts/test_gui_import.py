#!/usr/bin/env python3
"""
Test script for GUI import and basic initialization.
Used by GitHub Actions workflow for cross-platform testing.
"""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Test imports
try:
    import tkinter as tk
    print('[OK] tkinter imported successfully')
    
    # Test if GUI module can be imported
    from ui import app
    print('[OK] GUI module imported successfully')
    
    # Set up virtual display for headless environments (Linux)
    if sys.platform == 'linux' and 'DISPLAY' not in os.environ:
        # Try to use a virtual display if available
        os.environ['DISPLAY'] = ':99'
    
    # Test if we can create a Tk root (without showing window)
    # Use a try-except to handle display issues gracefully
    try:
        root = tk.Tk()
        root.withdraw()  # Hide window
        print('[OK] Tk root created successfully')
        
        # Test if BIDSLiteApp can be instantiated
        app_instance = app.BIDSLiteApp(root)
        print('[OK] BIDSLiteApp instantiated successfully')
        
        root.destroy()
        print('[OK] All GUI tests passed!')
    except tk.TclError as e:
        if 'no display' in str(e).lower() or 'display' in str(e).lower():
            print('[WARN] Cannot create GUI window in headless environment')
            print('[INFO] GUI module imports work correctly, but display is not available')
            print('[INFO] This is expected in CI environments without a display server')
            # In CI, we consider import success as a pass
            print('[OK] GUI import test passed (headless mode)')
        else:
            raise
    
except Exception as e:
    print(f'[ERROR] Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Workflow trigger
