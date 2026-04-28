#!/bin/bash
set -e

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install Python 3.10+ and try again."
    exit 1
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt --quiet

echo
echo "Bootstrap complete. Run 'python -m cli.main init' to configure the project."