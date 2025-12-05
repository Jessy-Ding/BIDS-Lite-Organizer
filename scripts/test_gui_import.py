#!/usr/bin/env python3
"""
Test script for GUI import and basic initialization.
Used by GitHub Actions workflow for cross-platform testing.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Test imports
try:
    import tkinter as tk
    print('✅ tkinter imported successfully')
    
    # Test if GUI module can be imported
    from ui import app
    print('✅ GUI module imported successfully')
    
    # Test if we can create a Tk root (without showing window)
    root = tk.Tk()
    root.withdraw()  # Hide window
    print('✅ Tk root created successfully')
    
    # Test if BIDSLiteApp can be instantiated
    app_instance = app.BIDSLiteApp(root)
    print('✅ BIDSLiteApp instantiated successfully')
    
    root.destroy()
    print('✅ All GUI tests passed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

