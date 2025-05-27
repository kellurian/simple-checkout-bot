@echo off
ECHO Star Citizen Checkout Bot - Setup and Configuration
ECHO ================================================

REM Create log file
SET LOG_FILE=setup_log.txt
ECHO Setup started at %DATE% %TIME% > %LOG_FILE%

REM Set paths
SET BOT_PATH=src\star_citizen_checkout
SET REQUIREMENTS_FILE=requirements.txt

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
python -m venv venv
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Failed to create virtual environment. Please install venv package.
    ECHO   You can try: python -m pip install virtualenv
    EXIT /B 1
)
ECHO ✓ Virtual environment created

REM Activate virtual environment and prepare for dependencies
ECHO Activating virtual environment...
call venv\Scripts\activate.bat
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
call venv\Scripts\python -m pip install --no-cache-dir -r "%~dp0requirements.txt"
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

ECHO Installing remaining dependencies...
call venv\Scripts\python -m pip install --no-cache-dir -r "%~dp0requirements.txt"
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Some dependencies failed to install.
    ECHO Core functionality should still work.
    ECHO.
    ECHO To retry installing optional dependencies later:
    ECHO pip install -r requirements.txt
    ECHO.
    CHOICE /C YN /M "Continue anyway"
    IF !ERRORLEVEL! EQU 2 EXIT /B 1
)

ECHO ✓ Dependencies installed

REM Verify core functionality
ECHO Verifying core packages...

REM Test Selenium
python -c "import selenium" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO X Selenium verification failed
    ECHO Please try running setup.bat again
    EXIT /B 1
)
ECHO ✓ Selenium verified

REM Test WebDriver Manager
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO X WebDriver Manager verification failed
    ECHO Please try:
    ECHO 1. Run setup.bat as administrator
    ECHO 2. Check your internet connection
    ECHO 3. Temporarily disable antivirus
    EXIT /B 1
)
ECHO ✓ WebDriver Manager verified

REM Verify browser setup
ECHO Testing browser configuration...
python -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service; from webdriver_manager.chrome import ChromeDriverManager; print('Setting up Chrome...'); driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())); print('Chrome launched successfully'); driver.quit(); print('Chrome test complete')"
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
ECHO 1. Launch the GUI: launch_gui.bat
ECHO 2. Configure your settings in the GUI
ECHO 3. Use the Testing tab to verify everything works
ECHO.
ECHO [33mNote:[0m The GUI includes all testing functionality
ECHO       and handles browser configuration automatically.
ECHO.

REM Create desktop shortcut
ECHO Creating desktop shortcut...
SET SHORTCUT_PATH=%USERPROFILE%\Desktop\Star_Citizen_Bot.lnk
IF EXIST "%SHORTCUT_PATH%" DEL "%SHORTCUT_PATH%"
ECHO Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
ECHO sLinkFile = "%SHORTCUT_PATH%" >> CreateShortcut.vbs
ECHO Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
ECHO oLink.TargetPath = "%CD%\launch_gui.bat" >> CreateShortcut.vbs
ECHO oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
ECHO oLink.Description = "Star Citizen Checkout Bot" >> CreateShortcut.vbs
ECHO oLink.Save >> CreateShortcut.vbs
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
