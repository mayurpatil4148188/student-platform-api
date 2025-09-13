"""
Test cases for Student API endpoints.
"""

import json
import pytest
from app.models.student import Student
from app.models.application import Application


class TestStudentAPI:
    """Test cases for Student API endpoints."""

    def test_get_students_empty(self, client):
        """Test getting students when none exist."""
        response = client.get("/api/v1/students/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["students"] == []
        assert data["data"]["pagination"]["total"] == 0

    def test_create_student_success(self, client, sample_student):
        """Test creating a student successfully."""
        response = client.post(
            "/api/v1/students/",
            data=json.dumps(sample_student),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["student"]["name"] == sample_student["name"]
        assert data["data"]["student"]["email"] == sample_student["email"]
        assert data["data"]["student"]["phone"] == sample_student["phone"]

    def test_create_student_missing_fields(self, client):
        """Test creating a student with missing required fields."""
        incomplete_data = {"name": "John Doe"}

        response = client.post(
            "/api/v1/students/",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )

        assert response.status_code == 422
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "Missing required fields" in data["error"]["message"]

    def test_create_student_duplicate_email(self, client, sample_student):
        """Test creating a student with duplicate email."""
        # Create first student
        client.post(
            "/api/v1/students/",
            data=json.dumps(sample_student),
            content_type="application/json",
        )

        # Try to create second student with same email
        response = client.post(
            "/api/v1/students/",
            data=json.dumps(sample_student),
            content_type="application/json",
        )

        assert response.status_code == 409
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "already exists" in data["error"]["message"]

    def test_get_student_by_id(self, client, student_in_db):
        """Test getting a specific student by ID."""
        response = client.get(f"/api/v1/students/{student_in_db.id}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["student"]["id"] == student_in_db.id
        assert data["data"]["student"]["name"] == student_in_db.name

    def test_get_student_not_found(self, client):
        """Test getting a non-existent student."""
        response = client.get("/api/v1/students/999")
        assert response.status_code == 404

    def test_update_student(self, client, student_in_db):
        """Test updating a student."""
        update_data = {
            "name": "Jane Doe",
            "email": student_in_db.email,
            "phone": "+9876543210",
        }

        response = client.put(
            f"/api/v1/students/{student_in_db.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["data"]["student"]["name"] == "Jane Doe"
        assert data["data"]["student"]["phone"] == "+9876543210"

    def test_delete_student(self, client, student_in_db):
        """Test deleting a student."""
        response = client.delete(f"/api/v1/students/{student_in_db.id}")
        assert response.status_code == 200

        # Verify student is deleted
        response = client.get(f"/api/v1/students/{student_in_db.id}")
        assert response.status_code == 404

    def test_get_student_status(self, client, student_in_db):
        """Test getting student's highest status and intake."""
        response = client.get(f"/api/v1/students/{student_in_db.id}/status")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "highest_status" in data["data"]
        assert "highest_intake" in data["data"]

    def test_search_students(self, client, student_in_db):
        """Test searching students by name or email."""
        response = client.get("/api/v1/students/?search=John")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert len(data["data"]["students"]) == 1
        assert data["data"]["students"][0]["name"] == "John Doe"

    def test_pagination(self, client, app):
        """Test pagination for students list."""
        with app.app_context():
            # Create multiple students
            for i in range(15):
                student = Student(
                    name=f"Student {i}",
                    email=f"student{i}@example.com",
                    phone=f"+123456789{i:02d}",
                )
                db.session.add(student)
            db.session.commit()

        # Test first page
        response = client.get("/api/v1/students/?page=1&per_page=10")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]["students"]) == 10
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["total"] == 15

        # Test second page
        response = client.get("/api/v1/students/?page=2&per_page=10")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]["students"]) == 5
        assert data["data"]["pagination"]["page"] == 2
