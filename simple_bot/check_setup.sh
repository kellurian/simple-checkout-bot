#!/bin/bash

# Make the check script executable
chmod +x check_python.py

# Check if Python is in PATH
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "✗ Python not found in PATH"
    echo "Please install Python from python.org"
    exit 1
fi

# Run the check script
$PYTHON check_python.py

# If check passes, ask about proceeding with setup
if [ $? -eq 0 ]; then
    echo
    read -p "Would you like to proceed with setup now? (y/n) " proceed
    if [[ "$proceed" =~ ^[Yy]$ ]]; then
        echo
        if [ -f "setup.sh" ]; then
            bash setup.sh
        else
            echo "✗ setup.sh not found in current directory"
            exit 1
        fi
    else
        echo
        echo "You can run setup later with: bash setup.sh"
    fi
fi
