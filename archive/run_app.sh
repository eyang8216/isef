#!/bin/bash
# Install the solver package and run Streamlit app
# Run this on your Mac Terminal

cd ~/Desktop/isef

echo "=========================================="
echo "Installing Solver Package and Running App"
echo "=========================================="

echo ""
echo "Step 1: Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "Step 2: Installing solver package in editable mode..."
pip install -e .
echo "✓ Solver package installed"

echo ""
echo "Step 3: Launching Streamlit app..."
echo ""
echo "The app will open in your browser with two tabs:"
echo "  - Classic: Original solver"
echo "  - Immersed verification: Free-boundary verification results"
echo ""
streamlit run app/streamlit_app.py
