@echo off
SETLOCAL EnableDelayedExpansion

REM Store the original directory
SET "ORIGINAL_DIR=%CD%"

REM Change to the script's directory
cd /d "%~dp0"

REM Ensure we can find the src directory
IF NOT EXIST "src\star_citizen_checkout" (
    ECHO Error: src\star_citizen_checkout directory not found!
    ECHO Please ensure you're running setup.bat from the correct location.
    PAUSE
    EXIT /B 1
)

ECHO Star Citizen Checkout Bot - Setup and Configuration
ECHO ================================================

REM Create log file
SET LOG_FILE=%~dp0setup_log.txt
ECHO Setup started at %DATE% %TIME% > %LOG_FILE%

REM Set paths
SET BOT_PATH=%~dp0src\star_citizen_checkout
SET REQUIREMENTS_FILE=%~dp0requirements.txt

REM Function to log messages
CALL :LOG "Checking system requirements..."

REM Check for administrative privileges
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [31mPlease run this script as Administrator[0m
    ECHO Right-click setup.bat and select "Run as administrator"
    CALL :LOG "Setup failed: Not running as administrator"
    PAUSE
    EXIT /B 1
)
CALL :LOG "Running with administrative privileges"

REM Check if Python is installed and get version
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [31mPython not found![0m
    ECHO.
    ECHO Please install Python:
    ECHO 1. Go to: https://www.python.org/downloads/
    ECHO 2. Download Python 3.9 or higher
    ECHO 3. IMPORTANT: Check "Add Python to PATH" during installation
    ECHO 4. Run this setup again
    CALL :LOG "Setup failed: Python not found"
    START https://www.python.org/downloads/
    PAUSE
    EXIT /B 1
)

REM Ensure src directory exists
IF NOT EXIST "%BOT_PATH%" (
    ECHO Creating bot directory structure...
    mkdir "%BOT_PATH%"
    CALL :LOG "Created directory: %BOT_PATH%"
)

REM Check Python version
FOR /F "tokens=2" %%I IN ('python --version 2^>^&1') DO SET PYTHON_VERSION=%%I
FOR /F "tokens=1 delims=." %%I IN ("%PYTHON_VERSION%") DO SET PYTHON_MAJOR=%%I
IF %PYTHON_MAJOR% LSS 3 (
    ECHO X Python 3 required. You have Python %PYTHON_VERSION%.
    EXIT /B 1
)

ECHO ✓ Python %PYTHON_VERSION% found

REM Check for tkinter
ECHO Checking for Tkinter (GUI library)...
python -c "import tkinter" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Tkinter not found. This is needed for the graphical interface.
    ECHO.
    ECHO To install Tkinter:
    ECHO 1. Go to python.org/downloads
    ECHO 2. Download Python installer again
    ECHO 3. Run installer and select "Modify"
    ECHO 4. Ensure "tcl/tk and IDLE" is selected
    ECHO 5. Click "Next" and complete the installation
    ECHO.
    ECHO After installing Tkinter, run this setup again.
    ECHO.
    PAUSE
    EXIT /B 1
)
ECHO ✓ Tkinter found

REM Create virtual environment
ECHO Creating virtual environment...
python -m venv "%~dp0venv"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to create virtual environment. Please install venv package.
    ECHO   You can try: python -m pip install virtualenv
    EXIT /B 1
)
ECHO ✓ Virtual environment created

REM Activate virtual environment and prepare for dependencies
ECHO Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to activate virtual environment.
    EXIT /B 1
)
ECHO ✓ Virtual environment activated

REM Install dependencies
ECHO Installing dependencies...
ECHO This may take a few minutes...

REM Upgrade pip first
call venv\Scripts\python -m pip install --upgrade pip
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to upgrade pip.
    EXIT /B 1
)

REM Install all dependencies from requirements.txt
ECHO Installing all packages...

REM Upgrade core build tools first
ECHO Upgrading pip and build tools...
call "%~dp0venv\Scripts\python" -m pip install --upgrade pip wheel setuptools build
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to upgrade build tools.
    ECHO Please ensure you have internet connectivity and proper permissions.
    EXIT /B 1
)
ECHO ✓ Build tools upgraded

REM Install project requirements
ECHO Installing project requirements...
call "%~dp0venv\Scripts\python" -m pip install --no-cache-dir -r "%REQUIREMENTS_FILE%"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to install core packages.
    ECHO.
    ECHO Troubleshooting steps:
    ECHO 1. Check your internet connection
    ECHO 2. Try running as administrator
    ECHO 3. If behind a proxy, configure pip proxy settings
    ECHO 4. Try updating pip: python -m pip install --upgrade pip
    ECHO.
    PAUSE
    EXIT /B 1
)

REM Install the bot package in development mode
ECHO Installing bot package...
cd /d "%~dp0"
REM First attempt: Install in development mode
call "%~dp0venv\Scripts\python" -m pip install --no-cache-dir -v -e .
IF %ERRORLEVEL% NEQ 0 (
    ECHO First installation attempt failed, trying alternative method...
    
    REM Second attempt: Install using absolute path
    pushd "%~dp0"
    call "%~dp0venv\Scripts\python" -m pip install --no-cache-dir -v .
    popd
    
    IF %ERRORLEVEL% NEQ 0 (
        ECHO X Failed to install package after multiple attempts.
        ECHO Please ensure you have proper permissions and Python is installed correctly.
        EXIT /B 1
    )
)

REM Verify installation
call "%~dp0venv\Scripts\python" -c "import star_citizen_checkout; print('Package verified: ' + star_citizen_checkout.__version__)"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Package installation verification failed.
    EXIT /B 1
)
ECHO ✓ Package installed and verified

REM Return to original directory
cd /d "%ORIGINAL_DIR%"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to install the bot package.
    ECHO Please try running setup.bat again as administrator.
    PAUSE
    EXIT /B 1
)

ECHO ✓ Dependencies installed

REM Verify core functionality
ECHO Verifying core packages...

REM Test Selenium using virtual environment Python
call "%~dp0venv\Scripts\python" -c "import selenium" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Selenium verification failed
    ECHO Please try running setup.bat again
    EXIT /B 1
)
ECHO ✓ Selenium verified

REM Test WebDriver Manager using virtual environment Python
call "%~dp0venv\Scripts\python" -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO X WebDriver Manager verification failed
    ECHO Please try:
    ECHO 1. Run setup.bat as administrator
    ECHO 2. Check your internet connection
    ECHO 3. Temporarily disable antivirus
    EXIT /B 1
)
ECHO ✓ WebDriver Manager verified

REM Verify browser setup using virtual environment Python
ECHO Testing browser configuration...
call "%~dp0venv\Scripts\python" -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service; from webdriver_manager.chrome import ChromeDriverManager; print('Setting up Chrome...'); driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())); print('Chrome launched successfully'); driver.quit(); print('Chrome test complete')"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Browser setup verification failed.
    ECHO Please ensure Chrome is installed and up to date.
    PAUSE
    EXIT /B 1
)
ECHO ✓ Browser setup verified

ECHO.
ECHO [32mSetup completed successfully![0m
CALL :LOG "Setup completed successfully"

ECHO.
ECHO [36mNext steps:[0m
ECHO 1. Run launch.bat to start the bot
ECHO 2. Check WINDOWS_GUIDE.md for detailed instructions
ECHO.
cscript //nologo CreateShortcut.vbs
DEL CreateShortcut.vbs
CALL :LOG "Created desktop shortcut"

ECHO.
CHOICE /C YN /M "Would you like to launch the GUI now"
IF %ERRORLEVEL% EQU 1 (
    ECHO.
    ECHO [32mStarting GUI...[0m
    CALL :LOG "Launching GUI"
    call launch_gui.bat
) ELSE (
    ECHO.
    ECHO You can start the GUI later using:
    ECHO 1. The desktop shortcut
    ECHO 2. launch_gui.bat in this folder
)

:LOG
ECHO %DATE% %TIME% - %~1 >> %LOG_FILE%
EXIT /B 0

PAUSE
