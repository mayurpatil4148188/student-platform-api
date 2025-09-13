"""
Production configuration settings for the Student Platform API.
"""

import os
from .config import Config


class ProductionConfig(Config):
    """Production configuration class."""

    # Flask settings
    DEBUG = False
    TESTING = False

    # Database settings
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://username:password@localhost:5432/student_platform_prod"
    )

    # Security settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "production-secret-key-change-this"

    # Redis settings for rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "logs/app.log")

    # CORS settings
    CORS_ORIGINS = (
        os.environ.get("CORS_ORIGINS", "").split(",")
        if os.environ.get("CORS_ORIGINS")
        else []
    )

    # API settings
    API_TITLE = "Student Platform API"
    API_VERSION = "1.0"
    API_DESCRIPTION = (
        "A comprehensive API for managing students and university applications"
    )

    # Rate limiting settings
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_HEADERS_ENABLED = True

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 20,
        "max_overflow": 30,
    }

    # Session settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Additional production settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
