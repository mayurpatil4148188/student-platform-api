"""
Test cases for Status Calculator service.
"""

import pytest
from app.services.status_calculator import StatusCalculator
from app.models.student import Student
from app.models.application import Application


class TestStatusCalculator:
    """Test cases for Status Calculator service."""

    def test_parse_intake_date_valid(self):
        """Test parsing valid intake dates."""
        # Test abbreviated months
        assert StatusCalculator.parse_intake_date("Jan 2026") == (2026, 1)
        assert StatusCalculator.parse_intake_date("Feb 2026") == (2026, 2)
        assert StatusCalculator.parse_intake_date("Dec 2026") == (2026, 12)

        # Test full month names
        assert StatusCalculator.parse_intake_date("January 2026") == (2026, 1)
        assert StatusCalculator.parse_intake_date("December 2026") == (2026, 12)

    def test_parse_intake_date_invalid(self):
        """Test parsing invalid intake dates."""
        # Invalid format
        assert StatusCalculator.parse_intake_date("Invalid") == (9999, 12)
        assert StatusCalculator.parse_intake_date("") == (9999, 12)
        assert StatusCalculator.parse_intake_date(None) == (9999, 12)

        # Invalid month
        assert StatusCalculator.parse_intake_date("Invalid 2026") == (9999, 12)

        # Invalid year
        assert StatusCalculator.parse_intake_date("Jan 1999") == (9999, 12)
        assert StatusCalculator.parse_intake_date("Jan 2101") == (9999, 12)

    def test_is_intake_earlier(self):
        """Test intake date comparison."""
        assert StatusCalculator.is_intake_earlier("Jan 2026", "Feb 2026") == True
        assert StatusCalculator.is_intake_earlier("Feb 2026", "Jan 2026") == False
        assert StatusCalculator.is_intake_earlier("Jan 2026", "Jan 2026") == False
        assert StatusCalculator.is_intake_earlier("Dec 2025", "Jan 2026") == True

    def test_calculate_highest_status_no_applications(self):
        """Test calculating highest status with no applications."""
        result = StatusCalculator.calculate_highest_status([])
        assert result["highest_status"] is None
        assert result["highest_intake"] is None

    def test_calculate_highest_status_single_application(self):
        """Test calculating highest status with single application."""
        application = Application(
            university_name="Test University",
            program_name="Test Program",
            intake="Jan 2026",
            status="Offer Received",
        )

        result = StatusCalculator.calculate_highest_status([application])
        assert result["highest_status"] == "Offer Received"
        assert result["highest_intake"] == "Jan 2026"

    def test_calculate_highest_status_multiple_applications(self):
        """Test calculating highest status with multiple applications."""
        applications = [
            Application(
                university_name="University 1",
                program_name="Program 1",
                intake="Jan 2026",
                status="Building Application",
            ),
            Application(
                university_name="University 2",
                program_name="Program 2",
                intake="Feb 2026",
                status="Offer Received",
            ),
            Application(
                university_name="University 3",
                program_name="Program 3",
                intake="Mar 2026",
                status="Application Submitted to University",
            ),
        ]

        result = StatusCalculator.calculate_highest_status(applications)
        assert result["highest_status"] == "Offer Received"
        assert result["highest_intake"] == "Feb 2026"

    def test_calculate_highest_status_tie_breaker(self):
        """Test tie-breaker logic when multiple applications have same status."""
        applications = [
            Application(
                university_name="University 1",
                program_name="Program 1",
                intake="Sep 2026",
                status="Offer Received",
            ),
            Application(
                university_name="University 2",
                program_name="Program 2",
                intake="Jan 2026",
                status="Offer Received",
            ),
        ]

        result = StatusCalculator.calculate_highest_status(applications)
        assert result["highest_status"] == "Offer Received"
        assert result["highest_intake"] == "Jan 2026"  # Earlier intake wins

    def test_calculate_highest_status_with_dropped(self):
        """Test calculating highest status with dropped applications."""
        applications = [
            Application(
                university_name="University 1",
                program_name="Program 1",
                intake="Jan 2026",
                status="Dropped",
            ),
            Application(
                university_name="University 2",
                program_name="Program 2",
                intake="Feb 2026",
                status="Offer Received",
            ),
        ]

        result = StatusCalculator.calculate_highest_status(applications)
        assert result["highest_status"] == "Offer Received"
        assert result["highest_intake"] == "Feb 2026"

    def test_calculate_highest_status_all_dropped(self):
        """Test calculating highest status when all applications are dropped."""
        applications = [
            Application(
                university_name="University 1",
                program_name="Program 1",
                intake="Jan 2026",
                status="Dropped",
            ),
            Application(
                university_name="University 2",
                program_name="Program 2",
                intake="Feb 2026",
                status="Dropped",
            ),
        ]

        result = StatusCalculator.calculate_highest_status(applications)
        assert result["highest_status"] is None
        assert result["highest_intake"] is None

    def test_validate_status(self):
        """Test status validation."""
        assert StatusCalculator.validate_status("Building Application") == True
        assert StatusCalculator.validate_status("Visa Approved") == True
        assert StatusCalculator.validate_status("Invalid Status") == False

    def test_validate_intake_format(self):
        """Test intake format validation."""
        assert StatusCalculator.validate_intake_format("Jan 2026") == True
        assert StatusCalculator.validate_intake_format("September 2026") == True
        assert StatusCalculator.validate_intake_format("Invalid") == False
        assert StatusCalculator.validate_intake_format("") == False

    def test_get_status_weight(self):
        """Test getting status weights."""
        assert StatusCalculator.get_status_weight("Building Application") == 1
        assert StatusCalculator.get_status_weight("Visa Approved") == 5
        assert StatusCalculator.get_status_weight("Invalid Status") == 0

    def test_can_transition(self):
        """Test status transition validation."""
        # Can move forward
        assert (
            StatusCalculator.can_transition(
                "Building Application", "Application Submitted to University"
            )
            == True
        )
        assert (
            StatusCalculator.can_transition(
                "Application Submitted to University", "Offer Received"
            )
            == True
        )

        # Can stay same
        assert (
            StatusCalculator.can_transition("Offer Received", "Offer Received") == True
        )

        # Can always drop
        assert (
            StatusCalculator.can_transition("Building Application", "Dropped") == True
        )
        assert StatusCalculator.can_transition("Visa Approved", "Dropped") == True

        # Can't move backward
        assert (
            StatusCalculator.can_transition("Offer Received", "Building Application")
            == False
        )

        # Can't transition from dropped
        assert (
            StatusCalculator.can_transition("Dropped", "Building Application") == False
        )
