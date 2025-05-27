#!/bin/bash
# Setup script for Star Citizen Checkout Bot

echo "Setting up Star Citizen Checkout Bot..."

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "✓ Python 3 found"
    PYTHON="python3"
elif command -v python &>/dev/null; then
    # Check Python version
    PYTHON_VERSION=$(python --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1)
    if [ "$PYTHON_VERSION" -ge 3 ]; then
        echo "✓ Python 3 found"
        PYTHON="python"
    else
        echo "✗ Python 3 not found. Please install Python 3.6 or higher."
        exit 1
    fi
else
    echo "✗ Python not found. Please install Python 3.6 or higher."
    exit 1
fi

# Check for tkinter
echo "Checking for Tkinter (GUI library)..."
if ! $PYTHON -c "import tkinter" &> /dev/null; then
    echo "✗ Tkinter not found. This is needed for the graphical interface."
    echo
    echo "To install Tkinter:"
    echo "For macOS:"
    echo "1. Install Python from python.org"
    echo "2. Ensure 'tcl/tk and IDLE' is selected during installation"
    echo
    echo "For Linux (Ubuntu/Debian):"
    echo "  sudo apt-get install python3-tk"
    echo
    echo "For Linux (Fedora):"
    echo "  sudo dnf install python3-tkinter"
    echo
    echo "For Linux (Arch):"
    echo "  sudo pacman -S tk"
    echo
    echo "After installing Tkinter, run this setup again."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi
echo "✓ Tkinter found"

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON -m venv venv
if [ $? -ne 0 ]; then
    echo "✗ Failed to create virtual environment. Please install venv package."
    echo "  You can try: $PYTHON -m pip install virtualenv"
    exit 1
fi
echo "✓ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "✗ Failed to activate virtual environment."
    exit 1
fi
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."

# Upgrade pip first
echo "Upgrading pip..."
$PYTHON -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "✗ Failed to upgrade pip."
    exit 1
fi

# Install each critical dependency separately with verification
echo "Installing Selenium..."
pip install selenium
if [ $? -ne 0 ]; then
    echo "✗ Failed to install Selenium. Retrying with --no-cache-dir..."
    pip install --no-cache-dir selenium
    if [ $? -ne 0 ]; then
        echo "✗ Failed to install Selenium."
        exit 1
    fi
fi

echo "Installing other dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "✗ Failed to install some dependencies."
    echo "Trying alternative installation method..."
    pip install --no-cache-dir -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "✗ Failed to install dependencies."
        exit 1
    fi
fi

echo "✓ Dependencies installed"

# Verify critical packages
echo "Verifying installations..."
$PYTHON -c "import selenium" &>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Selenium installation verification failed."
    echo "Please try running setup again or install manually:"
    echo "pip install selenium"
    exit 1
fi
echo "✓ Selenium verified"

# Download WebDriver
echo "Do you want to download ChromeDriver? (y/n)"
read -r download_driver
if [[ "$download_driver" =~ ^[Yy]$ ]]; then
    echo "Installing webdriver-manager..."
    pip install webdriver-manager
    echo "Creating helper script to download driver automatically..."
    cat > download_driver.py << 'EOF'
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import sys

print("Downloading WebDriver...")
try:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "firefox":
        driver_path = GeckoDriverManager().install()
        print(f"Firefox WebDriver downloaded to: {driver_path}")
    else:
        driver_path = ChromeDriverManager().install()
        print(f"Chrome WebDriver downloaded to: {driver_path}")
    print("✓ WebDriver downloaded successfully")
except Exception as e:
    print(f"✗ Error downloading WebDriver: {str(e)}")
EOF
    
    echo "Downloading Chrome WebDriver..."
    python download_driver.py
    echo "✓ Setup complete with WebDriver"
else
    echo "Skipping WebDriver download. You will need to download it manually."
    echo "✓ Setup complete without WebDriver"
fi

echo ""
echo "==== SETUP COMPLETE ===="
echo ""
echo "To run the bot, use:"
echo "source venv/bin/activate  # Activate the virtual environment"
echo "python bot.py --username YOUR_USERNAME --password YOUR_PASSWORD --coupon YOUR_COUPON_CODE"
echo ""
echo "To run a test without making a purchase:"
echo "python test_bot.py --username YOUR_USERNAME --password YOUR_PASSWORD --coupon YOUR_COUPON_CODE"
echo ""
echo "See README.md and guide.md for more information."
