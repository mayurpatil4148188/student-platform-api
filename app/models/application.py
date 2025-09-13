"""
Application Model
Represents a university application for a student.
"""

from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Text, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.base import BaseModel, db

if TYPE_CHECKING:
    from app.models.student import Student


class Application(BaseModel):
    """
    Application model representing a university application.

    Attributes:
        student_id: Foreign key to the student
        university_name: Name of the university (required)
        program_name: Name of the program (required)
        intake: Intake period (e.g., "Jan 2026") (required)
        status: Current application status (required)
        student: Relationship to the Student model
    """

    __tablename__ = "applications"

    # =====================================================
    # Status Constants
    # =====================================================

    # Application statuses in order of progression
    STATUS_BUILDING = "Building Application"
    STATUS_SUBMITTED = "Application Submitted to University"
    STATUS_OFFER_RECEIVED = "Offer Received"
    STATUS_OFFER_ACCEPTED = "Offer Accepted by Student"
    STATUS_VISA_APPROVED = "Visa Approved"
    STATUS_DROPPED = "Dropped"

    # All valid statuses
    VALID_STATUSES = [
        STATUS_BUILDING,
        STATUS_SUBMITTED,
        STATUS_OFFER_RECEIVED,
        STATUS_OFFER_ACCEPTED,
        STATUS_VISA_APPROVED,
        STATUS_DROPPED,
    ]

    # Status weights for comparison (higher = more advanced)
    STATUS_WEIGHTS = {
        STATUS_BUILDING: 1,
        STATUS_SUBMITTED: 2,
        STATUS_OFFER_RECEIVED: 3,
        STATUS_OFFER_ACCEPTED: 4,
        STATUS_VISA_APPROVED: 5,
        STATUS_DROPPED: 0,  # Special case - excluded from calculations
    }

    # =====================================================
    # Column Definitions
    # =====================================================

    # Foreign Key
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the student",
    )

    # Required Fields
    university_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Name of the university"
    )

    program_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Name of the academic program"
    )

    intake: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Intake period (e.g., 'Jan 2026', 'Sep 2026')",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=STATUS_BUILDING,
        index=True,
        comment="Current application status",
    )

    # Optional Fields
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional notes about the application"
    )

    application_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="External application ID from university",
    )

    # Metadata Fields (inherited from BaseModel)
    # id, created_at, updated_at, is_deleted, deleted_at

    # =====================================================
    # Relationships
    # =====================================================

    student: Mapped["Student"] = relationship("Student", back_populates="applications")

    # =====================================================
    # Table Configuration
    # =====================================================

    __table_args__ = (
        Index("idx_application_student_id", "student_id"),
        Index("idx_application_status", "status"),
        Index("idx_application_intake", "intake"),
        Index("idx_application_student_status", "student_id", "status"),
        CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}", name="check_valid_status"
        ),
        {"comment": "Applications table storing university applications for students"},
    )

    # =====================================================
    # Properties and Hybrid Attributes
    # =====================================================

    @hybrid_property
    def status_weight(self) -> int:
        """Get the weight of the current status."""
        return self.STATUS_WEIGHTS.get(self.status, 0)

    @hybrid_property
    def is_active(self) -> bool:
        """Check if the application is active (not dropped)."""
        return self.status != self.STATUS_DROPPED

    @property
    def intake_year(self) -> Optional[int]:
        """Extract year from intake string."""
        try:
            # Assuming format like "Jan 2026"
            parts = self.intake.split()
            if len(parts) >= 2:
                return int(parts[-1])
        except (ValueError, AttributeError):
            pass
        return None

    @property
    def intake_month(self) -> Optional[str]:
        """Extract month from intake string."""
        try:
            # Assuming format like "Jan 2026"
            parts = self.intake.split()
            if len(parts) >= 1:
                return parts[0]
        except AttributeError:
            pass
        return None

    @property
    def display_status(self) -> str:
        """Human-readable status display."""
        return self.status.replace("_", " ").title() if self.status else "Unknown"

    @property
    def is_successful(self) -> bool:
        """Check if application has reached a successful state."""
        return self.status in [
            self.STATUS_OFFER_RECEIVED,
            self.STATUS_OFFER_ACCEPTED,
            self.STATUS_VISA_APPROVED,
        ]

    # =====================================================
    # Instance Methods
    # =====================================================

    def update_status(self, new_status: str) -> bool:
        """
        Update the application status.

        Args:
            new_status: The new status to set

        Returns:
            True if status was updated, False if invalid
        """
        if new_status not in self.VALID_STATUSES:
            return False

        self.status = new_status
        self.updated_at = datetime.utcnow()
        return True

    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if transition to new status is valid.

        Args:
            new_status: The status to transition to

        Returns:
            True if transition is valid
        """
        if new_status not in self.VALID_STATUSES:
            return False

        # Can always drop an application
        if new_status == self.STATUS_DROPPED:
            return True

        # Can't transition from dropped
        if self.status == self.STATUS_DROPPED:
            return False

        # Can only move forward in the process (except for dropping)
        current_weight = self.STATUS_WEIGHTS.get(self.status, 0)
        new_weight = self.STATUS_WEIGHTS.get(new_status, 0)

        return new_weight >= current_weight

    def to_dict(self, include_student: bool = False) -> Dict[str, Any]:
        """
        Convert application to dictionary representation.

        Args:
            include_student: Whether to include student information

        Returns:
            Dictionary representation of the application
        """
        data = {
            "id": self.id,
            "student_id": self.student_id,
            "university_name": self.university_name,
            "program_name": self.program_name,
            "intake": self.intake,
            "status": self.status,
            "status_weight": self.status_weight,
            "is_active": self.is_active,
            "is_successful": self.is_successful,
            "application_id": self.application_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_student and self.student:
            data["student"] = {
                "id": self.student.id,
                "name": self.student.name,
                "email": self.student.email,
            }

        return data

    def parse_intake_date(self) -> tuple[int, int]:
        """
        Parse intake string to (year, month_number) for comparison.

        Returns:
            Tuple of (year, month_number)
        """
        month_map = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }

        try:
            parts = self.intake.split()
            if len(parts) >= 2:
                month = parts[0][:3].capitalize()
                year = int(parts[-1])
                month_num = month_map.get(month, 12)
                return (year, month_num)
        except (ValueError, AttributeError):
            pass

        return (9999, 12)  # Far future for invalid dates

    # =====================================================
    # Class Methods
    # =====================================================

    @classmethod
    def get_by_student(
        cls, student_id: int, include_dropped: bool = False
    ) -> list["Application"]:
        """
        Get all applications for a student.

        Args:
            student_id: The student's ID
            include_dropped: Whether to include dropped applications

        Returns:
            List of applications
        """
        query = cls.query.filter_by(student_id=student_id, is_deleted=False)

        if not include_dropped:
            query = query.filter(cls.status != cls.STATUS_DROPPED)

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_status(cls, status: str) -> list["Application"]:
        """
        Get all applications with a specific status.

        Args:
            status: The status to filter by

        Returns:
            List of applications with the specified status
        """
        return (
            cls.query.filter_by(status=status, is_deleted=False)
            .order_by(cls.created_at.desc())
            .all()
        )

    @classmethod
    def validate_status(cls, status: str) -> bool:
        """
        Validate if a status value is valid.

        Args:
            status: The status to validate

        Returns:
            True if status is valid
        """
        return status in cls.VALID_STATUSES

    # =====================================================
    # Magic Methods
    # =====================================================

    def __repr__(self) -> str:
        """String representation of the Application."""
        return (
            f"<Application(id={self.id}, student_id={self.student_id}, "
            f"university='{self.university_name}', status='{self.status}')>"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.university_name} - {self.program_name} ({self.status})"

    # =====================================================
    # Validation Methods
    # =====================================================

    def validate(self) -> list[str]:
        """
        Validate application data before saving.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.university_name or len(self.university_name.strip()) < 2:
            errors.append("University name must be at least 2 characters long")

        if not self.program_name or len(self.program_name.strip()) < 2:
            errors.append("Program name must be at least 2 characters long")

        if not self.intake:
            errors.append("Intake is required")
        else:
            # Validate intake format
            try:
                parts = self.intake.split()
                if len(parts) < 2:
                    errors.append(
                        "Intake must be in format 'Month Year' (e.g., 'Jan 2026')"
                    )
                else:
                    # Check if year is valid
                    year = int(parts[-1])
                    if year < 2024 or year > 2030:
                        errors.append("Intake year must be between 2024 and 2030")
            except ValueError:
                errors.append(
                    "Invalid intake format. Use 'Month Year' (e.g., 'Jan 2026')"
                )

        if not self.status:
            errors.append("Status is required")
        elif self.status not in self.VALID_STATUSES:
            errors.append(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )

        if not self.student_id:
            errors.append("Student ID is required")

        return errors
