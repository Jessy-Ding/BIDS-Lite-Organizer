#!/bin/bash
# BIDS Lite Organizer - GUI Launcher for Linux/macOS
# This script launches the GUI application on Linux or macOS

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Run the GUI
python3 run_gui.py

# If it fails, show helpful message
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Could not start GUI."
    echo "Please make sure Python 3 is installed and dependencies are installed:"
    echo "  pip3 install -r requirements.txt"
    echo ""
    echo "On Linux, you may also need to install tkinter:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  Arch: sudo pacman -S tk"
fi

