# Quick Start Guide

## Problem: externally-managed-environment

If you encounter this error when trying to install packages:
```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
```

**Don't worry!** This is a security feature in modern Debian/Ubuntu-based systems (including Raspberry Pi OS).

## Solution: Use a Virtual Environment

A virtual environment creates an isolated Python installation where you can safely install packages without affecting system packages.

### Method 1: Automatic Installation (Recommended)

Simply run the installation script:

```bash
./install.sh
```

This will:
1. Create a virtual environment in the `venv` directory
2. Install all required Python packages
3. Create necessary directories

### Method 2: Manual Installation

If you prefer to do it manually:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create directories
mkdir -p models/wakewords/sv models/vosk-model-sv models/piper-sv audio_feedback
```

## Using the Virtual Environment

**Important:** You need to activate the virtual environment every time you want to use the application:

```bash
# Activate virtual environment (do this in every new terminal session)
source venv/bin/activate

# Your prompt will change to show (venv) at the beginning
# Example: (venv) user@raspberrypi:~/genio-bot-v2$

# Now you can run the application
python3 setup_wizard.py
python3 main.py
```

## Verifying Your Installation

After activating the virtual environment, verify everything is working:

```bash
# Activate virtual environment
source venv/bin/activate

# Check Python version
python3 --version

# Check pip location (should be inside venv)
which pip

# List installed packages
pip list
```

If `which pip` shows a path like `/path/to/genio-bot-v2/venv/bin/pip`, you're using the virtual environment correctly!

### Quick Test

Run the test script to verify everything is set up correctly:

```bash
./test_installation.sh
```

This will check that:
- Virtual environment exists
- Python is available
- pip is using the virtual environment
- All required packages are installed

## Deactivating the Virtual Environment

When you're done:

```bash
deactivate
```

## Why Not Use --break-system-packages?

While you could use `pip install --break-system-packages`, this is **not recommended** because:
- It can break system packages
- It makes system management harder
- Updates might conflict with system packages
- It goes against Python's best practices

Virtual environments are the **proper and recommended** way to manage Python projects.

## Troubleshooting

### "python3: No module named venv"

Install the venv module:
```bash
sudo apt install python3-venv
```

### "python3-venv is not available"

Install python3-full:
```bash
sudo apt install python3-full
```

### Virtual environment already exists

If you want to recreate it:
```bash
rm -rf venv
./install.sh
```

## Additional Resources

- [Python Virtual Environments (official docs)](https://docs.python.org/3/library/venv.html)
- [PEP 668 - Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)
