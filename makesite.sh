#!/usr/bin/sh

VENV="venv"

if [ -d "$VENV" ]; then
    # Activate the existing virtual environment
    source venv/bin/activate
else
    python3 -m venv venv || python -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip || python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt || pip install -r requirements.txt
fi
python3 makesite.py || python makesite.py
python3 -m http.server -d _site || python -m http.server -d _site

