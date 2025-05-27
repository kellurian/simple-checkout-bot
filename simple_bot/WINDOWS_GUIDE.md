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

## Files Explained
- `setup.bat`: First-time setup script
- `launch.bat`: Main script to start the bot
- `config.json`: Bot configuration settings
- `bot.py`: Main bot implementation
- `checkout_bot.log`: Log file (created when bot runs)

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

## Need Help?
Check the main README.md for detailed documentation and support information.
