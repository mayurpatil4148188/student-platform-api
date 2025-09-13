"""
Example Test File - Student Platform API
This file demonstrates testing patterns and serves as a template for new tests.
"""

import pytest
from datetime import datetime
from app.models import Student, Application, db
from app.services.status_calculator import StatusCalculator


class TestExamplePatterns:
    """Example test class demonstrating various testing patterns."""
    
    def test_basic_assertion(self):
        """Example of basic assertion testing."""
        # Arrange
        expected = "Hello World"
        
        # Act
        result = "Hello World"
        
        # Assert
        assert result == expected
        assert len(result) == 11
        assert "Hello" in result
    
    def test_list_operations(self):
        """Example of testing list operations."""
        # Arrange
        numbers = [1, 2, 3, 4, 5]
        
        # Act
        doubled = [x * 2 for x in numbers]
        
        # Assert
        assert len(doubled) == 5
        assert doubled[0] == 2
        assert doubled[-1] == 10
        assert all(x % 2 == 0 for x in doubled)
    
    def test_exception_handling(self):
        """Example of testing exception handling."""
        # Arrange
        def divide(a, b):
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        
        # Act & Assert
        assert divide(10, 2) == 5.0
        
        with pytest.raises(ValueError) as exc_info:
            divide(10, 0)
        
        assert "Cannot divide by zero" in str(exc_info.value)


@pytest.mark.unit
class TestStudentModel:
    """Unit tests for Student model."""
    
    def test_student_creation(self, db_session):
        """Test creating a new student."""
        # Arrange
        student_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        }
        
        # Act
        student = Student(**student_data)
        db_session.add(student)
        db_session.commit()
        
        # Assert
        assert student.id is not None
        assert student.name == 'John Doe'
        assert student.email == 'john@example.com'
        assert student.phone == '+1234567890'
        assert student.created_at is not None
        assert student.is_deleted is False
    
    def test_student_email_uniqueness(self, db_session):
        """Test that student emails must be unique."""
        # Arrange
        email = 'unique@example.com'
        student1 = Student(name='Student 1', email=email, phone='+1111111111')
        student2 = Student(name='Student 2', email=email, phone='+2222222222')
        
        # Act
        db_session.add(student1)
        db_session.commit()
        
        # Assert
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.add(student2)
            db_session.commit()
    
    def test_student_validation(self):
        """Test student data validation."""
        # Arrange
        invalid_student = Student(
            name='A',  # Too short
            email='invalid-email',  # Invalid format
            phone='123'  # Too short
        )
        
        # Act
        errors = invalid_student.validate()
        
        # Assert
        assert len(errors) > 0
        assert any('name' in error.lower() for error in errors)
        assert any('email' in error.lower() for error in errors)
        assert any('phone' in error.lower() for error in errors)


@pytest.mark.api
class TestStudentAPI:
    """API tests for Student endpoints."""
    
    def test_create_student_success(self, client, db_session):
        """Test successful student creation via API."""
        # Arrange
        student_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+1234567890'
        }
        
        # Act
        response = client.post('/api/v1/students/', json=student_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Jane Smith'
        assert data['email'] == 'jane@example.com'
        assert 'id' in data
        assert 'created_at' in data
    
    def test_create_student_validation_error(self, client, db_session):
        """Test student creation with validation errors."""
        # Arrange
        invalid_data = {
            'name': 'A',  # Too short
            'email': 'invalid-email',
            'phone': '123'  # Too short
        }
        
        # Act
        response = client.post('/api/v1/students/', json=invalid_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'message' in data
    
    def test_get_student_success(self, client, db_session):
        """Test successful student retrieval."""
        # Arrange
        student = Student(
            name='Test Student',
            email='test@example.com',
            phone='+1234567890'
        )
        db_session.add(student)
        db_session.commit()
        
        # Act
        response = client.get(f'/api/v1/students/{student.id}')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Test Student'
        assert data['email'] == 'test@example.com'
    
    def test_get_student_not_found(self, client, db_session):
        """Test retrieving non-existent student."""
        # Act
        response = client.get('/api/v1/students/99999')
        
        # Assert
        assert response.status_code == 404


@pytest.mark.service
class TestStatusCalculator:
    """Tests for StatusCalculator service."""
    
    def test_calculate_highest_status_single_application(self):
        """Test status calculation with single application."""
        # Arrange
        applications = [
            {'status': 'Offer Received', 'intake': 'Sep 2026'}
        ]
        
        # Act
        highest_status, highest_intake = StatusCalculator.calculate_highest_status(applications)
        
        # Assert
        assert highest_status == 'Offer Received'
        assert highest_intake == 'Sep 2026'
    
    def test_calculate_highest_status_multiple_applications(self):
        """Test status calculation with multiple applications."""
        # Arrange
        applications = [
            {'status': 'Building Application', 'intake': 'Jan 2026'},
            {'status': 'Offer Received', 'intake': 'Sep 2026'},
            {'status': 'Application Submitted', 'intake': 'Jan 2026'}
        ]
        
        # Act
        highest_status, highest_intake = StatusCalculator.calculate_highest_status(applications)
        
        # Assert
        assert highest_status == 'Offer Received'
        assert highest_intake == 'Sep 2026'
    
    def test_calculate_highest_status_empty_list(self):
        """Test status calculation with empty application list."""
        # Arrange
        applications = []
        
        # Act
        highest_status, highest_intake = StatusCalculator.calculate_highest_status(applications)
        
        # Assert
        assert highest_status is None
        assert highest_intake is None


@pytest.mark.integration
class TestStudentApplicationWorkflow:
    """Integration tests for student-application workflow."""
    
    def test_complete_student_application_workflow(self, client, db_session):
        """Test complete workflow from student creation to status calculation."""
        # Arrange
        student_data = {
            'name': 'Workflow Test Student',
            'email': 'workflow@example.com',
            'phone': '+1234567890'
        }
        
        # Act 1: Create student
        response = client.post('/api/v1/students/', json=student_data)
        assert response.status_code == 201
        student = response.get_json()
        
        # Act 2: Create application
        application_data = {
            'student_id': student['id'],
            'university_name': 'Test University',
            'program_name': 'Computer Science',
            'intake': 'Sep 2026',
            'status': 'Offer Received'
        }
        
        response = client.post('/api/v1/applications/', json=application_data)
        assert response.status_code == 201
        
        # Act 3: Get student status
        response = client.get(f'/api/v1/students/{student["id"]}/status')
        
        # Assert
        assert response.status_code == 200
        status_data = response.get_json()
        assert status_data['highest_status'] == 'Offer Received'
        assert status_data['highest_intake'] == 'Sep 2026'


@pytest.mark.slow
class TestPerformance:
    """Performance tests (marked as slow)."""
    
    def test_bulk_student_creation(self, db_session):
        """Test creating multiple students efficiently."""
        # Arrange
        students_data = [
            {
                'name': f'Student {i}',
                'email': f'student{i}@example.com',
                'phone': f'+123456789{i:02d}'
            }
            for i in range(100)
        ]
        
        # Act
        start_time = datetime.now()
        students = [Student(**data) for data in students_data]
        db_session.bulk_save_objects(students)
        db_session.commit()
        end_time = datetime.now()
        
        # Assert
        duration = (end_time - start_time).total_seconds()
        assert duration < 5.0  # Should complete within 5 seconds
        assert len(students) == 100


# Example of parametrized tests
@pytest.mark.parametrize("status,expected_weight", [
    ("Building Application", 1),
    ("Application Submitted to University", 2),
    ("Offer Received", 3),
    ("Offer Accepted by Student", 4),
    ("Visa Approved", 5),
    ("Dropped", 0),
])
def test_status_weights(status, expected_weight):
    """Test that status weights are correctly defined."""
    # Act
    weight = Application.STATUS_WEIGHTS.get(status)
    
    # Assert
    assert weight == expected_weight


# Example of fixture usage
@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return {
        'name': 'Sample Student',
        'email': 'sample@example.com',
        'phone': '+1234567890'
    }

def test_with_sample_data(sample_student_data):
    """Test using sample data fixture."""
    # Act
    student = Student(**sample_student_data)
    
    # Assert
    assert student.name == sample_student_data['name']
    assert student.email == sample_student_data['email']
    assert student.phone == sample_student_data['phone']
