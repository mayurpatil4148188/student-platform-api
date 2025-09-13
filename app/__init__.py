"""
Application Factory
Creates and configures the Flask application.
"""

import os
import logging
from typing import Optional
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flasgger import Swagger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app.core.config import get_config, Config
from app.models import db

# Initialize extensions
migrate = Migrate()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
swagger = Swagger()

# Logger
logger = logging.getLogger(__name__)


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration environment name

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app, config)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register middleware
    register_middleware(app)

    # Register CLI commands
    register_cli_commands(app)

    # Setup logging
    setup_logging(app, config)

    # Initialize Sentry if configured
    init_sentry(config)

    # Register health check and root endpoints
    register_health_endpoints(app)

    logger.info(f"{config.APP_NAME} initialized in {config.APP_ENV} mode")

    return app


def init_extensions(app: Flask, config: Config) -> None:
    """
    Initialize Flask extensions.

    Args:
        app: Flask application instance
        config: Configuration object
    """
    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # CORS
    cors.init_app(
        app,
        origins=config.CORS_ORIGINS,
        allow_credentials=config.CORS_ALLOW_CREDENTIALS,
        max_age=config.CORS_MAX_AGE,
    )

    # Rate Limiting
    if config.RATE_LIMIT_ENABLED:
        limiter.init_app(app)

    # Caching
    cache_config = {
        "CACHE_TYPE": config.CACHE_TYPE,
        "CACHE_DEFAULT_TIMEOUT": config.CACHE_DEFAULT_TIMEOUT,
        "CACHE_KEY_PREFIX": config.CACHE_KEY_PREFIX,
    }

    if config.CACHE_TYPE == "redis":
        cache_config["CACHE_REDIS_URL"] = config.REDIS_URL

    cache.init_app(app, config=cache_config)

    # Swagger/API Documentation
    if config.SWAGGER_ENABLED:
        swagger.init_app(app)
        app.config["SWAGGER"] = config.SWAGGER


def register_blueprints(app: Flask) -> None:
    """
    Register application blueprints.

    Args:
        app: Flask application instance
    """
    from app.api import api_bp

    # Register the main API blueprint
    app.register_blueprint(api_bp)

    logger.debug("Registered API blueprint with Flask-RESTX")


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors."""
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": (
                            str(error.description)
                            if error.description
                            else "Bad request"
                        ),
                    },
                }
            ),
            400,
        )

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized errors."""
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication required",
                    },
                }
            ),
            401,
        )

    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden errors."""
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {"code": "FORBIDDEN", "message": "Access forbidden"},
                }
            ),
            403,
        )

    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors."""
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {"code": "NOT_FOUND", "message": "Resource not found"},
                }
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle validation errors."""
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": (
                            str(error.description)
                            if error.description
                            else "Validation failed"
                        ),
                    },
                }
            ),
            422,
        )

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit errors."""
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                    },
                }
            ),
            429,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {error}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                    },
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors."""
        logger.exception(f"Unexpected error: {error}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": {
                        "code": "UNEXPECTED_ERROR",
                        "message": "An unexpected error occurred",
                    },
                }
            ),
            500,
        )


def register_middleware(app: Flask) -> None:
    """
    Register application middleware.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request():
        """Execute before each request."""
        from flask import request, abort

        # API Key authentication for production
        if app.config["APP_ENV"] == "production":
            # Skip auth for health endpoints and docs
            if request.path in ["/health", "/ready", "/api/docs", "/"]:
                return

            # Check API key
            api_key = request.headers.get("X-API-Key")
            if api_key != app.config["API_KEY"]:
                abort(401, description="Invalid or missing API key")

    @app.after_request
    def after_request(response):
        """Execute after each request."""
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Add custom headers
        response.headers["X-API-Version"] = app.config["API_VERSION"]

        return response


def register_cli_commands(app: Flask) -> None:
    """
    Register CLI commands.

    Args:
        app: Flask application instance
    """

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized!")

    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        from app.utils.seed_data import seed_database

        seed_database()
        print("Database seeded!")

    @app.cli.command()
    def drop_db():
        """Drop all database tables."""
        db.drop_all()
        print("Database tables dropped!")

    @app.cli.command()
    def recreate_db():
        """Recreate the database."""
        db.drop_all()
        db.create_all()
        print("Database recreated!")


def register_health_endpoints(app: Flask) -> None:
    """
    Register health check endpoints.

    Args:
        app: Flask application instance
    """

    @app.route("/")
    def index():
        """Root endpoint."""
        return jsonify(
            {
                "name": app.config["APP_NAME"],
                "version": "1.0.0",
                "environment": app.config["APP_ENV"],
                "api_version": app.config["API_VERSION"],
                "documentation": (
                    f"{app.config['SWAGGER_URL']}"
                    if app.config["SWAGGER_ENABLED"]
                    else None
                ),
            }
        )

    @app.route("/health")
    def health():
        """Health check endpoint."""
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": app.config["APP_NAME"],
                    "environment": app.config["APP_ENV"],
                }
            ),
            200,
        )

    @app.route("/ready")
    def ready():
        """Readiness check endpoint."""
        try:
            # Check database connection
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))

            return (
                jsonify(
                    {
                        "status": "ready",
                        "service": app.config["APP_NAME"],
                        "checks": {"database": "connected"},
                    }
                ),
                200,
            )
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return (
                jsonify(
                    {
                        "status": "not_ready",
                        "service": app.config["APP_NAME"],
                        "checks": {"database": "disconnected"},
                    }
                ),
                503,
            )


def setup_logging(app: Flask, config: Config) -> None:
    """
    Setup application logging.

    Args:
        app: Flask application instance
        config: Configuration object
    """
    # Create logs directory if it doesn't exist
    if config.LOG_FILE:
        log_dir = os.path.dirname(config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # Configure logging format
    if config.LOG_FORMAT == "json":
        from pythonjsonlogger import jsonlogger

        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )

    # Configure handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler
    if config.LOG_FILE:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure app logger
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    for handler in handlers:
        handler.setLevel(log_level)
        app.logger.addHandler(handler)

    app.logger.setLevel(log_level)

    # Configure werkzeug logger
    logging.getLogger("werkzeug").setLevel(log_level)


def init_sentry(config: Config) -> None:
    """
    Initialize Sentry error tracking.

    Args:
        config: Configuration object
    """
    if config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            environment=config.SENTRY_ENVIRONMENT,
            traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
        )
        logger.info("Sentry error tracking initialized")
