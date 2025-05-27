@echo off
SETLOCAL EnableDelayedExpansion

REM Change to the script's directory
cd /d "%~dp0"

ECHO Star Citizen Checkout Bot - Launcher
ECHO ===================================

REM Set the correct path to the bot module
SET BOT_PATH=%~dp0src\star_citizen_checkout

REM Check if virtual environment exists first
IF NOT EXIST "venv" (
    ECHO Virtual environment not found!
    ECHO Please run setup.bat first to initialize the environment.
    PAUSE
    EXIT /B 1
)

REM Activate virtual environment immediately
ECHO [1/6] Activating virtual environment...
IF NOT EXIST "%~dp0venv\Scripts\activate.bat" (
    ECHO Virtual environment activation script not found!
    ECHO Please run setup.bat again to create the virtual environment.
    PAUSE
    EXIT /B 1
)
call "%~dp0venv\Scripts\activate.bat"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to activate virtual environment!
    ECHO Please run setup.bat again to fix the environment.
    PAUSE
    EXIT /B 1
)

REM Check if Chrome is installed
ECHO [2/6] Checking Chrome installation...
SET "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
SET "CHROME_PATH_X86=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

IF NOT EXIST "%CHROME_PATH%" (
    IF NOT EXIST "%CHROME_PATH_X86%" (
        ECHO Chrome browser not found! Please install Google Chrome first.
        PAUSE
        EXIT /B 1
    )
)

REM Run system checks using virtual environment Python
ECHO [3/6] Running system checks...
call "%~dp0venv\Scripts\python" -c "from star_citizen_checkout.utils.check_python import main; main()" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO System check failed! Please ensure all requirements are met.
    ECHO Run setup.bat again or check the documentation for requirements.
    PAUSE
    EXIT /B 1
)

REM Check if config.json exists
ECHO [4/6] Checking configuration...
IF NOT EXIST "%BOT_PATH%\config.json" (
    ECHO Configuration file not found!
    ECHO Please ensure config.json is present in %BOT_PATH% directory.
    PAUSE
    EXIT /B 1
)

ECHO [5/6] Starting the checkout bot...
ECHO.
ECHO NOTE: If this is your first time running the bot:
ECHO - Make sure you're logged into the RSI website
ECHO - Ensure your payment methods are configured
ECHO - Verify your store credits are available
ECHO.

REM Read URL from config file
for /f "tokens=* USEBACKQ" %%F in (`"%~dp0venv\Scripts\python" -c "import json; print(json.load(open('%BOT_PATH%\config.json'))['ship_url'])"`) do (
    set SHIP_URL=%%F
)

REM Launch bot with required arguments
call "%~dp0venv\Scripts\python" -m star_citizen_checkout start --url "%SHIP_URL%" --config "%BOT_PATH%\config.json" --browser-mode headed

REM Check if bot exited with error
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO Bot encountered an error during execution.
    ECHO Check the log file for details: checkout_bot.log
) ELSE (
    ECHO.
    ECHO Bot execution completed successfully.
    ECHO Check the log file for details: checkout_bot.log
)

REM Deactivate virtual environment
call "%~dp0venv\Scripts\deactivate.bat"

PAUSE
