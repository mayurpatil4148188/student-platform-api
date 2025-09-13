"""
Status Calculator Service
Core business logic for calculating student's highest application status.
This is the HEART of the application - handles all status calculation logic.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from app.models import db, Student, Application
from app.core.config import settings

logger = logging.getLogger(__name__)


class StatusCalculator:
    """
    Service for calculating and updating student's highest application status.

    This class contains the critical business logic that determines:
    1. The highest status among all applications
    2. The intake date associated with that status
    3. Tie-breaking logic when multiple applications have the same status
    """

    # Status weights from Application model
    STATUS_WEIGHTS = Application.STATUS_WEIGHTS

    # Month order for intake comparison
    MONTH_ORDER = {
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
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    @classmethod
    def parse_intake_date(cls, intake: str) -> Tuple[int, int]:
        """
        Parse intake string to comparable format.

        Args:
            intake: String like "Jan 2026" or "September 2026"

        Returns:
            Tuple of (year, month_number) for comparison

        Examples:
            "Jan 2026" -> (2026, 1)
            "Sep 2026" -> (2026, 9)
            "September 2026" -> (2026, 9)
        """
        if not intake:
            return (9999, 12)  # Far future for null/invalid intakes

        try:
            intake_clean = intake.strip()
            parts = intake_clean.split()

            if len(parts) < 2:
                logger.warning(f"Invalid intake format: {intake}")
                return (9999, 12)

            # Handle both abbreviated and full month names
            month_str = parts[0]
            year_str = parts[-1]  # Take last part as year

            # Try to match month (first 3 chars for abbreviation)
            month_key = month_str[:3].capitalize()
            if month_key not in cls.MONTH_ORDER:
                # Try full month name
                month_key = month_str.capitalize()
                if month_key not in cls.MONTH_ORDER:
                    logger.warning(f"Invalid month in intake: {month_str}")
                    return (9999, 12)

            month_num = cls.MONTH_ORDER[month_key]

            # Parse year
            try:
                year = int(year_str)
                if year < 2000 or year > 2100:  # Sanity check
                    logger.warning(f"Invalid year in intake: {year_str}")
                    return (9999, 12)
            except ValueError:
                logger.warning(f"Invalid year format in intake: {year_str}")
                return (9999, 12)

            return (year, month_num)

        except Exception as e:
            logger.error(f"Error parsing intake date '{intake}': {e}")
            return (9999, 12)

    @classmethod
    def is_intake_earlier(cls, intake1: str, intake2: str) -> bool:
        """
        Compare two intake dates - returns True if intake1 is earlier.

        Args:
            intake1: First intake date string
            intake2: Second intake date string

        Returns:
            True if intake1 is earlier than intake2
        """
        date1 = cls.parse_intake_date(intake1)
        date2 = cls.parse_intake_date(intake2)
        return date1 < date2

    @classmethod
    def calculate_highest_status(
        cls, applications: List[Application]
    ) -> Dict[str, Optional[str]]:
        """
        CORE ALGORITHM - Calculate the highest status and corresponding intake.

        This is the most critical function in the entire application.

        Business Rules:
        1. Find the application with the highest status weight
        2. If multiple applications have the same highest status,
           choose the one with the earliest intake
        3. Ignore "Dropped" applications unless ALL are dropped
        4. Return None/null values if no valid applications exist

        Args:
            applications: List of Application objects for a student

        Returns:
            Dictionary with 'highest_status' and 'highest_intake'
        """
        logger.debug(f"Calculating highest status for {len(applications)} applications")

        # Edge Case 1: No applications at all
        if not applications:
            logger.debug("No applications found - returning None values")
            return {"highest_status": None, "highest_intake": None}

        # Filter out dropped applications and soft-deleted records
        active_applications = [
            app
            for app in applications
            if app.status != "Dropped" and not app.is_deleted
        ]

        # Edge Case 2: All applications are dropped or deleted
        if not active_applications:
            logger.debug(
                "All applications are dropped or deleted - returning None values"
            )
            return {"highest_status": None, "highest_intake": None}

        # Find the maximum weight among active applications
        max_weight = max(
            cls.STATUS_WEIGHTS.get(app.status, 0) for app in active_applications
        )

        logger.debug(f"Maximum status weight found: {max_weight}")

        # Get all applications with the highest weight
        best_applications = [
            app
            for app in active_applications
            if cls.STATUS_WEIGHTS.get(app.status, 0) == max_weight
        ]

        # Edge Case 3: Single application with highest status
        if len(best_applications) == 1:
            best_app = best_applications[0]
            logger.debug(
                f"Single best application: {best_app.status} - {best_app.intake}"
            )
            return {
                "highest_status": best_app.status,
                "highest_intake": best_app.intake,
            }

        # Edge Case 4: Multiple applications with same highest status
        # Apply tie-breaker: choose the earliest intake
        logger.debug(f"Multiple applications with same status - applying tie-breaker")

        best_app = min(
            best_applications, key=lambda app: cls.parse_intake_date(app.intake)
        )

        logger.debug(
            f"Selected application after tie-breaker: {best_app.status} - {best_app.intake}"
        )

        return {"highest_status": best_app.status, "highest_intake": best_app.intake}

    @classmethod
    def update_student_highest_status(cls, student_id: int) -> Dict[str, Any]:
        """
        Update a student's highest status and intake based on their applications.

        This method should be called whenever an application is:
        - Created
        - Updated
        - Deleted

        Args:
            student_id: The ID of the student to update

        Returns:
            Dictionary with update results and new values
        """
        logger.info(f"Updating highest status for student {student_id}")

        try:
            # Start a database transaction for consistency
            with db.session.begin_nested():
                # Get the student
                student = Student.query.get(student_id)
                if not student:
                    logger.error(f"Student {student_id} not found")
                    return {"success": False, "error": "Student not found"}

                # Get all applications for the student
                applications = Application.query.filter_by(
                    student_id=student_id, is_deleted=False
                ).all()

                logger.debug(
                    f"Found {len(applications)} applications for student {student_id}"
                )

                # Calculate the new highest status
                result = cls.calculate_highest_status(applications)

                # Update the student record
                old_status = student.highest_status
                old_intake = student.highest_intake

                student.highest_status = result["highest_status"]
                student.highest_intake = result["highest_intake"]
                student.updated_at = datetime.utcnow()

                # Commit the transaction
                db.session.commit()

                logger.info(
                    f"Updated student {student_id}: "
                    f"status '{old_status}' -> '{result['highest_status']}', "
                    f"intake '{old_intake}' -> '{result['highest_intake']}'"
                )

                return {
                    "success": True,
                    "student_id": student_id,
                    "old_status": old_status,
                    "old_intake": old_intake,
                    "new_status": result["highest_status"],
                    "new_intake": result["highest_intake"],
                    "applications_count": len(applications),
                }

        except Exception as e:
            logger.error(f"Error updating student {student_id} highest status: {e}")
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @classmethod
    def bulk_update_students(cls, student_ids: List[int]) -> Dict[str, Any]:
        """
        Update highest status for multiple students.

        Args:
            student_ids: List of student IDs to update

        Returns:
            Dictionary with update results
        """
        logger.info(f"Bulk updating {len(student_ids)} students")

        results = {"success": 0, "failed": 0, "errors": []}

        for student_id in student_ids:
            result = cls.update_student_highest_status(student_id)
            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(
                    {"student_id": student_id, "error": result.get("error")}
                )

        logger.info(
            f"Bulk update completed: {results['success']} success, {results['failed']} failed"
        )
        return results

    @classmethod
    def validate_status(cls, status: str) -> bool:
        """
        Validate if a status value is valid.

        Args:
            status: The status to validate

        Returns:
            True if status is valid, False otherwise
        """
        return status in cls.STATUS_WEIGHTS

    @classmethod
    def validate_intake_format(cls, intake: str) -> bool:
        """
        Validate intake format (e.g., "Jan 2026").

        Args:
            intake: The intake string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            year, month = cls.parse_intake_date(intake)
            # Check if it's not the default "invalid" value
            return (year, month) != (9999, 12)
        except Exception:
            return False

    @classmethod
    def get_status_weight(cls, status: str) -> int:
        """
        Get the weight of a status.

        Args:
            status: The status string

        Returns:
            Weight of the status (0 if invalid)
        """
        return cls.STATUS_WEIGHTS.get(status, 0)

    @classmethod
    def get_status_progression(cls) -> List[str]:
        """
        Get the list of statuses in order of progression.

        Returns:
            List of statuses ordered by weight
        """
        return sorted(cls.STATUS_WEIGHTS.keys(), key=lambda s: cls.STATUS_WEIGHTS[s])

    @classmethod
    def can_transition(cls, current_status: str, new_status: str) -> bool:
        """
        Check if a status transition is valid.

        Args:
            current_status: Current application status
            new_status: Proposed new status

        Returns:
            True if transition is allowed
        """
        # Can always drop an application
        if new_status == "Dropped":
            return True

        # Can't transition from dropped
        if current_status == "Dropped":
            return False

        # Can only move forward or stay same
        current_weight = cls.get_status_weight(current_status)
        new_weight = cls.get_status_weight(new_status)

        return new_weight >= current_weight

    @classmethod
    def get_statistics(cls, student_id: int) -> Dict[str, Any]:
        """
        Get statistics about a student's applications.

        Args:
            student_id: The student's ID

        Returns:
            Dictionary with application statistics
        """
        applications = Application.query.filter_by(
            student_id=student_id, is_deleted=False
        ).all()

        if not applications:
            return {
                "total_applications": 0,
                "active_applications": 0,
                "dropped_applications": 0,
                "status_breakdown": {},
                "earliest_intake": None,
                "latest_intake": None,
            }

        status_breakdown = {}
        active_count = 0
        dropped_count = 0
        intakes = []

        for app in applications:
            # Count by status
            status_breakdown[app.status] = status_breakdown.get(app.status, 0) + 1

            # Count active vs dropped
            if app.status == "Dropped":
                dropped_count += 1
            else:
                active_count += 1

            # Collect intakes
            intakes.append(cls.parse_intake_date(app.intake))

        # Find earliest and latest intakes
        intakes = [i for i in intakes if i != (9999, 12)]  # Filter invalid
        earliest = min(intakes) if intakes else None
        latest = max(intakes) if intakes else None

        # Format intake dates back to string
        def format_intake(date_tuple):
            if not date_tuple:
                return None
            year, month = date_tuple
            month_names = {v: k for k, v in cls.MONTH_ORDER.items() if len(k) == 3}
            month_name = month_names.get(month, "Unknown")
            return f"{month_name} {year}"

        return {
            "total_applications": len(applications),
            "active_applications": active_count,
            "dropped_applications": dropped_count,
            "status_breakdown": status_breakdown,
            "earliest_intake": format_intake(earliest),
            "latest_intake": format_intake(latest),
            "highest_status": Student.query.get(student_id).highest_status,
            "highest_intake": Student.query.get(student_id).highest_intake,
        }


# Create a singleton instance
status_calculator = StatusCalculator()
