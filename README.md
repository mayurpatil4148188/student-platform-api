# Student Platform API

A comprehensive Flask-based REST API for managing students and their university applications. This application implements a complete student platform with automatic status calculation and intake tracking.

## Features

- **Student Management**: CRUD operations for student records
- **Application Management**: CRUD operations for university applications
- **Automatic Status Calculation**: Real-time calculation of highest application status and intake
- **Status Progression**: Support for application status workflow
- **Search & Filtering**: Advanced search and filtering capabilities
- **Pagination**: Efficient data pagination for large datasets
- **Rate Limiting**: Built-in rate limiting for API protection
- **Comprehensive Testing**: Full test suite with pytest
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Docker Support**: Complete Docker containerization
- **Production Ready**: Configured for production deployment

## Assignment Requirements Implementation

This project fulfills all the requirements from the interview assignment:

### 1. Modules & Data Models

#### Students Module
- ✅ Name (string, required)
- ✅ Email (string, required)
- ✅ Phone (string, required)
- ✅ Highest Intake (string, auto-calculated)
- ✅ Highest Status (string, auto-calculated)

#### Applications Module
- ✅ University Name (string, required)
- ✅ Program Name (string, required)
- ✅ Intake (string, required, format: Jan 2026, Feb 2026, etc.)
- ✅ Status (string, required) with valid values:
  1. Building Application
  2. Application Submitted to University
  3. Offer Received
  4. Offer Accepted by Student
  5. Visa Approved
  6. Dropped

### 2. Logic for Highest Status & Highest Intake

- ✅ Automatic recalculation when applications are created/updated
- ✅ Status weightage system (Visa Approved = highest)
- ✅ Tie-breaker logic using earliest intake date
- ✅ Proper handling of dropped applications

### 3. APIs Implemented

- ✅ CRUD operations for Students
- ✅ CRUD operations for Applications
- ✅ API to fetch Highest Status & Highest Intake for a student
- ✅ Proper error handling and validation
- ✅ Rate limiting and security measures

### 4. Technical Requirements

- ✅ Flask (Python) framework
- ✅ PostgreSQL database support
- ✅ Proper project structure (models, routes, services)
- ✅ All required fields are mandatory
- ✅ Docker setup included
- ✅ Comprehensive test cases
- ✅ API documentation with Swagger
- ✅ Production-ready configuration

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student-platform-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:5000`

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **Initialize database**
   ```bash
   docker-compose exec web flask db init
   docker-compose exec web flask db migrate -m "Initial migration"
   docker-compose exec web flask db upgrade
   ```

3. **Access the application**
   - API: `http://localhost:5000`
   - API Documentation: `http://localhost:5000/docs/`

### Using Docker only

1. **Build the image**
   ```bash
   docker build -t student-platform-api .
   ```

2. **Run with external database**
   ```bash
   docker run -p 5000:5000 \
     -e DATABASE_URL=postgresql://user:pass@host:port/db \
     student-platform-api
   ```

## API Documentation

### Interactive Documentation

Visit `http://localhost:5000/docs/` for interactive Swagger documentation.

### Core Endpoints

#### Students

- `GET /api/v1/students/` - List all students (with pagination)
- `POST /api/v1/students/` - Create a new student
- `GET /api/v1/students/{id}` - Get student by ID
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student
- `GET /api/v1/students/{id}/status` - Get student's highest status and intake

#### Applications

- `GET /api/v1/applications` - List all applications (with pagination)
- `POST /api/v1/applications` - Create a new application
- `GET /api/v1/applications/{id}` - Get application by ID
- `PUT /api/v1/applications/{id}` - Update application
- `DELETE /api/v1/applications/{id}` - Delete application

### Query Parameters

#### Pagination
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)

#### Filtering
- `status` - Filter by status
- `student_id` - Filter applications by student ID
- `search` - Search by name, email, university, or program

### Example Requests

#### Create a Student
```bash
curl -X POST http://localhost:5000/api/v1/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890"
  }'
```

#### Create an Application
```bash
curl -X POST http://localhost:5000/api/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "university_name": "University of California",
    "program_name": "Computer Science",
    "intake": "Jan 2026",
    "status": "Building Application"
  }'
```

#### Get Student Status
```bash
curl http://localhost:5000/api/v1/students/1/status
```

Response:
```json
{
  "status": "success",
  "data": {
    "student_id": 1,
    "highest_status": "Offer Received",
    "highest_intake": "Jan 2026"
  }
}
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_students.py

# Run with verbose output
pytest -v
```

### Test Categories

- **Unit Tests**: Test individual components
- **Integration Tests**: Test API endpoints
- **Status Calculator Tests**: Test business logic
- **Model Tests**: Test database models

## Postman Collection

Import the `postman_collection.json` file into Postman for comprehensive API testing. The collection includes:

- All CRUD operations for students and applications
- Test scenarios for complete user journeys
- Environment variables for easy configuration
- Example requests and responses

## Project Structure

```
student-platform-api/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # Base model class
│   │   ├── student.py          # Student model
│   │   └── application.py      # Application model
│   ├── services/
│   │   └── status_calculator.py # Business logic
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── students.py     # Student API endpoints
│   │       └── applications.py # Application API endpoints
│   └── migrations/             # Database migrations
├── tests/                      # Test suite
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
├── postman_collection.json     # Postman API collection
└── README.md                   # This file
```

## Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Environment (development/production)
- `REDIS_URL` - Redis connection for rate limiting

### Database Configuration

The application supports multiple database backends:
- PostgreSQL (recommended for production)
- SQLite (default for development)

## Status Calculation Logic

The application automatically calculates the highest status and intake for each student based on their applications:

1. **Status Weighting**: Each status has a weight (1-5, with "Visa Approved" being highest)
2. **Tie Breaking**: When multiple applications have the same highest status, the earliest intake date is selected
3. **Dropped Applications**: Dropped applications are excluded from calculations
4. **Real-time Updates**: Status is recalculated whenever applications are created, updated, or deleted

## Rate Limiting

The API includes rate limiting to prevent abuse:
- Students endpoints: 100 requests/minute
- Applications endpoints: 100 requests/minute
- Create operations: 50 requests/minute
- Delete operations: 20 requests/minute

## Production Deployment

### Environment Setup

1. **Set production environment variables**
2. **Use PostgreSQL database**
3. **Configure reverse proxy (Nginx)**
4. **Set up SSL certificates**
5. **Configure logging**
6. **Set up monitoring**

### Security Considerations

- Use strong secret keys
- Enable HTTPS
- Configure CORS properly
- Set up proper firewall rules
- Regular security updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please create an issue in the repository or contact the development team.