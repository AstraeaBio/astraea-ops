@echo off
REM Analysis Architect - Quick Launcher for Windows
REM Double-click this file to start the web UI

echo.
echo ========================================
echo   Analysis Architect - Project Tracker
echo ========================================
echo.
echo Starting web UI...
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run project_tracker_ui.py

pause
