"""
Configuration management system for Conference Research application.
Provides centralized, environment-aware configuration with validation.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, validator, Field
from enum import Enum


class Environment(str, Enum):
    """Supported application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class APIConfig(BaseSettings):
    """API configuration settings."""
    
    # OpenAI Configuration
    openai_model: str = Field(default="gpt-4o-mini-2024-07-18", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens for OpenAI responses")
    openai_timeout: int = Field(default=30, ge=5, le=120, description="OpenAI API timeout in seconds")
    
    # Google Serper Configuration
    serper_timeout: int = Field(default=10, ge=5, le=60, description="Serper API timeout in seconds")
    serper_max_results: int = Field(default=10, ge=1, le=100, description="Maximum search results from Serper")
    
    # Groq Configuration
    groq_timeout: int = Field(default=15, ge=5, le=60, description="Groq API timeout in seconds")
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_"


class FileUploadConfig(BaseSettings):
    """File upload configuration settings."""
    
    max_size_mb: int = Field(default=50, ge=1, le=500, description="Maximum file size in MB")
    allowed_extensions: List[str] = Field(default=[".csv", ".xlsx", ".xls"], description="Allowed file extensions")
    allowed_mime_types: List[str] = Field(
        default=[
            "text/csv",
            "application/csv", 
            "text/plain",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ],
        description="Allowed MIME types"
    )
    validation_strict: bool = Field(default=True, description="Enable strict file validation")
    
    @validator('allowed_extensions')
    def validate_extensions(cls, v):
        """Ensure all extensions start with a dot."""
        return [ext if ext.startswith('.') else f'.{ext}' for ext in v]
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_FILE_"


class WebDriverConfig(BaseSettings):
    """WebDriver configuration settings."""
    
    timeout: int = Field(default=30, ge=5, le=120, description="WebDriver timeout in seconds")
    headless: bool = Field(default=True, description="Run WebDriver in headless mode")
    chrome_binary_path: Optional[str] = Field(default=None, description="Path to Chrome binary")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        description="User agent string for web requests"
    )
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_WEBDRIVER_"


class RetryConfig(BaseSettings):
    """Retry configuration for API calls."""
    
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    initial_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Initial retry delay in seconds")
    backoff_factor: float = Field(default=2.0, ge=1.0, le=5.0, description="Exponential backoff factor")
    max_delay: float = Field(default=60.0, ge=1.0, le=300.0, description="Maximum retry delay in seconds")
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_RETRY_"


class LoggingConfig(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="standard", description="Logging format (standard, detailed, json)")
    file_enabled: bool = Field(default=False, description="Enable file logging")
    file_path: str = Field(default="logs/conference_research.log", description="Log file path")
    
    @validator('level')
    def validate_log_level(cls, v):
        """Validate logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_LOG_"


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Sub-configurations
    api: APIConfig = Field(default_factory=APIConfig)
    file_upload: FileUploadConfig = Field(default_factory=FileUploadConfig)
    webdriver: WebDriverConfig = Field(default_factory=WebDriverConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Feature flags
    enable_caching: bool = Field(default=False, description="Enable response caching")
    enable_analytics: bool = Field(default=False, description="Enable usage analytics")
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_"
        case_sensitive = False
        
    @validator('environment', pre=True)
    def validate_environment(cls, v):
        """Validate and convert environment string."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v


class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self, environment: Optional[str] = None, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            environment: Override environment detection
            config_dir: Custom configuration directory path
        """
        self.environment = self._detect_environment(environment)
        # Use repository-level config directory by default (e.g., /workspace/config)
        self.config_dir = config_dir or Path(__file__).resolve().parents[2] / "config"
        self._config = None
        self._secrets = None
    
    def _detect_environment(self, override: Optional[str] = None) -> Environment:
        """Detect current environment."""
        if override:
            return Environment(override.lower())
        
        # Check environment variable
        env_var = os.getenv("ENVIRONMENT", os.getenv("CONFERENCE_RESEARCH_ENVIRONMENT"))
        if env_var:
            return Environment(env_var.lower())
        
        # Check for testing context
        if "pytest" in os.environ.get("_", "") or os.getenv("PYTEST_CURRENT_TEST"):
            return Environment.TESTING
        
        # Default to development
        return Environment.DEVELOPMENT
    
    def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = self.config_dir / filename
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            return {}
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def load_config(self) -> AppConfig:
        """Load and validate configuration from all sources."""
        if self._config is not None:
            return self._config
        
        # Load base configuration
        base_config = self._load_yaml_config("base.yaml")
        
        # Load environment-specific configuration
        env_config = self._load_yaml_config(f"{self.environment.value}.yaml")
        
        # Merge configurations (environment overrides base)
        merged_config = self._merge_configs(base_config, env_config)
        
        # Load from environment variables and validate
        try:
            self._config = AppConfig(**merged_config)
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            # Fall back to defaults
            self._config = AppConfig()
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        config = self.load_config()
        
        # Handle nested keys like 'api.openai_model'
        keys = key.split('.')
        value = config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret value from environment or secrets management."""
        # Try environment variable first
        env_key = f"CONFERENCE_RESEARCH_{key.upper()}"
        value = os.getenv(env_key)
        if value:
            return value
        
        # Try Streamlit secrets (if available)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except ImportError:
            pass
        
        return default
    
    def validate_startup(self) -> List[str]:
        """Validate configuration at startup and return any errors."""
        errors = []
        
        try:
            config = self.load_config()
        except Exception as e:
            errors.append(f"Configuration loading failed: {e}")
            return errors
        
        # Check required secrets
        required_secrets = ["openai_api_key"]  # Add more as needed
        for secret in required_secrets:
            if not self.get_secret(secret):
                if config.environment == Environment.PRODUCTION:
                    errors.append(f"Required secret '{secret}' is missing")
                else:
                    print(f"Warning: Secret '{secret}' is missing (OK for {config.environment.value})")
        
        return errors


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return get_config_manager().load_config()


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret value."""
    return get_config_manager().get_secret(key, default)
