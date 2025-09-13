"""
Simple Test Examples - Student Platform API
Basic working tests that demonstrate testing patterns.
"""

import pytest


class TestBasicExamples:
    """Basic test examples that work without complex setup."""
    
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
    
    def test_string_operations(self):
        """Example of testing string operations."""
        # Arrange
        text = "Student Platform API"
        
        # Act
        words = text.split()
        upper_text = text.upper()
        lower_text = text.lower()
        
        # Assert
        assert len(words) == 3
        assert words[0] == "Student"
        assert words[1] == "Platform"
        assert words[2] == "API"
        assert upper_text == "STUDENT PLATFORM API"
        assert lower_text == "student platform api"
    
    def test_dictionary_operations(self):
        """Example of testing dictionary operations."""
        # Arrange
        student_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        }
        
        # Act
        keys = list(student_data.keys())
        values = list(student_data.values())
        has_name = 'name' in student_data
        email = student_data.get('email')
        
        # Assert
        assert len(keys) == 3
        assert 'name' in keys
        assert 'email' in keys
        assert 'phone' in keys
        assert 'John Doe' in values
        assert has_name is True
        assert email == 'john@example.com'


class TestDataValidation:
    """Examples of data validation testing."""
    
    def test_email_validation(self):
        """Test email validation logic."""
        # Arrange
        def is_valid_email(email):
            if not email or '@' not in email:
                return False
            parts = email.split('@')
            if len(parts) != 2 or not parts[0] or not parts[1]:
                return False
            return '.' in parts[1]
        
        valid_emails = [
            'user@example.com',
            'test.email@domain.org',
            'admin@company.co.uk'
        ]
        
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user.domain.com',
            '',
            None
        ]
        
        # Act & Assert
        for email in valid_emails:
            assert is_valid_email(email), f"Email {email} should be valid"
        
        for email in invalid_emails:
            assert not is_valid_email(email), f"Email {email} should be invalid"
    
    def test_phone_validation(self):
        """Test phone number validation logic."""
        # Arrange
        def is_valid_phone(phone):
            # Simple validation: at least 10 digits
            digits = ''.join(filter(str.isdigit, phone))
            return len(digits) >= 10
        
        valid_phones = [
            '+1234567890',
            '1234567890',
            '+1 (234) 567-8900',
            '123-456-7890'
        ]
        
        invalid_phones = [
            '123',
            '123456789',
            'abc123def',
            ''
        ]
        
        # Act & Assert
        for phone in valid_phones:
            assert is_valid_phone(phone), f"Phone {phone} should be valid"
        
        for phone in invalid_phones:
            assert not is_valid_phone(phone), f"Phone {phone} should be invalid"


class TestBusinessLogic:
    """Examples of business logic testing."""
    
    def test_status_priority_calculation(self):
        """Test status priority calculation."""
        # Arrange
        status_weights = {
            'Building Application': 1,
            'Application Submitted to University': 2,
            'Offer Received': 3,
            'Offer Accepted by Student': 4,
            'Visa Approved': 5,
            'Dropped': 0
        }
        
        def get_highest_status(applications):
            if not applications:
                return None
            
            highest_weight = -1
            highest_status = None
            
            for app in applications:
                weight = status_weights.get(app['status'], 0)
                if weight > highest_weight:
                    highest_weight = weight
                    highest_status = app['status']
            
            return highest_status
        
        # Test cases
        test_cases = [
            {
                'applications': [
                    {'status': 'Building Application', 'intake': 'Jan 2026'},
                    {'status': 'Offer Received', 'intake': 'Sep 2026'}
                ],
                'expected': 'Offer Received'
            },
            {
                'applications': [
                    {'status': 'Application Submitted to University', 'intake': 'Jan 2026'},
                    {'status': 'Building Application', 'intake': 'Sep 2026'}
                ],
                'expected': 'Application Submitted to University'
            },
            {
                'applications': [],
                'expected': None
            }
        ]
        
        # Act & Assert
        for case in test_cases:
            result = get_highest_status(case['applications'])
            assert result == case['expected'], f"Expected {case['expected']}, got {result}"
    
    def test_intake_date_parsing(self):
        """Test intake date parsing logic."""
        # Arrange
        def parse_intake_date(intake_str):
            """Parse intake string like 'Jan 2026' or 'Sep 2026'."""
            if not intake_str:
                return None
            
            parts = intake_str.split()
            if len(parts) != 2:
                return None
            
            month, year = parts
            try:
                year_int = int(year)
                return {'month': month, 'year': year_int}
            except ValueError:
                return None
        
        # Test cases
        test_cases = [
            ('Jan 2026', {'month': 'Jan', 'year': 2026}),
            ('Sep 2026', {'month': 'Sep', 'year': 2026}),
            ('Dec 2025', {'month': 'Dec', 'year': 2025}),
            ('Invalid', None),
            ('', None),
            (None, None)
        ]
        
        # Act & Assert
        for intake_str, expected in test_cases:
            result = parse_intake_date(intake_str)
            assert result == expected, f"For '{intake_str}', expected {expected}, got {result}"


# Example of parametrized tests
@pytest.mark.parametrize("input_value,expected", [
    ("John Doe", "JOHN DOE"),
    ("jane smith", "JANE SMITH"),
    ("", ""),
    ("a", "A"),
])
def test_string_uppercase(input_value, expected):
    """Test string uppercase conversion with different inputs."""
    # Act
    result = input_value.upper()
    
    # Assert
    assert result == expected


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
    name = sample_student_data['name']
    email = sample_student_data['email']
    phone = sample_student_data['phone']
    
    # Assert
    assert name == 'Sample Student'
    assert email == 'sample@example.com'
    assert phone == '+1234567890'
    assert len(sample_student_data) == 3


# Example of testing with multiple assertions
def test_comprehensive_data_validation():
    """Test comprehensive data validation."""
    # Arrange
    def validate_student_data(data):
        errors = []
        
        if not data.get('name') or len(data['name'].strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not data.get('email') or '@' not in data['email']:
            errors.append("Valid email is required")
        
        if not data.get('phone') or len(data['phone']) < 10:
            errors.append("Phone must be at least 10 characters")
        
        return errors
    
    # Test cases
    test_cases = [
        {
            'data': {'name': 'John Doe', 'email': 'john@example.com', 'phone': '+1234567890'},
            'expected_errors': 0
        },
        {
            'data': {'name': 'A', 'email': 'invalid', 'phone': '123'},
            'expected_errors': 3
        },
        {
            'data': {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '123'},
            'expected_errors': 1
        }
    ]
    
    # Act & Assert
    for case in test_cases:
        errors = validate_student_data(case['data'])
        assert len(errors) == case['expected_errors'], f"Expected {case['expected_errors']} errors, got {len(errors)}"
