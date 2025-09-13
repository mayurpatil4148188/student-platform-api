"""
Base Model
Abstract base class for all database models.
"""

from datetime import datetime
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# Initialize SQLAlchemy with custom base class
db = SQLAlchemy(model_class=Base)


class BaseModel(db.Model):
    """
    Abstract base model with common fields and methods.
    All models should inherit from this class.
    """

    __abstract__ = True

    # =====================================================
    # Common Fields
    # =====================================================

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="Primary key"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Timestamp when record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Timestamp when record was last updated",
    )

    # Soft delete fields
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True, comment="Soft delete flag"
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        comment="Timestamp when record was soft deleted",
    )

    # =====================================================
    # Instance Methods
    # =====================================================

    def save(self) -> "BaseModel":
        """
        Save the current instance to the database.

        Returns:
            The saved instance
        """
        db.session.add(self)
        db.session.commit()
        return self

    def update(self, **kwargs) -> "BaseModel":
        """
        Update instance attributes and save to database.

        Args:
            **kwargs: Attributes to update

        Returns:
            The updated instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self.save()

    def delete(self, soft: bool = True) -> None:
        """
        Delete the instance from the database.

        Args:
            soft: If True, perform soft delete; if False, permanent delete
        """
        if soft:
            self.soft_delete()
        else:
            self.hard_delete()

    def soft_delete(self) -> None:
        """
        Soft delete the instance (mark as deleted but keep in database).
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.save()

    def hard_delete(self) -> None:
        """
        Permanently delete the instance from the database.
        """
        db.session.delete(self)
        db.session.commit()

    def restore(self) -> "BaseModel":
        """
        Restore a soft-deleted instance.

        Returns:
            The restored instance
        """
        self.is_deleted = False
        self.deleted_at = None
        return self.save()

    def refresh(self) -> "BaseModel":
        """
        Refresh the instance from the database.

        Returns:
            The refreshed instance
        """
        db.session.refresh(self)
        return self

    # =====================================================
    # Class Methods
    # =====================================================

    @classmethod
    def get_by_id(cls, id: int, include_deleted: bool = False) -> Optional["BaseModel"]:
        """
        Get an instance by ID.

        Args:
            id: The ID to search for
            include_deleted: Whether to include soft-deleted records

        Returns:
            The instance or None if not found
        """
        query = cls.query.filter_by(id=id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.first()

    @classmethod
    def get_all(cls, include_deleted: bool = False) -> list["BaseModel"]:
        """
        Get all instances.

        Args:
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of all instances
        """
        query = cls.query
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.all()

    @classmethod
    def create(cls, **kwargs) -> "BaseModel":
        """
        Create a new instance and save to database.

        Args:
            **kwargs: Attributes for the new instance

        Returns:
            The created instance
        """
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def bulk_create(cls, instances_data: list[dict]) -> list["BaseModel"]:
        """
        Create multiple instances in a single transaction.

        Args:
            instances_data: List of dictionaries with instance data

        Returns:
            List of created instances
        """
        instances = [cls(**data) for data in instances_data]
        db.session.bulk_save_objects(instances, return_defaults=True)
        db.session.commit()
        return instances

    @classmethod
    def exists(cls, **kwargs) -> bool:
        """
        Check if a record exists with the given criteria.

        Args:
            **kwargs: Filter criteria

        Returns:
            True if exists, False otherwise
        """
        return cls.query.filter_by(is_deleted=False, **kwargs).first() is not None

    @classmethod
    def count(cls, include_deleted: bool = False, **kwargs) -> int:
        """
        Count records matching the criteria.

        Args:
            include_deleted: Whether to include soft-deleted records
            **kwargs: Additional filter criteria

        Returns:
            Count of matching records
        """
        query = cls.query.filter_by(**kwargs)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.count()

    # =====================================================
    # Transaction Management
    # =====================================================

    @staticmethod
    def begin_transaction():
        """Begin a new database transaction."""
        return db.session.begin_nested()

    @staticmethod
    def commit():
        """Commit the current transaction."""
        db.session.commit()

    @staticmethod
    def rollback():
        """Rollback the current transaction."""
        db.session.rollback()

    @staticmethod
    def flush():
        """Flush pending changes without committing."""
        db.session.flush()
