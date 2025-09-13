"""
Test cases for Application API endpoints.
"""

import json
import pytest
from app.models.student import Student
from app.models.application import Application


class TestApplicationAPI:
    """Test cases for Application API endpoints."""

    def test_get_applications_empty(self, client):
        """Test getting applications when none exist."""
        response = client.get("/api/v1/applications")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["applications"] == []
        assert data["data"]["pagination"]["total"] == 0

    def test_create_application_success(
        self, client, student_in_db, sample_application
    ):
        """Test creating an application successfully."""
        application_data = {"student_id": student_in_db.id, **sample_application}

        response = client.post(
            "/api/v1/applications",
            data=json.dumps(application_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert (
            data["data"]["application"]["university_name"]
            == sample_application["university_name"]
        )
        assert (
            data["data"]["application"]["program_name"]
            == sample_application["program_name"]
        )
        assert data["data"]["application"]["intake"] == sample_application["intake"]
        assert data["data"]["application"]["status"] == sample_application["status"]

    def test_create_application_missing_fields(self, client, student_in_db):
        """Test creating an application with missing required fields."""
        incomplete_data = {
            "student_id": student_in_db.id,
            "university_name": "Test University",
        }

        response = client.post(
            "/api/v1/applications",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "Missing required fields" in data["error"]["message"]

    def test_create_application_invalid_status(
        self, client, student_in_db, sample_application
    ):
        """Test creating an application with invalid status."""
        application_data = {
            "student_id": student_in_db.id,
            **sample_application,
            "status": "Invalid Status",
        }

        response = client.post(
            "/api/v1/applications",
            data=json.dumps(application_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "Invalid status" in data["error"]["message"]

    def test_create_application_student_not_found(self, client, sample_application):
        """Test creating an application for non-existent student."""
        application_data = {"student_id": 999, **sample_application}

        response = client.post(
            "/api/v1/applications",
            data=json.dumps(application_data),
            content_type="application/json",
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "Student not found" in data["error"]["message"]

    def test_get_application_by_id(self, client, application_in_db):
        """Test getting a specific application by ID."""
        response = client.get(f"/api/v1/applications/{application_in_db.id}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["application"]["id"] == application_in_db.id
        assert (
            data["data"]["application"]["university_name"]
            == application_in_db.university_name
        )

    def test_get_application_not_found(self, client):
        """Test getting a non-existent application."""
        response = client.get("/api/v1/applications/999")
        assert response.status_code == 404

    def test_update_application(self, client, application_in_db):
        """Test updating an application."""
        update_data = {
            "university_name": "Updated University",
            "program_name": application_in_db.program_name,
            "intake": application_in_db.intake,
            "status": "Application Submitted to University",
        }

        response = client.put(
            f"/api/v1/applications/{application_in_db.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["application"]["university_name"] == "Updated University"
        assert (
            data["data"]["application"]["status"]
            == "Application Submitted to University"
        )

    def test_delete_application(self, client, application_in_db):
        """Test deleting an application."""
        response = client.delete(f"/api/v1/applications/{application_in_db.id}")
        assert response.status_code == 200

        # Verify application is deleted
        response = client.get(f"/api/v1/applications/{application_in_db.id}")
        assert response.status_code == 404

    def test_get_applications_by_student(self, client, application_in_db):
        """Test getting applications filtered by student ID."""
        response = client.get(
            f"/api/v1/applications?student_id={application_in_db.student_id}"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert len(data["data"]["applications"]) == 1
        assert (
            data["data"]["applications"][0]["student_id"]
            == application_in_db.student_id
        )

    def test_get_applications_by_status(self, client, application_in_db):
        """Test getting applications filtered by status."""
        response = client.get(f"/api/v1/applications?status={application_in_db.status}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert len(data["data"]["applications"]) == 1
        assert data["data"]["applications"][0]["status"] == application_in_db.status

    def test_search_applications(self, client, application_in_db):
        """Test searching applications by university or program name."""
        response = client.get("/api/v1/applications?search=University")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert len(data["data"]["applications"]) == 1
        assert "University" in data["data"]["applications"][0]["university_name"]

    def test_pagination(self, client, app, student_in_db):
        """Test pagination for applications list."""
        with app.app_context():
            # Create multiple applications
            for i in range(15):
                application = Application(
                    student_id=student_in_db.id,
                    university_name=f"University {i}",
                    program_name=f"Program {i}",
                    intake="Jan 2026",
                    status="Building Application",
                )
                db.session.add(application)
            db.session.commit()

        # Test first page
        response = client.get("/api/v1/applications?page=1&per_page=10")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]["applications"]) == 10
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["total"] == 15

        # Test second page
        response = client.get("/api/v1/applications?page=2&per_page=10")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]["applications"]) == 5
        assert data["data"]["pagination"]["page"] == 2
