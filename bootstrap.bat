@echo off

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Install Python 3.10+ and try again.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo Bootstrap complete. Run "python -m cli.main init" to configure the project.
pause