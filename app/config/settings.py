"""
Settings Module
===============

This module defines centralized configuration management for the application.
It uses Pydantic's `BaseSettings` to load environment variables from `.env`
or system-level environment variables.

## Why this is needed:

* Avoid hardcoding API keys, secrets, and database URIs in code.
* Keep production, staging, and development settings separate.
* Provide a single configurable source of truth for all system settings.
* Make configuration changes without modifying business logic.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings class.

    Attributes:
        APP_NAME (str): Displayed API title.
        APP_VERSION (str): Application version.
        DEBUG (bool): Debug mode flag.
        GROQ_API_KEY (str): Required - must be set.
        SECRET_KEY (str): JWT signing secret.
        ALGORITHM (str): JWT signing algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Token validity period.
        DATABASE_URL (str): Storage backend.
        MAX_RESEARCH_ITERATIONS (int): Max loops per agent.
        DEFAULT_LLM_TEMPERATURE (float): Base LLM creativity.
    """
    pass

# ------------------------------
# API Metadata
# ------------------------------
APP_NAME: str = "Multi-Agent Research Assistant"   # Displayed API title
APP_VERSION: str = "2.0.0"                         # Application version
DEBUG: bool = False                                # Debug mode flag

# ------------------------------
# LLM / AI Configuration
# ------------------------------
GROQ_API_KEY: str                                  # Required - must be set

# ------------------------------
# Authentication / Security
# ------------------------------
SECRET_KEY: str                                    # JWT signing secret
ALGORITHM: str = "HS256"                           # JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440            # Token validity period

# ------------------------------
# Database Configuration
# ------------------------------
DATABASE_URL: str = "sqlite:///./research_assistant.db"  # Storage backend

# ------------------------------
# AI Agent Behavior Settings
# ------------------------------
MAX_RESEARCH_ITERATIONS: int = 2                   # Max loops per agent
DEFAULT_LLM_TEMPERATURE: float = 0.7               # Base LLM creativity

class Config:
    """
    Pydantic configuration for settings loading.

    - `env_file`: forces Pydantic to read values from `.env` if present.
    - `case_sensitive`: makes environment variable names case-sensitive.
    """
    env_file = ".env"
    case_sensitive = True

# ----------------------------------------------------

# Global Singleton Settings Instance

# ----------------------------------------------------

# Import and use `settings` anywhere in the application to access configuration.

settings = Settings()
