"""
Logging configuration for the Student Platform API.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import current_app


def setup_logging(app):
    """Set up logging configuration for the Flask application."""

    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # File handler with rotation
        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=10240000, backupCount=10  # 10MB
        )

        # Set log format
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )

        # Set log level
        file_handler.setLevel(logging.INFO)

        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

        # Log startup message
        app.logger.info("Student Platform API startup")

        # Log configuration info
        app.logger.info(f'Environment: {app.config.get("ENV", "unknown")}')
        app.logger.info(f"Debug mode: {app.debug}")
        app.logger.info(
            f'Database: {app.config.get("SQLALCHEMY_DATABASE_URI", "not configured")}'
        )


def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)
