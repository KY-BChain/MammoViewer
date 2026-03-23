#!/bin/bash
# Monte Carlo Streamlit Application - Quick Start Script
# Run this script to automatically set up and launch the application

echo "=========================================="
echo "🎲 MONTE CARLO SIMULATION APP"
echo "Quick Start Installation & Launch"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo ""

pip3 install --quiet streamlit numpy pandas plotly scipy

if [ $? -ne 0 ]; then
    echo "❌ Package installation failed"
    exit 1
fi

echo ""
echo "✓ All packages installed"
echo ""

# Launch application
echo "🚀 Launching Monte Carlo Simulation Application..."
echo ""
echo "The app will open in your default browser at:"
echo "👉 http://localhost:8501"
echo ""
echo "To stop the app: Press Ctrl+C in this terminal"
echo ""
echo "=========================================="
echo ""

streamlit run monte_carlo_streamlit_app.py
