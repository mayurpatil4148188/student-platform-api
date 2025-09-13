# 🧪 Testing Guide - Student Platform API

This guide covers how to run tests and create new test cases for the Student Platform API using pytest.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Running Tests](#running-tests)
3. [Test Structure](#test-structure)
4. [Creating New Tests](#creating-new-tests)
5. [Test Examples](#test-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
```bash
# Activate virtual environment
pyenv activate project_env

# Install test dependencies (already in requirements.txt)
pip install pytest pytest-flask
```

### Run All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_students.py

# Run specific test function
pytest tests/test_students.py::test_create_student
```

## 🏃‍♂️ Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with detailed output
pytest -vv

# Run tests and show local variables on failure
pytest -l

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (if pytest-xdist is installed)
pytest -n auto
```

### Coverage Commands

```bash
# Run tests with coverage report
pytest --cov=app

# Run tests with coverage and HTML report
pytest --cov=app --cov-report=html

# Run tests with coverage and show missing lines
pytest --cov=app --cov-report=term-missing

# Generate coverage report in multiple formats
pytest --cov=app --cov-report=html --cov-report=xml --cov-report=term
```

### Filtering Tests

```bash
# Run tests matching a pattern
pytest -k "test_student"

# Run tests in a specific directory
pytest tests/

# Run tests in a specific file
pytest tests/test_students.py

# Run tests matching a specific function
pytest tests/test_students.py::test_create_student

# Run tests with specific markers
pytest -m "not slow"

# Run only failed tests from last run
pytest --lf
```

### Output Options

```bash
# Show print statements
pytest -s

# Show slowest 10 tests
pytest --durations=10

# Show test results in real-time
pytest -v --tb=short

# Show full traceback on failure
pytest --tb=long

# Show only the failing line
pytest --tb=line
```

## 📁 Test Structure

```
tests/
├── __init__.py                 # Makes tests a Python package
├── conftest.py                 # Pytest configuration and fixtures
├── test_students.py           # Student model and API tests
├── test_applications.py       # Application model and API tests
└── test_status_calculator.py  # Business logic tests
```

### Test File Naming Convention
- Test files must start with `test_` or end with `_test.py`
- Test functions must start with `test_`
- Test classes must start with `Test`

## ✨ Creating New Tests

### 1. Test Function Structure

```python
def test_function_name():
    """Test description explaining what is being tested."""
    # Arrange - Set up test data
    # Act - Execute the code being tested
    # Assert - Verify the results
```

### 2. Test Class Structure

```python
class TestClassName:
    """Test class for testing specific functionality."""
    
    def test_method_name(self):
        """Test specific method or functionality."""
        # Test implementation
```

### 3. Using Fixtures

```python
def test_with_fixture(client, db_session):
    """Test using pytest fixtures."""
    # Use client for API testing
    # Use db_session for database operations
```

## 📝 Test Examples

### Simple Unit Test

```python
def test_basic_assertion():
    """Example of basic assertion testing."""
    # Arrange
    expected = "Hello World"
    
    # Act
    result = "Hello World"
    
    # Assert
    assert result == expected
    assert len(result) == 11
    assert "Hello" in result
```

### Model Test

```python
def test_student_creation():
    """Test creating a new student."""
    # Arrange
    student_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890'
    }
    
    # Act
    student = Student(**student_data)
    student.save()
    
    # Assert
    assert student.id is not None
    assert student.name == 'John Doe'
    assert student.email == 'john@example.com'
    assert student.phone == '+1234567890'
    assert student.created_at is not None
```

### API Test

```python
def test_create_student_api(client, db_session):
    """Test creating a student via API."""
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
```

### Error Handling Test

```python
def test_invalid_email_validation():
    """Test validation with invalid email."""
    # Arrange
    student_data = {
        'name': 'Test User',
        'email': 'invalid-email',
        'phone': '+1234567890'
    }
    
    # Act
    student = Student(**student_data)
    errors = student.validate()
    
    # Assert
    assert len(errors) > 0
    assert any('email' in error.lower() for error in errors)
```

## 🎯 Best Practices

### 1. Test Naming
```python
# Good: Descriptive and specific
def test_create_student_with_valid_data():
def test_create_student_with_duplicate_email_raises_error():
def test_get_student_status_returns_highest_status():

# Bad: Vague and unclear
def test_student():
def test_api():
def test_error():
```

### 2. Test Organization
```python
class TestStudentAPI:
    """Test class for Student API endpoints."""
    
    def test_create_student_success(self):
        """Test successful student creation."""
        pass
    
    def test_create_student_validation_error(self):
        """Test student creation with validation errors."""
        pass
    
    def test_get_student_success(self):
        """Test successful student retrieval."""
        pass
```

### 3. Use Fixtures for Common Setup
```python
@pytest.fixture
def sample_student():
    """Create a sample student for testing."""
    return Student(
        name='Test Student',
        email='test@example.com',
        phone='+1234567890'
    )

def test_student_operations(sample_student):
    """Test operations on sample student."""
    assert sample_student.name == 'Test Student'
```

### 4. Test Data Management
```python
@pytest.fixture
def student_data():
    """Sample student data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890'
    }

def test_create_student_with_data(student_data):
    """Test creating student with sample data."""
    student = Student(**student_data)
    assert student.name == student_data['name']
```

### 5. Assertion Best Practices
```python
# Good: Specific assertions
assert response.status_code == 201
assert 'id' in response_data
assert response_data['name'] == expected_name

# Good: Multiple assertions for complex objects
assert student.id is not None
assert student.name == 'John Doe'
assert student.email == 'john@example.com'
assert student.created_at is not None

# Bad: Generic assertions
assert response
assert student
assert data
```

## 🔧 Pytest Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### conftest.py Structure
```python
import pytest
from app import create_app
from app.models import db

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        yield db.session
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'app'
# Solution: Run from project root directory
cd /path/to/student-platform-api
pytest
```

#### 2. Database Issues
```bash
# Error: Database connection failed
# Solution: Set test database URL
export DATABASE_URL="sqlite:///:memory:"
pytest
```

#### 3. Fixture Not Found
```python
# Error: Fixture 'client' not found
# Solution: Ensure conftest.py is in tests/ directory
# and contains the client fixture
```

#### 4. Test Discovery Issues
```bash
# Error: No tests found
# Solution: Check file naming convention
# Files must start with 'test_' or end with '_test.py'
```

### Debug Commands

```bash
# Run tests with maximum verbosity
pytest -vvv

# Run tests and drop into debugger on failure
pytest --pdb

# Run tests and show local variables
pytest -l

# Run specific test with debugging
pytest tests/test_students.py::test_create_student --pdb
```

### Performance Testing

```bash
# Profile slow tests
pytest --durations=10

# Run tests in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"
```

## 📊 Test Coverage

### Generate Coverage Report
```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Coverage Goals
- **Unit Tests**: 90%+ coverage for business logic
- **API Tests**: 80%+ coverage for endpoints
- **Integration Tests**: 70%+ coverage for workflows

## 🚀 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-flask Documentation](https://pytest-flask.readthedocs.io/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_students.py::test_create_student

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Test File Template
```python
import pytest
from app.models import Student, Application
from app.services.status_calculator import StatusCalculator

class TestNewFeature:
    """Test class for new feature."""
    
    def test_feature_success_case(self, client, db_session):
        """Test successful feature execution."""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_feature_error_case(self, client, db_session):
        """Test feature error handling."""
        # Arrange
        # Act
        # Assert
        pass
```

Happy Testing! 🧪✨