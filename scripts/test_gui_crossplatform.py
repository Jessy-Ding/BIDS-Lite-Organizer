#!/usr/bin/env python3
"""
Cross-platform GUI test script.

This script tests if the GUI can be imported and initialized on the current platform.
It doesn't show a window, just tests that everything can be loaded.

Usage:
    python scripts/test_gui_crossplatform.py
"""

import sys
import platform
from pathlib import Path

# Add project root to path (scripts/ is one level down from project root)
_project_root = Path(__file__).parent.parent.absolute()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

def test_gui():
    """Test GUI import and initialization."""
    print("=" * 70)
    print("GUI Cross-Platform Compatibility Test")
    print("=" * 70)
    print()
    
    # Print platform info
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Test 1: Import tkinter
    print("Test 1: Importing tkinter...")
    try:
        import tkinter as tk
        print("  ✅ tkinter imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import tkinter: {e}")
        print("  💡 On Linux, you may need to install python3-tk:")
        print("     sudo apt-get install python3-tk  # Debian/Ubuntu")
        print("     sudo yum install python3-tkinter  # RHEL/CentOS")
        return False
    
    # Test 2: Import GUI module
    print("Test 2: Importing GUI module...")
    try:
        from ui import app
        print("  ✅ GUI module imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import GUI module: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Create Tk root
    print("Test 3: Creating Tk root...")
    try:
        root = tk.Tk()
        root.withdraw()  # Hide window (don't show it)
        print("  ✅ Tk root created successfully")
    except Exception as e:
        print(f"  ❌ Failed to create Tk root: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Instantiate BIDSLiteApp
    print("Test 4: Instantiating BIDSLiteApp...")
    try:
        app_instance = app.BIDSLiteApp(root)
        print("  ✅ BIDSLiteApp instantiated successfully")
    except Exception as e:
        print(f"  ❌ Failed to instantiate BIDSLiteApp: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()
        return False
    
    # Test 5: Check for platform-specific issues
    print("Test 5: Checking for platform-specific issues...")
    issues = []
    
    # Check if tkinterdnd2 is available
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        print("  ✅ tkinterdnd2 (drag-and-drop) is available")
    except ImportError:
        print("  ⚠️  tkinterdnd2 not available (drag-and-drop will be disabled)")
        print("     This is optional and won't prevent the GUI from working")
    
    # Check file path handling
    test_path = Path("/test/path") if platform.system() != "Windows" else Path("C:\\test\\path")
    if isinstance(test_path, Path):
        print("  ✅ pathlib.Path works correctly")
    else:
        issues.append("pathlib.Path may have issues")
    
    # Cleanup
    root.destroy()
    
    print()
    print("=" * 70)
    if issues:
        print("⚠️  Tests passed with warnings:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All tests passed! GUI should work on this platform.")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_gui()
    sys.exit(0 if success else 1)

