"""
API package for the student platform application.
"""

from flask_restx import Api
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Create API instance
api = Api(
    api_bp,
    version="1.0",
    title="Student Platform API",
    description="A comprehensive API for managing students and their university applications",
    doc="/docs/",
    prefix="/v1",
)

# Import and register namespaces
from app.api.v1.students import students_ns
from app.api.v1.applications import applications_ns
from app.api.v1.health import health_ns

api.add_namespace(students_ns)
api.add_namespace(applications_ns)
api.add_namespace(health_ns)
