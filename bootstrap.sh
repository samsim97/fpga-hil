#!/bin/bash
set -e

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install Python 3.10+ and try again."
    read -p "Press Enter to close..."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo
echo "Bootstrap complete. Run 'python -m cli.main init' to configure the project."
read -p "Press Enter to close..."