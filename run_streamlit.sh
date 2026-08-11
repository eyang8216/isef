#!/bin/bash
# Properly run the Streamlit app with the correct Python environment

cd ~/Desktop/isef

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Install dependencies
echo "Installing dependencies..."
.venv/bin/pip install -e ".[dev,app]" -q
echo "✓ Dependencies installed"

# Run streamlit using the venv's python
echo ""
echo "Starting Streamlit app..."
echo "The app will open at: http://localhost:8501"
echo ""
.venv/bin/streamlit run app/streamlit_app.py
