"""
Applications API endpoints using Flask-RESTX.
"""

from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.application import Application
from app.models.student import Student
from app.models import db
from app.services.status_calculator import StatusCalculator

# Create namespace
applications_ns = Namespace('applications', description='Application operations')

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Define models for API documentation
application_model = applications_ns.model('Application', {
    'id': fields.Integer(readonly=True, description='Application ID'),
    'student_id': fields.Integer(required=True, description='Student ID'),
    'university_name': fields.String(required=True, description='University name'),
    'program_name': fields.String(required=True, description='Program name'),
    'intake': fields.String(required=True, description='Intake date'),
    'status': fields.String(required=True, description='Application status'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

applications_list_model = applications_ns.model('ApplicationsList', {
    'applications': fields.List(fields.Nested(application_model)),
    'pagination': fields.Raw(description='Pagination information')
})


@applications_ns.route('/')
class ApplicationsList(Resource):
    @applications_ns.doc('list_applications')
    @applications_ns.marshal_with(applications_list_model)
    @limiter.limit("100 per minute")
    def get(self):
        """
        Get all applications with optional filtering and pagination.

        Query Parameters:
            - page: Page number (default: 1)
            - per_page: Items per page (default: 10, max: 100)
            - status: Filter by status
            - student_id: Filter by student ID
            - search: Search by application details

        Returns:
            JSON response with applications list and pagination info
        """
        try:
            # Get query parameters
            page = request.args.get("page", 1, type=int)
            per_page = min(request.args.get("per_page", 10, type=int), 100)
            status = request.args.get("status")
            student_id = request.args.get("student_id", type=int)
            search = request.args.get("search")

            # Build query
            query = Application.query

            # Apply filters
            if status:
                query = query.filter(Application.status == status)

            if student_id:
                query = query.filter(Application.student_id == student_id)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (Application.program_name.ilike(search_term))
                    | (Application.university_name.ilike(search_term))
                )

            # Execute query with pagination
            paginated_applications = query.paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Format response
            applications_data = []
            for application in paginated_applications.items:
                applications_data.append(
                    {
                        "id": application.id,
                        "student_id": application.student_id,
                        "program_name": application.program_name,
                        "university_name": application.university_name,
                        "status": application.status,
                        "intake": application.intake,
                        "created_at": (
                            application.created_at.isoformat()
                            if application.created_at
                            else None
                        ),
                        "updated_at": (
                            application.updated_at.isoformat()
                            if application.updated_at
                            else None
                        ),
                    }
                )

            return (
                jsonify(
                    {
                        "status": "success",
                        "data": {
                            "applications": applications_data,
                            "pagination": {
                                "page": paginated_applications.page,
                                "per_page": paginated_applications.per_page,
                                "total": paginated_applications.total,
                                "pages": paginated_applications.pages,
                                "has_next": paginated_applications.has_next,
                                "has_prev": paginated_applications.has_prev,
                            },
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Failed to retrieve applications",
                        },
                    }
                ),
                500,
            )

    @applications_ns.doc('create_application')
    @applications_ns.expect(application_model)
    @applications_ns.marshal_with(application_model, code=201)
    @limiter.limit("50 per minute")
    def post(self):
        """
        Create a new application.

        Request Body:
            JSON with application data (student_id, university_name, program_name, intake, status)

        Returns:
            JSON response with created application data
        """
        try:
            data = request.get_json()

            if not data:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": {
                                "code": "BAD_REQUEST",
                                "message": "Request body must be JSON",
                            },
                        }
                    ),
                    400,
                )

            # Validate required fields
            required_fields = [
                "student_id",
                "university_name",
                "program_name",
                "intake",
                "status",
            ]
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "message": f'Missing required fields: {", ".join(missing_fields)}',
                            },
                        }
                    ),
                    422,
                )

            # Check if student exists
            student = Student.query.get(data["student_id"])
            if not student:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": {"code": "NOT_FOUND", "message": "Student not found"},
                        }
                    ),
                    404,
                )

            # Validate status
            if data["status"] not in Application.VALID_STATUSES:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "message": f'Invalid status. Must be one of: {", ".join(Application.VALID_STATUSES)}',
                            },
                        }
                    ),
                    422,
                )

            # Create new application
            application = Application(
                student_id=data["student_id"],
                university_name=data["university_name"],
                program_name=data["program_name"],
                intake=data["intake"],
                status=data["status"],
            )

            db.session.add(application)
            db.session.commit()

            # Update student's highest status and intake
            StatusCalculator.update_student_highest_status(data["student_id"])

            return (
                jsonify(
                    {
                        "status": "success",
                        "data": {
                            "application": {
                                "id": application.id,
                                "student_id": application.student_id,
                                "university_name": application.university_name,
                                "program_name": application.program_name,
                                "intake": application.intake,
                                "status": application.status,
                                "created_at": (
                                    application.created_at.isoformat()
                                    if application.created_at
                                    else None
                                ),
                                "updated_at": (
                                    application.updated_at.isoformat()
                                    if application.updated_at
                                    else None
                                ),
                            }
                        },
                    }
                ),
                201,
            )

        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Failed to create application",
                        },
                    }
                ),
                500,
            )


@applications_ns.route('/<int:application_id>')
class ApplicationDetail(Resource):
    @applications_ns.doc('get_application')
    @applications_ns.marshal_with(application_model)
    @limiter.limit("200 per minute")
    def get(self, application_id):
        """
        Get a specific application by ID.

        Args:
            application_id: The ID of the application to retrieve

        Returns:
            JSON response with application data
        """
        try:
            application = Application.query.get_or_404(application_id)

            return (
                jsonify(
                    {
                        "status": "success",
                        "data": {
                            "application": {
                                "id": application.id,
                                "student_id": application.student_id,
                                "university_name": application.university_name,
                                "program_name": application.program_name,
                                "intake": application.intake,
                                "status": application.status,
                                "created_at": (
                                    application.created_at.isoformat()
                                    if application.created_at
                                    else None
                                ),
                                "updated_at": (
                                    application.updated_at.isoformat()
                                    if application.updated_at
                                    else None
                                ),
                            }
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": {"code": "NOT_FOUND", "message": "Application not found"},
                    }
                ),
                404,
            )

    @applications_ns.doc('update_application')
    @applications_ns.expect(application_model)
    @applications_ns.marshal_with(application_model)
    @limiter.limit("100 per minute")
    def put(self, application_id):
        """
        Update an application.

        Args:
            application_id: The ID of the application to update

        Request Body:
            JSON with updated application data

        Returns:
            JSON response with updated application data
        """
        try:
            application = Application.query.get_or_404(application_id)
            data = request.get_json()

            if not data:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": {
                                "code": "BAD_REQUEST",
                                "message": "Request body must be JSON",
                            },
                        }
                    ),
                    400,
                )

            # Update fields if provided
            if "university_name" in data:
                application.university_name = data["university_name"]
            if "program_name" in data:
                application.program_name = data["program_name"]
            if "intake" in data:
                application.intake = data["intake"]
            if "status" in data:
                # Validate status
                if data["status"] not in Application.VALID_STATUSES:
                    return (
                        jsonify(
                            {
                                "status": "error",
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "message": f'Invalid status. Must be one of: {", ".join(Application.VALID_STATUSES)}',
                                },
                            }
                        ),
                        422,
                    )
                application.status = data["status"]

            db.session.commit()

            # Update student's highest status and intake
            StatusCalculator.update_student_highest_status(application.student_id)

            return (
                jsonify(
                    {
                        "status": "success",
                        "data": {
                            "application": {
                                "id": application.id,
                                "student_id": application.student_id,
                                "university_name": application.university_name,
                                "program_name": application.program_name,
                                "intake": application.intake,
                                "status": application.status,
                                "created_at": (
                                    application.created_at.isoformat()
                                    if application.created_at
                                    else None
                                ),
                                "updated_at": (
                                    application.updated_at.isoformat()
                                    if application.updated_at
                                    else None
                                ),
                            }
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Failed to update application",
                        },
                    }
                ),
                500,
            )

    @applications_ns.doc('delete_application')
    @limiter.limit("50 per minute")
    def delete(self, application_id):
        """
        Delete an application.

        Args:
            application_id: The ID of the application to delete

        Returns:
            JSON response confirming deletion
        """
        try:
            application = Application.query.get_or_404(application_id)
            student_id = application.student_id

            db.session.delete(application)
            db.session.commit()

            # Update student's highest status and intake
            StatusCalculator.update_student_highest_status(student_id)

            return (
                jsonify(
                    {"status": "success", "message": "Application deleted successfully"}
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Failed to delete application",
                        },
                    }
                ),
                500,
            )


@applications_ns.route('/students/<int:student_id>')
class StudentApplications(Resource):
    @applications_ns.doc('get_student_applications')
    @applications_ns.marshal_with(applications_list_model)
    @limiter.limit("200 per minute")
    def get(self, student_id):
        """
        Get all applications for a specific student.

        Args:
            student_id: The ID of the student

        Query Parameters:
            - page: Page number (default: 1)
            - per_page: Items per page (default: 10, max: 100)
            - status: Filter by status

        Returns:
            JSON response with student's applications
        """
        try:
            # Check if student exists
            student = Student.query.get_or_404(student_id)

            # Get query parameters
            page = request.args.get("page", 1, type=int)
            per_page = min(request.args.get("per_page", 10, type=int), 100)
            status = request.args.get("status")

            # Build query
            query = Application.query.filter_by(student_id=student_id)

            # Apply status filter if provided
            if status:
                query = query.filter(Application.status == status)

            # Execute query with pagination
            paginated_applications = query.paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Format response
            applications_data = []
            for application in paginated_applications.items:
                applications_data.append(
                    {
                        "id": application.id,
                        "student_id": application.student_id,
                        "program_name": application.program_name,
                        "university_name": application.university_name,
                        "status": application.status,
                        "intake": application.intake,
                        "created_at": (
                            application.created_at.isoformat()
                            if application.created_at
                            else None
                        ),
                        "updated_at": (
                            application.updated_at.isoformat()
                            if application.updated_at
                            else None
                        ),
                    }
                )

            return (
                jsonify(
                    {
                        "status": "success",
                        "data": {
                            "student_id": student_id,
                            "applications": applications_data,
                            "pagination": {
                                "page": paginated_applications.page,
                                "per_page": paginated_applications.per_page,
                                "total": paginated_applications.total,
                                "pages": paginated_applications.pages,
                                "has_next": paginated_applications.has_next,
                                "has_prev": paginated_applications.has_prev,
                            },
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Failed to retrieve student applications",
                        },
                    }
                ),
                500,
            )
