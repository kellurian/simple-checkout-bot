# Star Citizen Checkout Bot - Windows Guide

## Quick Start
1. Install Google Chrome if you haven't already
2. Double-click `setup.bat` to install and configure the bot
   - This will create a virtual environment and install all required dependencies
   - If prompted, run as administrator
3. Double-click `launch.bat` to start the bot

## First-Time Setup Checklist
Before running the bot, ensure:
- [x] Google Chrome is installed
- [x] You're logged into the RSI website
- [x] Your payment methods are configured
- [x] Your store credits are available
- [x] You've run `setup.bat` successfully

## Project Structure
- Root directory:
  - `setup.bat`: First-time setup script
  - `launch.bat`: Main script to start the bot
  - `requirements.txt`: Python package dependencies
  - `WINDOWS_GUIDE.md`: This guide
  - `setup_log.txt`: Setup process log (created during setup)
  - `checkout_bot.log`: Bot runtime log (created when bot runs)

- Source code (`src/star_citizen_checkout/`):
  - `bot.py`: Main bot implementation
  - `config.json`: Bot configuration settings

## Configuration
The bot's settings are stored in `src/star_citizen_checkout/config.json`. Default settings:
- Browser: Chrome
- Headless mode: Disabled
- Store credit amount: 1385
- Ship URL: Aegis Idris-P page

## Troubleshooting
1. If setup fails:
   - Make sure Python 3.9+ is installed
   - Run setup.bat as administrator
   - Check setup_log.txt for errors

2. If launch fails:
   - Ensure Chrome is not already running in debug mode
   - Run setup.bat again to verify all dependencies
   - Check checkout_bot.log for errors

3. Common Issues:
   - "Chrome not found": Install Google Chrome
   - "Virtual environment not found": Run setup.bat first
   - "Missing dependencies": Run setup.bat again
   - "Configuration file not found": Ensure config.json exists in src/star_citizen_checkout/

## Need Help?
Check the main README.md for detailed documentation and support information.
