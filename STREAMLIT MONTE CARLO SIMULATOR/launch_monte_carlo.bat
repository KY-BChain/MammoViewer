@echo off
REM Monte Carlo Streamlit Application - Quick Start Script (Windows)
REM Run this script to automatically set up and launch the application

echo ==========================================
echo 🎲 MONTE CARLO SIMULATION APP
echo Quick Start Installation ^& Launch
echo ==========================================
echo.

REM Check Python version
echo 📋 Checking Python version...
python --version

if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Install dependencies
echo 📦 Installing dependencies...
echo.

pip install streamlit numpy pandas plotly scipy

if %errorlevel% neq 0 (
    echo ❌ Package installation failed
    pause
    exit /b 1
)

echo.
echo ✓ All packages installed
echo.

REM Launch application
echo 🚀 Launching Monte Carlo Simulation Application...
echo.
echo The app will open in your default browser at:
echo 👉 http://localhost:8501
echo.
echo To stop the app: Press Ctrl+C in this terminal
echo.
echo ==========================================
echo.

streamlit run monte_carlo_streamlit_app.py

pause
