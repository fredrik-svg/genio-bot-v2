#!/bin/bash
# Test script to verify virtual environment setup
# This script helps verify that the installation is working correctly

set -e

echo "=================================================="
echo "  🧪 Testing Virtual Environment Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if venv directory exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "Please run './install.sh' first"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment directory exists${NC}"

# Activate virtual environment
source venv/bin/activate

# Check Python is available
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python is available: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

# Check pip is in venv
PIP_PATH=$(which pip)
if [[ "$PIP_PATH" == *"venv"* ]]; then
    echo -e "${GREEN}✓ pip is using virtual environment: ${PIP_PATH}${NC}"
else
    echo -e "${YELLOW}⚠ pip might not be using virtual environment: ${PIP_PATH}${NC}"
fi

# Check if requirements are installed
echo ""
echo "Checking installed packages..."
REQUIRED_PACKAGES=("paho-mqtt" "pvporcupine" "vosk" "piper-tts" "pyaudio" "soundfile" "numpy" "python-dotenv")
ALL_INSTALLED=true

for package in "${REQUIRED_PACKAGES[@]}"; do
    if pip show "$package" &> /dev/null; then
        echo -e "${GREEN}✓ ${package} is installed${NC}"
    else
        echo -e "${RED}✗ ${package} is NOT installed${NC}"
        ALL_INSTALLED=false
    fi
done

echo ""
if [ "$ALL_INSTALLED" = true ]; then
    echo -e "${GREEN}=================================================="
    echo "  ✅ All tests passed!"
    echo "==================================================${NC}"
    echo ""
    echo "Your installation is ready! Next steps:"
    echo "  1. Run setup wizard: python3 setup_wizard.py"
    echo "  2. Download required models (see README.md)"
    echo "  3. Start application: python3 main.py"
else
    echo -e "${YELLOW}=================================================="
    echo "  ⚠ Some packages are missing"
    echo "==================================================${NC}"
    echo ""
    echo "Try running: pip install -r requirements.txt"
fi

# Deactivate virtual environment
deactivate
