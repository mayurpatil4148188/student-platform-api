"""
Students API endpoints.
"""

from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.student import Student
from app.models import db
from app.services.status_calculator import StatusCalculator

# Create namespace
students_ns = Namespace('students', description='Student operations')

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Define models for API documentation
student_model = students_ns.model('Student', {
    'id': fields.Integer(readonly=True, description='Student ID'),
    'name': fields.String(required=True, description='Student name'),
    'email': fields.String(required=True, description='Student email'),
    'phone': fields.String(required=True, description='Student phone number'),
    'highest_status': fields.String(description='Highest application status'),
    'highest_intake': fields.String(description='Intake date of highest status application'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

student_create_model = students_ns.model('StudentCreate', {
    'name': fields.String(required=True, description='Student name'),
    'email': fields.String(required=True, description='Student email'),
    'phone': fields.String(required=True, description='Student phone number')
})

student_status_model = students_ns.model('StudentStatus', {
    'student_id': fields.Integer(description='Student ID'),
    'highest_status': fields.String(description='Highest application status'),
    'highest_intake': fields.String(description='Intake date of highest status application')
})

pagination_model = students_ns.model('Pagination', {
    'page': fields.Integer(description='Current page'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total items'),
    'pages': fields.Integer(description='Total pages'),
    'has_next': fields.Boolean(description='Has next page'),
    'has_prev': fields.Boolean(description='Has previous page')
})

students_list_model = students_ns.model('StudentsList', {
    'students': fields.List(fields.Nested(student_model)),
    'pagination': fields.Nested(pagination_model)
})


@students_ns.route('/')
class StudentsList(Resource):
    @students_ns.doc('list_students')
    @students_ns.marshal_with(students_list_model)
    @limiter.limit("100 per minute")
    def get(self):
        """
        Get all students with optional filtering and pagination.
        
        Query Parameters:
            - page: Page number (default: 1)
            - per_page: Items per page (default: 10, max: 100)
            - status: Filter by status
            - search: Search by name or email
        
        Returns:
            JSON response with students list and pagination info
        """
        try:
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 10, type=int), 100)
            status = request.args.get('status')
            search = request.args.get('search')
            
            # Build query
            query = Student.query
            
            # Apply filters
            if status:
                query = query.filter(Student.highest_status == status)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (Student.name.ilike(search_term)) |
                    (Student.email.ilike(search_term))
                )
            
            # Execute query with pagination
            paginated_students = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Format response
            students_data = []
            for student in paginated_students.items:
                students_data.append({
                    'id': student.id,
                    'name': student.name,
                    'email': student.email,
                    'phone': student.phone,
                    'highest_status': student.highest_status,
                    'highest_intake': student.highest_intake,
                    'created_at': student.created_at.isoformat() if student.created_at else None,
                    'updated_at': student.updated_at.isoformat() if student.updated_at else None
                })
            
            return jsonify({
                'status': 'success',
                'data': {
                    'students': students_data,
                    'pagination': {
                        'page': paginated_students.page,
                        'per_page': paginated_students.per_page,
                        'total': paginated_students.total,
                        'pages': paginated_students.pages,
                        'has_next': paginated_students.has_next,
                        'has_prev': paginated_students.has_prev
                    }
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'Failed to retrieve students'
                }
            }), 500

    @students_ns.doc('create_student')
    @students_ns.expect(student_create_model)
    @students_ns.marshal_with(student_model, code=201)
    @limiter.limit("50 per minute")
    def post(self):
        """
        Create a new student.
        
        Request Body:
            JSON with student data (name, email, phone)
        
        Returns:
            JSON response with created student data
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'error': {
                        'code': 'BAD_REQUEST',
                        'message': 'Request body must be JSON'
                    }
                }), 400
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({
                    'status': 'error',
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    }
                }), 422
            
            # Check if email already exists
            existing_student = Student.query.filter_by(email=data['email']).first()
            if existing_student:
                return jsonify({
                    'status': 'error',
                    'error': {
                        'code': 'CONFLICT',
                        'message': 'Student with this email already exists'
                    }
                }), 409
            
            # Create new student
            student = Student(
                name=data['name'],
                email=data['email'],
                phone=data['phone']
            )
            
            db.session.add(student)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'student': {
                        'id': student.id,
                        'name': student.name,
                        'email': student.email,
                        'phone': student.phone,
                        'highest_status': student.highest_status,
                        'highest_intake': student.highest_intake,
                        'created_at': student.created_at.isoformat() if student.created_at else None,
                        'updated_at': student.updated_at.isoformat() if student.updated_at else None
                    }
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'Failed to create student'
                }
            }), 500


@students_ns.route('/<int:student_id>')
@students_ns.doc('get_student')
@students_ns.marshal_with(student_model)
@limiter.limit("200 per minute")
class StudentDetail(Resource):
    def get(self, student_id):
        """
        Get a specific student by ID.
        
        Args:
            student_id: The ID of the student to retrieve
        
        Returns:
            JSON response with student data
        """
        try:
            student = Student.query.get_or_404(student_id)
            
            return jsonify({
                'status': 'success',
                'data': {
                    'student': {
                        'id': student.id,
                        'name': student.name,
                        'email': student.email,
                        'phone': student.phone,
                        'highest_status': student.highest_status,
                        'highest_intake': student.highest_intake,
                        'created_at': student.created_at.isoformat() if student.created_at else None,
                        'updated_at': student.updated_at.isoformat() if student.updated_at else None
                    }
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Student not found'
                }
            }), 404

    @students_ns.doc('update_student')
    @students_ns.expect(student_model)
    @students_ns.marshal_with(student_model)
    @limiter.limit("100 per minute")
    def put(self, student_id):
        """
        Update a student.
        
        Args:
            student_id: The ID of the student to update
        
        Request Body:
            JSON with updated student data
        
        Returns:
            JSON response with updated student data
        """
        try:
            student = Student.query.get_or_404(student_id)
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'error': {
                        'code': 'BAD_REQUEST',
                        'message': 'Request body must be JSON'
                    }
                }), 400
            
            # Update fields if provided
            if 'name' in data:
                student.name = data['name']
            if 'email' in data:
                # Check if email already exists for another student
                existing_student = Student.query.filter(
                    Student.email == data['email'],
                    Student.id != student_id
                ).first()
                if existing_student:
                    return jsonify({
                        'status': 'error',
                        'error': {
                            'code': 'CONFLICT',
                            'message': 'Student with this email already exists'
                        }
                    }), 409
                student.email = data['email']
            if 'phone' in data:
                student.phone = data['phone']
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'student': {
                        'id': student.id,
                        'name': student.name,
                        'email': student.email,
                        'phone': student.phone,
                        'highest_status': student.highest_status,
                        'highest_intake': student.highest_intake,
                        'created_at': student.created_at.isoformat() if student.created_at else None,
                        'updated_at': student.updated_at.isoformat() if student.updated_at else None
                    }
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'Failed to update student'
                }
            }), 500


    @students_ns.doc('delete_student')
    @limiter.limit("50 per minute")
    def delete(self, student_id):
        """
        Delete a student.
        
        Args:
            student_id: The ID of the student to delete
        
        Returns:
            JSON response confirming deletion
        """
        try:
            student = Student.query.get_or_404(student_id)
            
            db.session.delete(student)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Student deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'Failed to delete student'
                }
            }), 500


@students_ns.route('/<int:student_id>/status')
@students_ns.doc('get_student_status')
@students_ns.marshal_with(student_status_model)
@limiter.limit("200 per minute")
class StudentStatus(Resource):
    def get(self, student_id):
        """
        Get the highest status and highest intake for a student.
        
        Args:
            student_id: The ID of the student
        
        Returns:
            JSON response with highest status and intake information
        """
        try:
            student = Student.query.get_or_404(student_id)
            
            # Get applications for the student
            from app.models.application import Application
            applications = Application.query.filter_by(
                student_id=student_id,
                is_deleted=False
            ).all()
            
            # Calculate highest status and intake
            status_calculator = StatusCalculator()
            result = status_calculator.calculate_highest_status(applications)
            
            return jsonify({
                'status': 'success',
                'data': {
                    'student_id': student.id,
                    'highest_status': result['highest_status'],
                    'highest_intake': result['highest_intake']
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'Failed to calculate student status'
                }
            }), 500
