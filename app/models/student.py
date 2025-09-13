"""
Student Model
Represents a student in the platform with their applications.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.base import BaseModel, db

if TYPE_CHECKING:
    from app.models.application import Application


class Student(BaseModel):
    """
    Student model representing a student with university applications.

    Attributes:
        name: Student's full name (required)
        email: Student's email address (required, unique)
        phone: Student's phone number (required)
        highest_status: Automatically calculated highest application status
        highest_intake: Intake date of the highest status application
        applications: List of related applications
    """

    __tablename__ = "students"

    # =====================================================
    # Column Definitions
    # =====================================================

    # Basic Information (Required Fields)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Student's full name"
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Student's email address (unique)",
    )

    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Student's phone number with country code"
    )

    # Calculated Fields (Auto-updated)
    highest_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        comment="Highest application status among all applications",
    )

    highest_intake: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="Intake date of the highest status application",
    )

    # Additional Fields (Optional)
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Internal notes about the student"
    )

    # Metadata Fields (inherited from BaseModel)
    # id, created_at, updated_at, is_deleted, deleted_at

    # =====================================================
    # Relationships
    # =====================================================

    applications: Mapped[List["Application"]] = relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="Application.created_at.desc()",
    )

    # =====================================================
    # Indexes
    # =====================================================

    __table_args__ = (
        Index("idx_student_email", "email"),
        Index("idx_student_highest_status", "highest_status"),
        Index("idx_student_created_at", "created_at"),
        {"comment": "Students table storing student information and calculated status"},
    )

    # =====================================================
    # Properties and Hybrid Attributes
    # =====================================================

    @hybrid_property
    def active_applications_count(self) -> int:
        """Count of non-dropped applications."""
        if self.applications:
            total = self.applications.filter_by(is_deleted=False).count()
            dropped = self.applications.filter_by(is_deleted=False, status="Dropped").count()
            return total - dropped
        return 0

    @hybrid_property
    def total_applications_count(self) -> int:
        """Total count of all applications."""
        if self.applications:
            return self.applications.filter_by(is_deleted=False).count()
        return 0

    @property
    def has_active_applications(self) -> bool:
        """Check if student has any active (non-dropped) applications."""
        return self.active_applications_count > 0

    @property
    def display_name(self) -> str:
        """Formatted display name."""
        return self.name.title() if self.name else ""

    # =====================================================
    # Instance Methods
    # =====================================================

    def update_highest_status(
        self, status: Optional[str], intake: Optional[str]
    ) -> None:
        """
        Update the student's highest status and intake.

        Args:
            status: The new highest status
            intake: The intake date for the highest status
        """
        self.highest_status = status
        self.highest_intake = intake
        self.updated_at = datetime.utcnow()

    def get_applications_by_status(self, status: str) -> List["Application"]:
        """
        Get all applications with a specific status.

        Args:
            status: The application status to filter by

        Returns:
            List of applications with the specified status
        """
        return self.applications.filter_by(status=status, is_deleted=False).all()

    def get_latest_application(self) -> Optional["Application"]:
        """
        Get the most recently created application.

        Returns:
            The latest application or None if no applications exist
        """
        return (
            self.applications.filter_by(is_deleted=False)
            .order_by(Application.created_at.desc())
            .first()
        )

    def to_dict(self, include_applications: bool = False) -> dict:
        """
        Convert student to dictionary representation.

        Args:
            include_applications: Whether to include applications in the response

        Returns:
            Dictionary representation of the student
        """
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "highest_status": self.highest_status,
            "highest_intake": self.highest_intake,
            "active_applications_count": self.active_applications_count,
            "total_applications_count": self.total_applications_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_applications:
            data["applications"] = [
                app.to_dict()
                for app in self.applications.filter_by(is_deleted=False).all()
            ]

        return data

    def soft_delete(self) -> None:
        """
        Soft delete the student and all associated applications.
        """
        super().soft_delete()
        for application in self.applications:
            application.soft_delete()

    # =====================================================
    # Class Methods
    # =====================================================

    @classmethod
    def find_by_email(cls, email: str) -> Optional["Student"]:
        """
        Find a student by email address.

        Args:
            email: Email address to search for

        Returns:
            Student instance or None if not found
        """
        return cls.query.filter_by(email=email, is_deleted=False).first()

    @classmethod
    def search(cls, query: str) -> List["Student"]:
        """
        Search students by name or email.

        Args:
            query: Search query string

        Returns:
            List of matching students
        """
        search_filter = f"%{query}%"
        return cls.query.filter(
            db.and_(
                cls.is_deleted == False,
                db.or_(cls.name.ilike(search_filter), cls.email.ilike(search_filter)),
            )
        ).all()

    # =====================================================
    # Magic Methods
    # =====================================================

    def __repr__(self) -> str:
        """String representation of the Student."""
        return f"<Student(id={self.id}, name='{self.name}', email='{self.email}', highest_status='{self.highest_status}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.email})"

    # =====================================================
    # Validation Methods
    # =====================================================

    def validate(self) -> List[str]:
        """
        Validate student data before saving.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.name or len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")

        if not self.email or "@" not in self.email:
            errors.append("Valid email address is required")

        if not self.phone or len(self.phone) < 10:
            errors.append("Phone number must be at least 10 digits")

        # Check for duplicate email (excluding soft-deleted records)
        if self.email:
            existing = Student.query.filter(
                Student.email == self.email,
                Student.id != self.id,
                Student.is_deleted == False,
            ).first()
            if existing:
                errors.append(f"Email '{self.email}' is already registered")

        return errors
