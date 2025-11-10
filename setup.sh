#!/bin/bash

# MammoViewer - Setup Script
# Automates the installation and configuration process

set -e

echo "================================================"
echo "MammoViewer - Setup"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python
else
    echo -e "${RED}✗ Python not found!${NC}"
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    exit 1
fi

# Check pip
echo ""
echo "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip is installed${NC}"
    PIP_CMD=pip3
elif command -v pip &> /dev/null; then
    echo -e "${GREEN}✓ pip is installed${NC}"
    PIP_CMD=pip
else
    echo -e "${RED}✗ pip not found!${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    fi
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
cd ..

# Create directories
echo ""
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p outputs
mkdir -p temp
mkdir -p logs
mkdir -p slicer_scripts
echo -e "${GREEN}✓ Directories created${NC}"

# Create .env file
echo ""
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from template${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and update SLICER_PATH${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
fi

# Detect 3D Slicer
echo ""
echo "Searching for 3D Slicer installation..."
SLICER_FOUND=false

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [ -f "/Applications/Slicer.app/Contents/MacOS/Slicer" ]; then
        SLICER_PATH="/Applications/Slicer.app/Contents/MacOS/Slicer"
        SLICER_FOUND=true
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    SLICER_LOCATIONS=(
        "/usr/local/Slicer-*/Slicer"
        "$HOME/Slicer-*/Slicer"
    )
    for loc in "${SLICER_LOCATIONS[@]}"; do
        if ls $loc 1> /dev/null 2>&1; then
            SLICER_PATH=$(ls $loc | head -1)
            SLICER_FOUND=true
            break
        fi
    done
fi

if [ "$SLICER_FOUND" = true ]; then
    echo -e "${GREEN}✓ Found 3D Slicer at: $SLICER_PATH${NC}"
    
    # Update config.py
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sed -i.bak "s|SLICER_PATH = .*|SLICER_PATH = os.environ.get('SLICER_PATH', '$SLICER_PATH')|" backend/config.py
        rm backend/config.py.bak
        echo -e "${GREEN}✓ Updated config.py with Slicer path${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 3D Slicer not found automatically${NC}"
    echo "Please install 3D Slicer from: https://download.slicer.org/"
    echo "Then update SLICER_PATH in backend/config.py"
fi

# Test configuration
echo ""
echo "Testing configuration..."
cd backend
$PYTHON_CMD config.py
cd ..

# Final instructions
echo ""
echo "================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. If 3D Slicer path wasn't auto-detected:"
echo "   Edit backend/config.py and set SLICER_PATH"
echo ""
echo "2. Start the application:"
echo "   cd backend"
echo "   python app.py"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:5000"
echo ""
echo "4. For detailed instructions, see:"
echo "   - QUICKSTART.md"
echo "   - README.md"
echo ""
echo "================================================"
echo ""

# Ask to start server
read -p "Start the server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting server..."
    echo "Press Ctrl+C to stop"
    echo ""
    cd backend
    $PYTHON_CMD app.py
fi