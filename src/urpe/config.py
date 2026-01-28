"""Configuration management."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings."""
    
    # LLM settings
    default_model: str = Field(default="gemini/gemini-2.0-flash")
    gemini_api_key: Optional[str] = None
    
    # Memory settings  
    db_path: str = Field(default="data/urpe.db")
    
    # Tool settings
    tools_require_confirmation: bool = Field(default=True)
    command_timeout: int = Field(default=30)


def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Load settings from YAML file and environment variables.
    
    Priority (highest to lowest):
    1. Environment variables (URPE_*, GEMINI_API_KEY)
    2. Config file
    3. Defaults
    """
    settings_dict = {}
    
    # Load from config file if exists
    if config_path:
        path = Path(config_path)
    else:
        path = Path("config.yaml")
    
    if path.exists():
        with open(path) as f:
            file_config = yaml.safe_load(f) or {}
            settings_dict.update(file_config)
    
    # Override with environment variables
    env_mapping = {
        "URPE_MODEL": "default_model",
        "URPE_DB_PATH": "db_path",
        "GEMINI_API_KEY": "gemini_api_key",
    }
    
    for env_var, setting_key in env_mapping.items():
        value = os.getenv(env_var)
        if value:
            settings_dict[setting_key] = value
    
    return Settings(**settings_dict)


# Default settings instance
settings = load_settings()
