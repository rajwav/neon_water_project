@echo off
setlocal enabledelayedexpansion
title AQUA NEON - Local Windows Launcher

echo ====================================================================
echo   AQUA NEON Water Intelligence Platform - Windows Setup & Launcher
echo ====================================================================
echo.

cd /d "%~dp0"

set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 --version >nul 2>nul
    if !errorlevel!==0 set "PY_CMD=py -3"
)
if "%PY_CMD%"=="" (
    where python >nul 2>nul
    if %errorlevel%==0 set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python 3.11+ was not found on PATH.
    echo Please install Python 3.11 or 3.12 from https://www.python.org/downloads/windows/
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PY_CMD% --version 2^>^&1') do echo [INFO] Found %%v

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment .venv ...
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment .venv already exists.
)

echo [2/3] Installing dependencies ^(first run may take 2-4 minutes^)...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>nul
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [WARN] Exact requirements.txt pin failed ^(likely Python ^< 3.11 for numpy==2.3.5^).
    echo [WARN] Retrying with unpinned numpy compatibility...
    ".venv\Scripts\python.exe" -c "txt=open('requirements.txt').read().replace('numpy==2.3.5','numpy'); open('requirements_win_tmp.txt','w').write(txt)"
    ".venv\Scripts\python.exe" -m pip install -r requirements_win_tmp.txt
    del /q requirements_win_tmp.txt >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

echo.
echo [3/3] Launching AQUA NEON Streamlit App at http://localhost:8501 ...
echo Keep this window open while presenting. Press Ctrl+C to stop.
echo.
".venv\Scripts\streamlit.exe" run app.py --server.port 8501 --browser.gatherUsageStats false
pause
