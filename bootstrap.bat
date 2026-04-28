@echo off

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Install Python 3.10+ and try again.
    exit /b 1
)

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo.
echo Bootstrap complete. Run "python -m cli.main init" to configure the project.