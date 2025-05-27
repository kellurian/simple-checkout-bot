import pytest
from pathlib import Path
import json
from unittest.mock import patch
from star_citizen_checkout.cli import CheckoutCLI

@pytest.fixture
def temp_config(tmp_path):
    config = {
        "retry": {
            "base_interval": 3.0,
            "max_retries": 50,
            "max_attempts_per_minute": 10
        },
        "browser": {
            "mode": "headless"
        }
    }
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file

def test_cli_parser_creation():
    cli = CheckoutCLI()
    parser = cli._create_parser()
    
    assert parser.description == "Star Citizen Checkout Bot CLI"
    
    # Verify required arguments
    args = parser.parse_args(["start", "--url", "https://example.com"])
    assert args.command == "start"
    assert args.url == "https://example.com"
    assert args.config == "config.json"  # default value

def test_config_file_loading(temp_config):
    cli = CheckoutCLI()
    config_data = cli._load_config_file(str(temp_config))
    
    assert config_data["retry"]["base_interval"] == 3.0
    assert config_data["retry"]["max_retries"] == 50
    assert config_data["browser"]["mode"] == "headless"

def test_cli_command_line_override(temp_config):
    cli = CheckoutCLI()
    cli.run([
        "start",
        "--url", "https://example.com",
        "--config", str(temp_config),
        "--retry-interval", "10.0",
        "--browser-mode", "headed"
    ])
    
    # Command line args should override config file
    assert cli.config.retry.base_interval == 10.0
    assert cli.config.browser.mode == "headed"
    # Original config values should persist
    assert cli.config.retry.max_retries == 50
    assert cli.config.retry.max_attempts_per_minute == 10

def test_nonexistent_config():
    cli = CheckoutCLI()
    config_data = cli._load_config_file("nonexistent.json")
    assert config_data == {}

@pytest.mark.parametrize("command", ["start", "status", "stop"])
def test_cli_commands(command):
    cli = CheckoutCLI()
    with patch.object(cli, f"_handle_{command}") as mock_handler:
        mock_handler.return_value = 0
        result = cli.run([command, "--url", "https://example.com"])
        
        assert result == 0
        mock_handler.assert_called_once()

def test_keyboard_interrupt_handling():
    cli = CheckoutCLI()
    with patch.object(cli, "_handle_start", side_effect=KeyboardInterrupt):
        result = cli.run(["start", "--url", "https://example.com"])
        assert result == 0  # Should handle gracefully

def test_general_error_handling():
    cli = CheckoutCLI()
    with patch.object(cli, "_handle_start", side_effect=Exception("Test error")):
        result = cli.run(["start", "--url", "https://example.com"])
        assert result == 1  # Should return error code
