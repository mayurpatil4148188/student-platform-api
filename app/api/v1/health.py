"""
Health check endpoints for monitoring and production readiness.
"""

from flask import jsonify, current_app
from flask_restx import Namespace, Resource
from sqlalchemy import text
from app import db

# Create namespace for health endpoints
health_ns = Namespace("health", description="Health check endpoints")


@health_ns.route("/")
class HealthCheck(Resource):
    """Basic health check endpoint."""

    def get(self):
        """Return basic health status."""
        return {
            "status": "healthy",
            "service": "Student Platform API",
            "version": "1.0.0",
        }


@health_ns.route("/detailed")
class DetailedHealthCheck(Resource):
    """Detailed health check with database connectivity."""

    def get(self):
        """Return detailed health status including database connectivity."""
        health_status = {
            "status": "healthy",
            "service": "Student Platform API",
            "version": "1.0.0",
            "checks": {},
        }

        # Check database connectivity
        try:
            db.session.execute(text("SELECT 1"))
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful",
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
            }
            health_status["status"] = "unhealthy"

        # Check Redis connectivity (if configured)
        try:
            from flask_limiter import Limiter
            from flask_limiter.util import get_remote_address

            # Try to get rate limiter instance
            limiter = current_app.extensions.get("limiter")
            if limiter:
                # Test Redis connection by checking storage
                storage = limiter.storage
                if hasattr(storage, "get"):
                    storage.get("health_check")
                health_status["checks"]["redis"] = {
                    "status": "healthy",
                    "message": "Redis connection successful",
                }
            else:
                health_status["checks"]["redis"] = {
                    "status": "not_configured",
                    "message": "Redis not configured",
                }
        except Exception as e:
            health_status["checks"]["redis"] = {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}",
            }

        # Check application configuration
        health_status["checks"]["configuration"] = {
            "status": "healthy",
            "debug_mode": current_app.debug,
            "environment": current_app.config.get("ENV", "unknown"),
        }

        return health_status


@health_ns.route("/ready")
class ReadinessCheck(Resource):
    """Readiness check for Kubernetes/Docker health checks."""

    def get(self):
        """Return readiness status."""
        try:
            # Check if database is accessible
            db.session.execute(text("SELECT 1"))
            return {"status": "ready"}, 200
        except Exception as e:
            return {"status": "not_ready", "error": str(e)}, 503


@health_ns.route("/live")
class LivenessCheck(Resource):
    """Liveness check for Kubernetes/Docker health checks."""

    def get(self):
        """Return liveness status."""
        return {"status": "alive"}, 200
