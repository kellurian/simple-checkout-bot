import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from selenium import webdriver
from .config import Config, BrowserMode, RetryConfig, BrowserConfig
from .logging import setup_logging, get_logger
from .browser import BrowserFactory
from .shutdown import ShutdownManager
class CheckoutCLI:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.parser = self._create_parser()
        self.config: Optional[Config] = None
        self.driver: Optional[webdriver.Remote] = None
        self.shutdown_manager = ShutdownManager()
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Star Citizen Checkout Bot CLI",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        parser.add_argument(
            "command",
            choices=["start", "status", "stop"],
            help="Command to execute"
        )
        
        parser.add_argument(
            "--url",
            required=True,
            help="Target checkout page URL"
        )
        
        parser.add_argument(
            "--config",
            type=str,
            default="config.json",
            help="Path to configuration file"
        )
        
        parser.add_argument(
            "--retry-interval",
            type=float,
            default=5.0,
            help="Interval between retry attempts in seconds"
        )
        
        parser.add_argument(
            "--max-retries",
            type=int,
            default=100,
            help="Maximum number of retry attempts"
        )
        
        parser.add_argument(
            "--browser-mode",
            choices=["headless", "headed"],
            default="headless",
            help="Browser execution mode"
        )
        
        return parser
    
    def _load_config_file(self, config_path: str) -> Dict[str, Any]:
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file) as f:
                    config_data: Dict[str, Any] = json.load(f)
                    return config_data
            return {}
        except Exception as e:
            self.logger.warning(f"Failed to load config file: {e}")
            return {}
    
    def _create_config(self, args: argparse.Namespace) -> Config:
        # Load config file first
        config_data = self._load_config_file(args.config)
        
        # Create retry config with values from file, overridden by command line
        retry_config = RetryConfig(
            base_interval=args.retry_interval,
            max_retries=config_data.get("retry", {}).get("max_retries", 100),
            max_attempts_per_minute=config_data.get("retry", {}).get("max_attempts_per_minute", 10)
        )

        # Create browser config with values from file, overridden by command line
        browser_config = BrowserConfig(
            mode=args.browser_mode,
            browser_type=config_data.get("browser", {}).get("browser_type", "chrome"),
            profile_path=config_data.get("browser", {}).get("profile_path", None)
        )

        # Build final config
        return Config(
            retry=retry_config,
            browser=browser_config,
            log_level=config_data.get("log_level", "INFO"),
            debug=config_data.get("debug", False)
        )
    
    def run(self, test_args: Optional[List[str]] = None) -> int:
        """Execute the CLI command. Returns exit code."""
        try:
            args = self.parser.parse_args(test_args)
            self.config = self._create_config(args)
            
            if args.command == "start":
                return self._handle_start(args)
            elif args.command == "status":
                return self._handle_status()
            elif args.command == "stop":
                return self._handle_stop()
            
            return 1
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
            return self._handle_stop()
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return 1
    
    def _handle_start(self, args: argparse.Namespace) -> int:
        self.logger.info("Starting checkout bot", url=args.url)
        try:
            if not self.config:
                self.logger.error("No configuration available")
                return 1
                
            # Create and register browser
            self.driver = BrowserFactory.create_driver(self.config.browser)
            self.shutdown_manager.register_browser(self.driver)
            
            # TODO: Additional start logic here
            
            return 0
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            self._handle_stop()
            return 1
    
    def _handle_status(self) -> int:
        self.logger.info("Checking bot status")
        running = self.driver is not None
        self.logger.info("Bot status", running=running)
        return 0 if running else 1
    
    def _handle_stop(self) -> int:
        self.logger.info("Stopping checkout bot")
        self.shutdown_manager.shutdown("Stop command received")
        return 0

def main() -> int:
    """Entry point for the CLI."""
    cli = CheckoutCLI()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())
