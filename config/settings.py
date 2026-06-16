"""Centralized application configuration using environment variables.

This module consolidates all hardcoded paths, model hyperparameters,
API keys, and service configurations into a single source of truth.
All values are loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = PROJECT_ROOT / "data"
UPLOAD_DIR: Path = PROJECT_ROOT / "uploads"
FRONTEND_DIR: Path = PROJECT_ROOT / "frontend"

# Flask
FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT: int = int(os.getenv("PORT", "5000"))
FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# MongoDB
MONGODB_URI: str = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "Medicare")

# aiXplain
TEAM_API_KEY: str = os.getenv("TEAM_API_KEY", "")
AIXPLAIN_AGENT_ID: str = os.getenv("AIXPLAIN_AGENT_ID", "")
AIXPLAIN_PIPELINE_ID: str = os.getenv("AIXPLAIN_PIPELINE_ID", "")

# Email / SMTP (must be set via environment variables — no defaults)
MAIL_SERVER: str = os.getenv("MAIL_HOST", "")
MAIL_PORT: int = int(os.getenv("MAIL_PORT", "0"))
MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
MAIL_USE_SSL: bool = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER: str = os.getenv("MAIL_DEFAULT_SENDER", "")
MAIL_DEBUG: bool = os.getenv("MAIL_DEBUG", "false").lower() == "true"

# Upload
ALLOWED_EXTENSIONS: set = {"pdf", "png", "jpg", "jpeg"}
