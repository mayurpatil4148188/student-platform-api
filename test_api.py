#!/usr/bin/env python3
"""
Comprehensive API test script for Student Platform API.
This script tests all endpoints and validates the complete functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional


class StudentPlatformAPITester:
    """Comprehensive API tester for Student Platform API."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.test_data = {}
        self.results = {"passed": 0, "failed": 0, "errors": []}

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        expected_status: int = 200,
        description: str = "",
    ) -> bool:
        """Test a single endpoint and return success status."""
        url = f"{self.api_base}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status

            if success:
                self.results["passed"] += 1
                self.log(
                    f"✓ {description or f'{method} {endpoint}'} - Status: {response.status_code}"
                )
            else:
                self.results["failed"] += 1
                error_msg = f"✗ {description or f'{method} {endpoint}'} - Expected: {expected_status}, Got: {response.status_code}"
                self.log(error_msg, "ERROR")
                self.results["errors"].append(error_msg)

                # Log response content for debugging
                try:
                    error_content = response.json()
                    self.log(
                        f"Response: {json.dumps(error_content, indent=2)}", "DEBUG"
                    )
                except:
                    self.log(f"Response: {response.text}", "DEBUG")

            return success, response

        except Exception as e:
            self.results["failed"] += 1
            error_msg = (
                f"✗ {description or f'{method} {endpoint}'} - Exception: {str(e)}"
            )
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            return False, None

    def test_health_endpoints(self):
        """Test health check endpoints."""
        self.log("Testing health endpoints...")

        # Test basic health check
        self.test_endpoint("GET", "/health", description="Basic health check")

        # Test detailed health check
        self.test_endpoint(
            "GET", "/health/detailed", description="Detailed health check"
        )

        # Test readiness check
        self.test_endpoint("GET", "/health/ready", description="Readiness check")

        # Test liveness check
        self.test_endpoint("GET", "/health/live", description="Liveness check")

    def test_student_crud(self):
        """Test student CRUD operations."""
        self.log("Testing student CRUD operations...")

        # Test data
        student_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
        }

        # Create student
        success, response = self.test_endpoint(
            "POST",
            "/students/",
            data=student_data,
            expected_status=201,
            description="Create student",
        )

        if success and response:
            student = response.json()
            student_id = student["data"]["id"]
            self.test_data["student_id"] = student_id
            self.log(f"Created student with ID: {student_id}")

        # Get all students
        self.test_endpoint("GET", "/students/", description="Get all students")

        # Get student by ID
        if "student_id" in self.test_data:
            self.test_endpoint(
                "GET",
                f"/students/{self.test_data['student_id']}",
                description="Get student by ID",
            )

        # Update student
        if "student_id" in self.test_data:
            updated_data = {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1234567891",
            }
            self.test_endpoint(
                "PUT",
                f"/students/{self.test_data['student_id']}",
                data=updated_data,
                description="Update student",
            )

    def test_application_crud(self):
        """Test application CRUD operations."""
        self.log("Testing application CRUD operations...")

        if "student_id" not in self.test_data:
            self.log("Skipping application tests - no student ID available", "WARNING")
            return

        # Test data
        application_data = {
            "student_id": self.test_data["student_id"],
            "university_name": "University of California",
            "program_name": "Computer Science",
            "intake": "Jan 2026",
            "status": "Building Application",
        }

        # Create application
        success, response = self.test_endpoint(
            "POST",
            "/applications",
            data=application_data,
            expected_status=201,
            description="Create application",
        )

        if success and response:
            application = response.json()
            application_id = application["data"]["id"]
            self.test_data["application_id"] = application_id
            self.log(f"Created application with ID: {application_id}")

        # Get all applications
        self.test_endpoint("GET", "/applications", description="Get all applications")

        # Get application by ID
        if "application_id" in self.test_data:
            self.test_endpoint(
                "GET",
                f"/applications/{self.test_data['application_id']}",
                description="Get application by ID",
            )

        # Update application
        if "application_id" in self.test_data:
            updated_data = {
                "student_id": self.test_data["student_id"],
                "university_name": "University of California",
                "program_name": "Computer Science",
                "intake": "Jan 2026",
                "status": "Application Submitted to University",
            }
            self.test_endpoint(
                "PUT",
                f"/applications/{self.test_data['application_id']}",
                data=updated_data,
                description="Update application",
            )

    def test_status_calculation(self):
        """Test status calculation functionality."""
        self.log("Testing status calculation...")

        if "student_id" not in self.test_data:
            self.log(
                "Skipping status calculation tests - no student ID available", "WARNING"
            )
            return

        # Test getting student status
        self.test_endpoint(
            "GET",
            f"/students/{self.test_data['student_id']}/status",
            description="Get student status",
        )

        # Create multiple applications with different statuses
        applications = [
            {
                "student_id": self.test_data["student_id"],
                "university_name": "Stanford University",
                "program_name": "Data Science",
                "intake": "Feb 2026",
                "status": "Offer Received",
            },
            {
                "student_id": self.test_data["student_id"],
                "university_name": "MIT",
                "program_name": "Artificial Intelligence",
                "intake": "Mar 2026",
                "status": "Visa Approved",
            },
        ]

        for i, app_data in enumerate(applications):
            success, response = self.test_endpoint(
                "POST",
                "/applications",
                data=app_data,
                expected_status=201,
                description=f"Create application {i+1} for status testing",
            )

            if success and response:
                app = response.json()
                self.test_data[f"application_{i+1}_id"] = app["data"]["id"]

        # Test status calculation after multiple applications
        self.test_endpoint(
            "GET",
            f"/students/{self.test_data['student_id']}/status",
            description="Get updated student status",
        )

    def test_pagination_and_filtering(self):
        """Test pagination and filtering functionality."""
        self.log("Testing pagination and filtering...")

        # Test pagination
        self.test_endpoint(
            "GET", "/students/?page=1&per_page=5", description="Test student pagination"
        )

        self.test_endpoint(
            "GET",
            "/applications?page=1&per_page=5",
            description="Test application pagination",
        )

        # Test filtering
        self.test_endpoint(
            "GET", "/students/?search=John", description="Test student search"
        )

        self.test_endpoint(
            "GET",
            "/applications?status=Building Application",
            description="Test application status filtering",
        )

    def test_validation_errors(self):
        """Test validation error handling."""
        self.log("Testing validation error handling...")

        # Test invalid student data
        invalid_student = {
            "name": "",  # Empty name
            "email": "invalid-email",  # Invalid email
            "phone": "",  # Empty phone
        }
        self.test_endpoint(
            "POST",
            "/students/",
            data=invalid_student,
            expected_status=400,
            description="Test invalid student data validation",
        )

        # Test invalid application data
        invalid_application = {
            "student_id": 99999,  # Non-existent student
            "university_name": "",  # Empty university
            "program_name": "",  # Empty program
            "intake": "Invalid Date",  # Invalid intake
            "status": "Invalid Status",  # Invalid status
        }
        self.test_endpoint(
            "POST",
            "/applications",
            data=invalid_application,
            expected_status=400,
            description="Test invalid application data validation",
        )

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        self.log("Testing rate limiting...")

        # Make multiple rapid requests to test rate limiting
        for i in range(5):
            success, response = self.test_endpoint(
                "GET", "/students/", description=f"Rate limit test request {i+1}"
            )

            if response and response.status_code == 429:
                self.log("Rate limiting is working correctly", "INFO")
                break
            time.sleep(0.1)  # Small delay between requests

    def cleanup_test_data(self):
        """Clean up test data."""
        self.log("Cleaning up test data...")

        # Delete applications first (due to foreign key constraints)
        for key, value in self.test_data.items():
            if key.startswith("application"):
                self.test_endpoint(
                    "DELETE",
                    f"/applications/{value}",
                    expected_status=204,
                    description=f"Delete {key}",
                )

        # Delete student
        if "student_id" in self.test_data:
            self.test_endpoint(
                "DELETE",
                f"/students/{self.test_data['student_id']}",
                expected_status=204,
                description="Delete test student",
            )

    def run_all_tests(self):
        """Run all tests."""
        self.log("Starting comprehensive API testing...")
        self.log(f"Testing API at: {self.base_url}")

        try:
            # Test health endpoints
            self.test_health_endpoints()

            # Test CRUD operations
            self.test_student_crud()
            self.test_application_crud()

            # Test business logic
            self.test_status_calculation()

            # Test advanced features
            self.test_pagination_and_filtering()
            self.test_validation_errors()
            self.test_rate_limiting()

        except KeyboardInterrupt:
            self.log("Testing interrupted by user", "WARNING")
        except Exception as e:
            self.log(f"Unexpected error during testing: {str(e)}", "ERROR")
        finally:
            # Clean up test data
            self.cleanup_test_data()

            # Print results
            self.print_results()

    def print_results(self):
        """Print test results summary."""
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (
            (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        )

        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {self.results['passed']}")
        self.log(f"Failed: {self.results['failed']}")
        self.log(f"Success Rate: {success_rate:.1f}%")

        if self.results["errors"]:
            self.log("\nERRORS:")
            for error in self.results["errors"]:
                self.log(f"  - {error}", "ERROR")

        if self.results["failed"] == 0:
            self.log("\n🎉 All tests passed! API is working correctly.", "INFO")
            return True
        else:
            self.log(
                f"\n❌ {self.results['failed']} test(s) failed. Please check the errors above.",
                "ERROR",
            )
            return False


def main():
    """Main function to run the API tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Student Platform API")
    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="Base URL of the API (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--no-cleanup", action="store_true", help="Skip cleanup of test data"
    )

    args = parser.parse_args()

    tester = StudentPlatformAPITester(args.url)

    if args.no_cleanup:
        tester.cleanup_test_data = lambda: None

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
