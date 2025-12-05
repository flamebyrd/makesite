#!/bin/bash -x
cd "$(dirname "$0")"

VENV="venv"

if which python3 > /dev/null 2>&1; then
    PYTHON="python3"
else
    PYTHON="python"
fi

if [ -d "$VENV" ]; then
    # Activate the existing virtual environment
    source venv/bin/activate
else
    $PYTHON -m venv venv
    PIP="$VENV/bin/pip"
    source venv/bin/activate
    $PIP install -r requirements.txt
fi
PYTHON="$VENV/bin/python"
$PYTHON makesite.py
#$PYTHON -u -m http.server 8800 -d _site;