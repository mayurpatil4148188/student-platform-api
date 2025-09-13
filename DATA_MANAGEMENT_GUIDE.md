# 🏭 Data Management Guide - Student Platform API

This guide covers how to create, manage, export, and import dummy data for the Student Platform API using the built-in factory system.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Factory Classes](#factory-classes)
4. [CLI Commands](#cli-commands)
5. [Data Scenarios](#data-scenarios)
6. [Export/Import](#exportimport)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

## 🎯 Overview

The Student Platform API includes a comprehensive data factory system that allows you to:

- **Generate realistic dummy data** for testing and development
- **Create different scenarios** (basic, realistic, custom)
- **Export data** to JSON files for backup or sharing
- **Import data** from JSON files to restore or migrate data
- **Clear all data** when needed for fresh starts

### Key Features

✅ **Realistic Data Generation** - Uses Faker library for authentic-looking data  
✅ **Multiple Scenarios** - Basic, realistic, and custom data patterns  
✅ **Export/Import** - Full data portability with JSON format  
✅ **Status Calculation** - Automatically calculates student highest status  
✅ **Soft Deletion** - Safe data clearing with soft delete  
✅ **CLI Interface** - Easy-to-use command-line tools  

## 🚀 Quick Start

### Prerequisites
```bash
# Activate virtual environment
pyenv activate project_env

# Install dependencies (faker is already in requirements.txt)
pip install faker==20.1.0
```

### Basic Usage
```bash
# Create 20 students with 3 applications each
python manage_data.py create --students 20 --applications 3

# Create realistic scenario
python manage_data.py create --scenario realistic

# Export current data
python manage_data.py export --output my_data.json

# Import data from file
python manage_data.py import --file my_data.json

# Clear all data
python manage_data.py clear

# Show database statistics
python manage_data.py stats
```

## 🏭 Factory Classes

### StudentFactory

Creates realistic student data with:

- **Names**: 100+ common first and last names
- **Emails**: Realistic email addresses with various domains
- **Phones**: International phone number formats
- **Notes**: Generated sentences for additional context

```python
from app.factories import StudentFactory

# Create a single student
student = StudentFactory.create_student()

# Create multiple students
students = StudentFactory.create_students(count=10)

# Create and save to database
students = StudentFactory.create_and_save_students(count=10)
```

### ApplicationFactory

Creates realistic application data with:

- **Universities**: 50+ real university names
- **Programs**: 70+ academic programs across disciplines
- **Intakes**: Various intake periods (Fall 2024, Spring 2025, etc.)
- **Statuses**: Weighted status distribution (more early-stage applications)

```python
from app.factories import ApplicationFactory

# Create applications for a student
applications = ApplicationFactory.create_applications_for_student(
    student_id=1, count=3
)

# Create and save to database
applications = ApplicationFactory.create_and_save_applications_for_student(
    student_id=1, count=3
)
```

### DataFactory

Main factory class for comprehensive data management:

```python
from app.factories import DataFactory

# Create complete sample data
result = DataFactory.create_sample_data(
    student_count=20,
    applications_per_student=3,
    update_student_status=True
)

# Create realistic scenario
result = DataFactory.create_realistic_scenario()

# Export all data
data = DataFactory.export_data_to_dict()

# Clear all data
result = DataFactory.clear_all_data()
```

## 🖥️ CLI Commands

### Create Data

```bash
# Basic creation
python manage_data.py create --students 20 --applications 3

# Realistic scenario
python manage_data.py create --scenario realistic

# Skip status updates (faster)
python manage_data.py create --students 50 --no-status-update

# Create and export in one command
python manage_data.py create --students 10 --export --output sample.json
```

**Options:**
- `--students N`: Number of students to create (default: 20)
- `--applications N`: Applications per student (default: 3)
- `--scenario {basic,realistic}`: Data scenario type (default: basic)
- `--no-status-update`: Skip updating student highest status
- `--export`: Export data after creation
- `--output FILE`: Output file for export

### Export Data

```bash
# Export with timestamp
python manage_data.py export

# Export to specific file
python manage_data.py export --output my_backup.json
```

**Options:**
- `--output FILE`: Output filename (default: timestamped)

### Import Data

```bash
# Import with confirmation
python manage_data.py import --file my_data.json

# Import without confirmation
python manage_data.py import --file my_data.json --force

# Import without status updates
python manage_data.py import --file my_data.json --no-status-update
```

**Options:**
- `--file FILE`: JSON file to import (required)
- `--force`: Skip confirmation prompt
- `--no-status-update`: Skip updating student status

### Clear Data

```bash
# Clear with confirmation
python manage_data.py clear

# Clear without confirmation
python manage_data.py clear --force
```

**Options:**
- `--force`: Skip confirmation prompt

### Show Statistics

```bash
# Show current database statistics
python manage_data.py stats
```

## 📊 Data Scenarios

### Basic Scenario

Creates random students with random applications:

```bash
python manage_data.py create --students 20 --applications 3
```

**Characteristics:**
- Random names, emails, phones
- Random universities and programs
- Weighted status distribution
- Automatic status calculation

### Realistic Scenario

Creates a curated set of students with realistic profiles:

```bash
python manage_data.py create --scenario realistic
```

**Includes:**
- **High-achieving student**: Multiple offers, excellent record
- **Average student**: Mixed results, exploring options
- **Struggling student**: Working on improvement, considering gap year
- **Random students**: 7 additional students with varied profiles

**Example Profiles:**
- Alex Johnson: Harvard CS offer, Stanford Data Science accepted
- Sarah Williams: UC Berkeley Psychology submitted, Michigan Business building
- Mike Chen: Community College General Studies building

## 📁 Export/Import

### Export Format

The exported JSON contains:

```json
{
  "students": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "highest_status": "Offer Received",
      "highest_intake": "Fall 2025",
      "notes": "Excellent student...",
      "applications": [...],
      "created_at": "2025-09-13T10:00:00",
      "updated_at": "2025-09-13T10:00:00"
    }
  ],
  "applications": [
    {
      "id": 1,
      "student_id": 1,
      "university_name": "Harvard University",
      "program_name": "Computer Science",
      "intake": "Fall 2025",
      "status": "Offer Received",
      "created_at": "2025-09-13T10:00:00",
      "updated_at": "2025-09-13T10:00:00"
    }
  ],
  "export_timestamp": "2025-09-13T10:00:00",
  "total_students": 5,
  "total_applications": 10
}
```

### Import Process

1. **Validation**: Checks file existence and format
2. **Confirmation**: Prompts user unless `--force` is used
3. **Import**: Creates students and applications
4. **Status Update**: Calculates highest status for all students
5. **Summary**: Shows import results

### Use Cases

- **Backup**: Export before major changes
- **Testing**: Share test data between environments
- **Migration**: Move data between databases
- **Demo**: Prepare demo data for presentations

## 💡 Examples

### Development Workflow

```bash
# 1. Start with clean database
python manage_data.py clear --force

# 2. Create realistic test data
python manage_data.py create --scenario realistic

# 3. Check what we have
python manage_data.py stats

# 4. Export for backup
python manage_data.py export --output dev_backup.json

# 5. Test your changes...

# 6. Restore if needed
python manage_data.py clear --force
python manage_data.py import --file dev_backup.json --force
```

### Testing Different Scenarios

```bash
# Test with many students
python manage_data.py create --students 100 --applications 2

# Test with few students, many applications
python manage_data.py create --students 5 --applications 10

# Test realistic scenario
python manage_data.py create --scenario realistic
```

### Data Sharing

```bash
# Export current data
python manage_data.py export --output shared_data.json

# Share the file with team members

# Import on another machine
python manage_data.py import --file shared_data.json
```

### Performance Testing

```bash
# Create large dataset
python manage_data.py create --students 1000 --applications 5 --no-status-update

# Export for performance testing
python manage_data.py export --output performance_test.json
```

## 🎯 Best Practices

### Data Creation

1. **Start Small**: Begin with 10-20 students for development
2. **Use Realistic Scenarios**: Use `--scenario realistic` for demos
3. **Skip Status Updates**: Use `--no-status-update` for faster creation
4. **Export After Creation**: Always backup your test data

### Data Management

1. **Regular Backups**: Export data before major changes
2. **Version Control**: Don't commit large JSON files to git
3. **Clean Slate**: Use `clear` before creating new test data
4. **Documentation**: Document your test scenarios

### Performance

1. **Batch Operations**: Create data in batches rather than one-by-one
2. **Skip Status Updates**: For large datasets, update status separately
3. **Use Indexes**: Ensure database indexes are in place
4. **Monitor Memory**: Large datasets may require more memory

### Testing

1. **Isolated Tests**: Clear data between test runs
2. **Consistent Data**: Use exported data for consistent testing
3. **Edge Cases**: Test with empty, single, and large datasets
4. **Status Validation**: Verify status calculations are correct

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Error: File not found
# Solution: Check file path and permissions
ls -la my_data.json

# Error: Invalid JSON
# Solution: Validate JSON format
python -m json.tool my_data.json
```

#### Database Issues
```bash
# Error: Database connection failed
# Solution: Check database URL
export DATABASE_URL="postgresql://postgres:1234@localhost:5432/student_platform_db"

# Error: Permission denied
# Solution: Check database permissions
```

#### Memory Issues
```bash
# Error: Out of memory with large datasets
# Solution: Create data in smaller batches
python manage_data.py create --students 100 --applications 2
python manage_data.py create --students 100 --applications 2
```

### Debug Commands

```bash
# Check current data
python manage_data.py stats

# Test export/import cycle
python manage_data.py export --output test.json
python manage_data.py clear --force
python manage_data.py import --file test.json --force
python manage_data.py stats
```

## 📚 Additional Resources

- [Faker Documentation](https://faker.readthedocs.io/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [JSON Format Specification](https://www.json.org/)

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Create basic data
python manage_data.py create --students 20 --applications 3

# Create realistic scenario
python manage_data.py create --scenario realistic

# Export data
python manage_data.py export --output backup.json

# Import data
python manage_data.py import --file backup.json

# Clear all data
python manage_data.py clear --force

# Show statistics
python manage_data.py stats
```

### Factory Usage
```python
from app.factories import DataFactory, StudentFactory, ApplicationFactory

# Create comprehensive data
result = DataFactory.create_sample_data(20, 3)

# Create single student
student = StudentFactory.create_student()

# Create applications for student
apps = ApplicationFactory.create_applications_for_student(student.id, 3)
```

Happy Data Management! 🏭✨
