"""
Test configuration and fixtures.
"""

import pytest
import os
import tempfile
from app import create_app, db
from app.models.student import Student
from app.models.application import Application


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()

    # Create app with test configuration
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    # Create the database
    with app.app_context():
        db.create_all()

    yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_student():
    """Create a sample student for testing."""
    return {"name": "John Doe", "email": "john.doe@example.com", "phone": "+1234567890"}


@pytest.fixture
def sample_application():
    """Create a sample application for testing."""
    return {
        "university_name": "University of California",
        "program_name": "Computer Science",
        "intake": "Jan 2026",
        "status": "Building Application",
    }


@pytest.fixture
def student_in_db(app, sample_student):
    """Create a student in the database."""
    with app.app_context():
        student = Student(**sample_student)
        db.session.add(student)
        db.session.commit()
        return student


@pytest.fixture
def application_in_db(app, student_in_db, sample_application):
    """Create an application in the database."""
    with app.app_context():
        application = Application(student_id=student_in_db.id, **sample_application)
        db.session.add(application)
        db.session.commit()
        return application
