# Cross-Platform GUI Testing Guide

This document explains how to test the GUI's cross-platform compatibility.

## Quick Test (On Your Current Platform)

Run the test script:

```bash
python scripts/test_gui_crossplatform.py
```

This will test if the GUI can be imported and initialized on your current platform.

## Automated Testing with GitHub Actions

We have set up GitHub Actions workflows that automatically test the GUI on:
- **Windows** (windows-latest)
- **Linux** (ubuntu-latest)
- **macOS** (macos-latest)

The workflow file is located at `.github/workflows/test_gui_crossplatform.yml`.

### How It Works

1. **Automatic Testing**: The workflow runs automatically on:
   - Every push to `main` or `master` branch
   - Every pull request
   - Manual trigger (workflow_dispatch)

2. **What It Tests**:
   - GUI module can be imported
   - Tkinter can create a root window
   - BIDSLiteApp can be instantiated
   - CLI still works (core functionality)

3. **View Results**: 
   - Go to the "Actions" tab in your GitHub repository
   - Click on the latest workflow run
   - Check if all platforms passed

## Manual Testing Methods

### Method 1: Virtual Machine (Most Reliable)

If you have a Windows license, you can use a virtual machine:

1. **Install VirtualBox** (free):
   ```bash
   brew install --cask virtualbox
   ```

2. **Download Windows ISO** from Microsoft

3. **Create VM and Install Windows**

4. **Test GUI**:
   ```powershell
   # In Windows VM
   python -m pip install -r requirements.txt
   python ui/app.py
   ```

### Method 2: Ask Windows Users to Test

1. Add a note in README asking Windows users to test
2. Provide clear instructions
3. Create an issue template for bug reports
4. Welcome feedback

### Method 3: Code Review

Check for platform-specific code:

- **Path handling**: Uses `pathlib.Path` (cross-platform)
- **File dialogs**: Uses `tkinter.filedialog` (cross-platform)
- **Drag-and-drop**: Uses `tkinterdnd2` (supports Windows and macOS)
- **Mouse wheel**: Has platform-specific bindings (Button-4/5 for macOS)

## Known Platform-Specific Considerations

### Windows

- **tkinter**: Included with Python, should work out of the box
- **tkinterdnd2**: Should work, but may need installation
- **File dialogs**: Should work, but `filetypes` parameter format may differ

### Linux

- **tkinter**: May need to install `python3-tk`:
  ```bash
  sudo apt-get install python3-tk  # Debian/Ubuntu
  sudo yum install python3-tkinter  # RHEL/CentOS
  ```
- **tkinterdnd2**: May have limited support

### macOS

- **tkinter**: Included with Python, should work
- **tkinterdnd2**: Works well
- **File dialogs**: Some issues with `filetypes` parameter (we removed it to avoid crashes)

## Testing Checklist

When testing on a new platform, check:

- [ ] GUI launches without errors
- [ ] All buttons are clickable
- [ ] File dialogs work (Browse buttons)
- [ ] Drag-and-drop works (if tkinterdnd2 is installed)
- [ ] Scrolling works (scrollbar and mouse wheel)
- [ ] Validation works
- [ ] Plan (dry-run) works
- [ ] Apply works
- [ ] Phenotype files can be added
- [ ] Publication files can be added (derivatives only)

## Reporting Issues

If you find platform-specific issues:

1. **Create an issue** with:
   - Platform (Windows/Linux/macOS)
   - Python version
   - Error message or screenshot
   - Steps to reproduce

2. **Check existing issues** to see if it's already reported

3. **Test with CLI** to verify core functionality still works

## Current Status

- **macOS**: Fully tested and working
- **Windows**: Should work (tkinter is cross-platform), but not manually tested
- **Linux**: Should work (tkinter is cross-platform), but not manually tested

**Recommendation**: Use CLI on Windows/Linux if GUI has issues. CLI is fully cross-platform and feature-complete.

