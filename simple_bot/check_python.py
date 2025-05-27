#!/usr/bin/env python3
"""
Quick check script to verify Python installation and required components
"""

import sys
import platform
from pathlib import Path

def print_status(message, success):
    """Print a status message with color if available."""
    try:
        from colorama import init, Fore
        init()
        print(f"{Fore.GREEN if success else Fore.RED}{'✓' if success else '✗'} {message}{Fore.RESET}")
    except ImportError:
        print(f"{'✓' if success else '✗'} {message}")

def main():
    print("\nChecking Python Installation for Star Citizen Checkout Bot\n")

    # Check Python version
    python_version = sys.version.split()[0]
    major, minor = map(int, python_version.split('.')[:2])
    version_ok = major >= 3 and minor >= 6
    print_status(f"Python version {python_version} (need 3.6+)", version_ok)
    
    if not version_ok:
        print("\nPlease install Python 3.6 or higher from python.org")
        sys.exit(1)

    # Check Tkinter
    try:
        import tkinter
        print_status("Tkinter (GUI library) installed", True)
    except ImportError:
        print_status("Tkinter not found", False)
        print("\nTo install Tkinter:")
        if platform.system() == "Windows":
            print("1. Go to python.org/downloads")
            print("2. Download Python installer")
            print("3. Run installer and select 'Modify'")
            print("4. Ensure 'tcl/tk and IDLE' is selected")
            print("5. Complete installation")
        elif platform.system() == "Darwin":  # macOS
            print("1. Install Python from python.org")
            print("2. Ensure 'tcl/tk and IDLE' is selected during installation")
        else:  # Linux
            print("Install using your package manager:")
            print("Ubuntu/Debian: sudo apt-get install python3-tk")
            print("Fedora: sudo dnf install python3-tkinter")
            print("Arch: sudo pacman -S tk")
        sys.exit(1)

    # Check pip
    try:
        import pip
        print_status("pip installed", True)
    except ImportError:
        print_status("pip not found", False)
        print("\nPlease install pip:")
        print("1. Download get-pip.py: https://bootstrap.pypa.io/get-pip.py")
        print("2. Run: python get-pip.py")
        sys.exit(1)

    # Check if running in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print_status("Running in virtual environment", in_venv)
    if not in_venv:
        print("Note: It's recommended to run the bot in a virtual environment")
        print("The setup script will create one for you")

    # Check installation location
    install_path = Path(__file__).resolve().parent
    path_ok = " " not in str(install_path)
    print_status("Installation path has no spaces", path_ok)
    if not path_ok:
        print("\nWarning: Your installation path contains spaces:")
        print(f"  {install_path}")
        print("This might cause issues. Consider moving to a path without spaces.")

    # Final status
    if all([version_ok, 'tkinter' in sys.modules, 'pip' in sys.modules, path_ok]):
        print("\n✓ Your Python installation looks good! You can proceed with setup.")
    else:
        print("\n! Please fix the issues above before running setup.")

if __name__ == "__main__":
    main()
