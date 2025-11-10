#!/bin/bash

# MammoViewer Setup Script for Linux/macOS
# This script automates the installation and configuration of MammoViewer

set -e  # Exit on error

echo "============================================"
echo "  MammoViewer - DICOM to STL Converter"
echo "  Setup Script v1.0"
echo "============================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "  $1"
}

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python $PYTHON_VERSION is too old"
    print_info "Python 3.8 or higher is required"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check pip
echo ""
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi
print_success "pip is installed"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take several minutes..."
pip install -r backend/requirements.txt --quiet
if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p uploads outputs temp logs slicer_scripts
print_success "Directories created"

# Check for 3D Slicer
echo ""
echo "Checking for 3D Slicer installation..."

SLICER_FOUND=0
SLICER_PATH=""

# Common Slicer locations
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    COMMON_PATHS=(
        "/Applications/Slicer.app/Contents/MacOS/Slicer"
        "$HOME/Applications/Slicer.app/Contents/MacOS/Slicer"
    )
else
    # Linux
    COMMON_PATHS=(
        "/opt/Slicer/Slicer"
        "/usr/local/Slicer/Slicer"
        "$HOME/Slicer/Slicer"
    )
fi

for path in "${COMMON_PATHS[@]}"; do
    if [ -f "$path" ]; then
        SLICER_PATH="$path"
        SLICER_FOUND=1
        break
    fi
done

if [ $SLICER_FOUND -eq 1 ]; then
    print_success "3D Slicer found at: $SLICER_PATH"
else
    print_warning "3D Slicer not found in common locations"
    print_info "You will need to install 3D Slicer and set SLICER_PATH in .env"
    print_info "Download from: https://www.slicer.org/"
fi

# Create .env file if it doesn't exist
echo ""
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env

    # Set Slicer path if found
    if [ $SLICER_FOUND -eq 1 ]; then
        # Escape special characters in path
        ESCAPED_PATH=$(echo "$SLICER_PATH" | sed 's/[\/&]/\\&/g')

        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|#SLICER_PATH=/Applications/Slicer.app/Contents/MacOS/Slicer|SLICER_PATH=$ESCAPED_PATH|" .env
        else
            sed -i "s|#SLICER_PATH=/opt/Slicer/Slicer|SLICER_PATH=$ESCAPED_PATH|" .env
        fi
    fi

    print_success ".env file created"
    print_info "Please review and customize .env as needed"
else
    print_warning ".env file already exists, skipping"
fi

# Test installation
echo ""
echo "Testing installation..."
python3 test_installation.py
if [ $? -eq 0 ]; then
    print_success "Installation test passed"
else
    print_warning "Installation test had some warnings"
fi

# Summary
echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo ""

if [ $SLICER_FOUND -eq 0 ]; then
    echo "2. Install 3D Slicer from https://www.slicer.org/"
    echo ""
    echo "3. Set SLICER_PATH in .env file:"
    echo "   ${GREEN}nano .env${NC}"
    echo ""
    echo "4. Start the application:"
else
    echo "2. Start the application:"
fi
echo "   ${GREEN}python backend/app.py${NC}"
echo ""
echo "5. Open your browser:"
echo "   ${GREEN}http://localhost:5000${NC}"
echo ""
echo "For more information, see README.md and QUICKSTART.md"
echo ""
echo "============================================"
