from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class BrowserMode(str, Enum):
    HEADLESS = "headless"
    HEADED = "headed"

class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    base_interval: float = Field(default=5.0, description="Base interval between retries in seconds")
    max_retries: int = Field(default=100, description="Maximum number of retry attempts")
    max_attempts_per_minute: int = Field(default=10, description="Rate limiting: max attempts per minute")

class BrowserConfig(BaseModel):
    """Browser-specific configuration."""
    mode: BrowserMode = Field(default=BrowserMode.HEADLESS, description="Browser mode (headless/headed)")
    browser_type: str = Field(default="chrome", description="Browser type (chrome/firefox)")
    profile_path: Optional[str] = Field(default=None, description="Path to browser profile if using one")

class Config(BaseModel):
    """Main configuration class."""
    retry: RetryConfig = Field(default_factory=RetryConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Enable debug mode")
