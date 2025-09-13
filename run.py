#!/usr/bin/env python
"""
Application Entry Point
Main script to run the Flask application.

Usage:
    Development: python run.py
    Production: gunicorn "app:create_app()" --config gunicorn.conf.py
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the application factory
from app import create_app
from app.core.config import settings

# Create the Flask application
app = create_app()


# Application context for shell
@app.shell_context_processor
def make_shell_context():
    """
    Make variables available in flask shell.

    Usage:
        flask shell
        >>> db.create_all()
        >>> Student.query.all()
    """
    from app.models import db, Student, Application
    from app.services.status_calculator import status_calculator

    return {
        "db": db,
        "Student": Student,
        "Application": Application,
        "status_calculator": status_calculator,
        "settings": settings,
    }


if __name__ == "__main__":
    """
    Run the application in development mode.
    For production, use gunicorn or another WSGI server.
    """

    # Print startup information
    print("\n" + "=" * 60)
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📍 Environment: {settings.APP_ENV}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}{settings.SWAGGER_URL}")
    print(f"🔑 API Key Required: {settings.APP_ENV == 'production'}")
    print("=" * 60 + "\n")

    # Development server warning
    if settings.DEBUG:
        print("⚠️  WARNING: Running in development mode.")
        print("   Do not use this in production!")
        print("   Use 'gunicorn' or another WSGI server for production.\n")

    # Check database connection
    try:
        with app.app_context():
            from app.models import db
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Please check your DATABASE_URL in .env file\n")
        if input("Continue anyway? (y/n): ").lower() != "y":
            sys.exit(1)

    # Run the development server
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
        use_reloader=settings.DEBUG,
        use_debugger=settings.DEBUG,
    )
