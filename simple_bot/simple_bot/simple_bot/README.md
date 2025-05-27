# Simple Star Citizen Purchase Bot

A straightforward bot for automating ship purchases on the Star Citizen website.

## Requirements
- Python 3.x
- Chrome or Firefox browser
- Required Python packages (install using `pip install -r requirements.txt`):
  - selenium
  - webdriver-manager
  - requests

## Setup
1. Install Python 3.x from https://www.python.org/downloads/
2. Extract this archive
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Configure the bot in `config.json`:
   - `browser`: Choose "chrome" or "firefox"
   - `headless`: Set to true for invisible operation
   - `profile`: Browser profile to use (optional)

2. Run the bot:
   ```bash
   python bot.py
   ```

   Or on Windows:
   ```bash
   setup.bat
   ```

   Or on Linux/Mac:
   ```bash
   ./setup.sh
   ```

## Files
- `bot.py` - Main bot script
- `config.json` - Bot configuration
- `requirements.txt` - Python dependencies
- `setup.bat`/`setup.sh` - Setup scripts
- `check_python.py` - Python environment checker

## Disclaimer
This bot is for educational purposes only. Use at your own risk and in accordance with RSI's terms of service.
