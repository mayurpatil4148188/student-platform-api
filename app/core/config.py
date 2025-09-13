"""
Configuration Management
Handles all application configuration from environment variables.
"""

import os
from typing import Optional, List
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""

    # =====================================================
    # Application Settings
    # =====================================================
    APP_NAME: str = os.getenv("APP_NAME", "Student Platform API")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    API_VERSION: str = os.getenv("API_VERSION", "v1")

    # =====================================================
    # Server Settings
    # =====================================================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 5000))
    WORKERS: int = int(os.getenv("WORKERS", 4))
    THREADS: int = int(os.getenv("THREADS", 2))
    WORKER_TIMEOUT: int = int(os.getenv("WORKER_TIMEOUT", 120))

    # =====================================================
    # Database Configuration
    # =====================================================
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///student_platform.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"

    # Database Pool Settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", 30)),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 3600)),
        "pool_pre_ping": True,  # Verify connections before using
    }

    # =====================================================
    # Security Configuration
    # =====================================================
    API_KEY: str = os.getenv("API_KEY", "your-api-key-here")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(
        seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 2592000))
    )

    # Session Configuration
    SESSION_COOKIE_SECURE: bool = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )
    SESSION_COOKIE_HTTPONLY: bool = (
        os.getenv("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
    )
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    # =====================================================
    # CORS Configuration
    # =====================================================
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = (
        os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    )
    CORS_MAX_AGE: int = int(os.getenv("CORS_MAX_AGE", 3600))

    # =====================================================
    # Rate Limiting
    # =====================================================
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100/hour")
    RATE_LIMIT_STORAGE_URL: str = os.getenv(
        "RATE_LIMIT_STORAGE_URL", "redis://localhost:6379/1"
    )

    # =====================================================
    # Redis/Cache Configuration
    # =====================================================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE: str = os.getenv("CACHE_TYPE", "simple")  # 'redis' in production
    CACHE_DEFAULT_TIMEOUT: int = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_KEY_PREFIX: str = os.getenv("CACHE_KEY_PREFIX", "student_platform_")

    # =====================================================
    # Pagination Settings
    # =====================================================
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", 20))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", 100))
    DEFAULT_SORT_ORDER: str = os.getenv("DEFAULT_SORT_ORDER", "desc")

    # =====================================================
    # Logging Configuration
    # =====================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", 10485760))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", 10))
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # 'json' or 'text'

    # =====================================================
    # Swagger/Documentation
    # =====================================================
    SWAGGER_ENABLED: bool = os.getenv("SWAGGER_ENABLED", "True").lower() == "true"
    SWAGGER_URL: str = os.getenv("SWAGGER_URL", "/api/docs")
    SWAGGER_UI_JSONEDITOR: bool = (
        os.getenv("SWAGGER_UI_JSONEDITOR", "True").lower() == "true"
    )
    SWAGGER_UI_DOC_EXPANSION: str = os.getenv("SWAGGER_UI_DOC_EXPANSION", "list")

    # Swagger configuration dict
    SWAGGER = {
        "title": APP_NAME,
        "version": "1.0.0",
        "description": "RESTful API for managing student university applications",
        "uiversion": 3,
        "doc_dir": "./docs/api/",
        "specs_route": f"{SWAGGER_URL}/specs/",
        "specs": [
            {
                "endpoint": "apispec",
                "route": f"{SWAGGER_URL}/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": f"{SWAGGER_URL}/specs/",
    }

    # =====================================================
    # Request Settings
    # =====================================================
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))  # 16MB
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 30))

    # =====================================================
    # Monitoring
    # =====================================================
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", APP_ENV)
    SENTRY_TRACES_SAMPLE_RATE: float = float(
        os.getenv("SENTRY_TRACES_SAMPLE_RATE", 0.1)
    )

    PROMETHEUS_ENABLED: bool = (
        os.getenv("PROMETHEUS_ENABLED", "False").lower() == "true"
    )
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "True").lower() == "true"

    # =====================================================
    # Feature Flags
    # =====================================================
    FEATURE_BULK_OPERATIONS: bool = (
        os.getenv("FEATURE_BULK_OPERATIONS", "True").lower() == "true"
    )
    FEATURE_EXPORT_DATA: bool = (
        os.getenv("FEATURE_EXPORT_DATA", "True").lower() == "true"
    )
    FEATURE_ADVANCED_SEARCH: bool = (
        os.getenv("FEATURE_ADVANCED_SEARCH", "True").lower() == "true"
    )
    FEATURE_WEBHOOKS: bool = os.getenv("FEATURE_WEBHOOKS", "False").lower() == "true"
    FEATURE_EMAIL_NOTIFICATIONS: bool = (
        os.getenv("FEATURE_EMAIL_NOTIFICATIONS", "False").lower() == "true"
    )

    # =====================================================
    # Business Logic Constants
    # =====================================================
    STATUS_WEIGHTS = {
        "Building Application": int(os.getenv("STATUS_WEIGHT_BUILDING", 1)),
        "Application Submitted to University": int(
            os.getenv("STATUS_WEIGHT_SUBMITTED", 2)
        ),
        "Offer Received": int(os.getenv("STATUS_WEIGHT_OFFER_RECEIVED", 3)),
        "Offer Accepted by Student": int(os.getenv("STATUS_WEIGHT_OFFER_ACCEPTED", 4)),
        "Visa Approved": int(os.getenv("STATUS_WEIGHT_VISA_APPROVED", 5)),
        "Dropped": int(os.getenv("STATUS_WEIGHT_DROPPED", 0)),
    }

    INTAKE_DATE_FORMAT: str = os.getenv("INTAKE_DATE_FORMAT", "%b %Y")

    # =====================================================
    # Email Configuration (if needed)
    # =====================================================
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = os.getenv(
        "MAIL_DEFAULT_SENDER", "noreply@studentplatform.com"
    )


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    RATE_LIMIT_ENABLED = False

    # Use simple cache in development
    CACHE_TYPE = "simple"

    # More verbose logging in development
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True

    # Use separate test database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/student_platform_test_db",
    )

    # Disable rate limiting in tests
    RATE_LIMIT_ENABLED = False

    # Use simple cache in tests
    CACHE_TYPE = "simple"

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Enforce security in production
    SESSION_COOKIE_SECURE = True

    # Use Redis for caching in production
    CACHE_TYPE = "redis" if Config.REDIS_URL else "simple"

    # Ensure secret keys are set in production
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        if cls.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set in production")
        if cls.API_KEY == "your-api-key-here":
            raise ValueError("API_KEY must be set in production")


class StagingConfig(ProductionConfig):
    """Staging environment configuration."""

    DEBUG = True

    # Use staging database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "STAGING_DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI
    )


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
    "default": DevelopmentConfig,
}


def get_config(env: Optional[str] = None) -> Config:
    """
    Get configuration object based on environment.

    Args:
        env: Environment name (development, testing, production, staging)

    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv("APP_ENV", "development")

    return config.get(env, DevelopmentConfig)


# Export the current configuration
settings = get_config()
