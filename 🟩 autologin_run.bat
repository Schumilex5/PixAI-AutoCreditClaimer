@echo off
REM ============================================================
REM Run Python script using local .venv if present,
REM otherwise fall back to system Python.
REM ============================================================

cd /d "%~dp0"

REM --- CONFIG ---
set "VENV_PY=.venv\Scripts\python.exe"
set "SCRIPT=open_pixai.py"

REM --- CHECK FOR .venv PYTHON ---
if exist "%VENV_PY%" (
    echo ✅ Using virtual environment: %VENV_PY%
    "%VENV_PY%" "%SCRIPT%"
) else (
    echo ⚠️ No virtual environment found.
    echo 🔍 Trying to use system Python...

    where python >nul 2>nul
    if %errorlevel%==0 (
        echo ✅ Found system Python on PATH.
        python "%SCRIPT%"
    ) else (
        where py >nul 2>nul
        if %errorlevel%==0 (
            echo ✅ Found system Python launcher.
            py "%SCRIPT%"
        ) else (
            echo ❌ No Python found! Please install Python or create a virtual environment.
            pause
            exit /b
        )
    )
)

echo ------------------------------------------------------------
echo ✅ Script finished.
pause
