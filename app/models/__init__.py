# =====================================================
# app/models/__init__.py
# =====================================================
"""
Models Package
Exports all database models and the database instance.
"""

from app.models.base import db, BaseModel
from app.models.student import Student
from app.models.application import Application

__all__ = ["db", "BaseModel", "Student", "Application"]
