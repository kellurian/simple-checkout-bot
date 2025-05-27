@echo off
SETLOCAL EnableDelayedExpansion

ECHO Star Citizen Checkout Bot - Launcher
ECHO ===================================

REM Set the correct path to the bot module
SET BOT_PATH=src\star_citizen_checkout

REM Check if Chrome is installed
SET CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
SET CHROME_PATH_X86="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

IF NOT EXIST %CHROME_PATH% (
    IF NOT EXIST %CHROME_PATH_X86% (
        ECHO Chrome browser not found! Please install Google Chrome first.
        PAUSE
        EXIT /B 1
    )
)

REM Check if virtual environment exists
IF NOT EXIST "venv" (
    ECHO Virtual environment not found!
    ECHO Please run setup.bat first to initialize the environment.
    PAUSE
    EXIT /B 1
)

REM Run system checks
ECHO [1/5] Running system checks...
python -c "from star_citizen_checkout.utils.check_python import main; main()" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO System check failed! Please ensure all requirements are met.
    ECHO Run setup.bat again or check the documentation for requirements.
    PAUSE
    EXIT /B 1
)

REM Check if config.json exists
IF NOT EXIST "%BOT_PATH%\config.json" (
    ECHO Configuration file not found!
    ECHO Please ensure config.json is present in %BOT_PATH% directory.
    PAUSE
    EXIT /B 1
)

ECHO Preparing to launch checkout bot...
ECHO.
ECHO [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

ECHO [3/5] Checking dependencies...
python -c "import selenium" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO Missing dependencies detected!
    ECHO Please run setup.bat to install required packages.
    PAUSE
    EXIT /B 1
)

ECHO [4/5] Launching Chrome in debug mode...
python -c "from star_citizen_checkout.bot import launch_chrome_debug; launch_chrome_debug()"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to launch Chrome in debug mode!
    ECHO Please ensure Chrome is not already running in debug mode.
    PAUSE
    EXIT /B 1
)

ECHO [5/5] Starting the checkout bot...
ECHO.
ECHO NOTE: If this is your first time running the bot:
ECHO - Make sure you're logged into the RSI website
ECHO - Ensure your payment methods are configured
ECHO - Verify your store credits are available
ECHO.
python -m star_citizen_checkout.bot

REM Deactivate virtual environment when done
deactivate

ECHO.
ECHO Bot execution completed.
ECHO Check the log file for details: checkout_bot.log
PAUSE
