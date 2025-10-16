#!/bin/bash
# Installation script for rpi-n8n-voice-assistant
# This script sets up a Python virtual environment and installs dependencies

set -e  # Exit on error

echo "=================================================="
echo "  🤖 RPI-N8N Voice Assistant - Installation"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first:"
    echo "   sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python version: $PYTHON_VERSION"

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "❌ Python venv module is not installed. Please install it:"
    echo "   sudo apt install python3-venv"
    exit 1
fi

# Create virtual environment
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment already exists at '$VENV_DIR'"
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "ℹ️  Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created at '$VENV_DIR'"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p models/wakewords/sv
mkdir -p models/vosk-model-sv
mkdir -p models/piper-sv
mkdir -p audio_feedback
echo "✓ Directories created"

echo ""
echo "=================================================="
echo "  ✅ Installation completed successfully!"
echo "=================================================="
echo ""
echo "📋 Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the setup wizard to configure:"
echo "     python3 setup_wizard.py"
echo ""
echo "  3. Download required models:"
echo "     • Vosk (Swedish STT): https://alphacephei.com/vosk/models"
echo "     • Piper (Swedish TTS): https://github.com/rhasspy/piper#voices"
echo "     • Porcupine wakeword: https://picovoice.ai/platform/porcupine/"
echo ""
echo "  4. Start the application:"
echo "     python3 main.py"
echo ""
echo "🔒 Security note: The .env file will contain sensitive information."
echo "   Never commit it to Git - it's already in .gitignore"
echo ""
