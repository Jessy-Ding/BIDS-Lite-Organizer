@echo off
REM BIDS Lite Organizer - GUI Launcher for Windows
REM This script launches the GUI application on Windows

python run_gui.py
if errorlevel 1 (
    echo.
    echo Error: Could not start GUI.
    echo Please make sure Python is installed and dependencies are installed:
    echo   pip install -r requirements.txt
    pause
)

