#!/usr/bin/sh

VENV="venv"

if which python3 > /dev/null 2>&1; then
    PYTHON="python3"
    PIP="pip3"
else
    PYTHON="python"
    PIP="pip"
fi

if [ -d "$VENV" ]; then
    # Activate the existing virtual environment
    source venv/bin/activate
else
    $PYTHON -m venv venv
    source venv/bin/activate
    $PYTHON -m pip install --upgrade pip
    $PIP install -r requirements.txt
fi
$PYTHON makesite.py
$PYTHON -u -m http.server -d _site;