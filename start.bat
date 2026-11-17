@echo off
title Kreditly
cd /d "%~dp0"
echo Starting Kreditly local app...
echo Opening browser at http://localhost:8501...
start "" "http://localhost:8501"
".venv\Scripts\streamlit.exe" run app.py --server.headless false
if errorlevel 1 (
    echo.
    echo Something went wrong while running Kreditly.
    pause
)
