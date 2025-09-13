"""
Data Factories for Student Platform API
Generate dummy data for testing and development.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker
from app.models import Student, Application, db
from app.services.status_calculator import StatusCalculator

# Initialize Faker for generating realistic dummy data
fake = Faker()


class StudentFactory:
    """Factory for creating Student instances with realistic dummy data."""
    
    # Common first names for students
    FIRST_NAMES = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Jessica",
        "Robert", "Ashley", "William", "Amanda", "Richard", "Jennifer", "Charles",
        "Lisa", "Joseph", "Nancy", "Thomas", "Karen", "Christopher", "Betty",
        "Daniel", "Helen", "Matthew", "Sandra", "Anthony", "Donna", "Mark",
        "Carol", "Donald", "Ruth", "Steven", "Sharon", "Paul", "Michelle",
        "Andrew", "Laura", "Joshua", "Sarah", "Kenneth", "Kimberly", "Kevin",
        "Deborah", "Brian", "Dorothy", "George", "Lisa", "Timothy", "Nancy",
        "Ronald", "Karen", "Jason", "Betty", "Edward", "Helen", "Jeffrey",
        "Sandra", "Ryan", "Donna", "Jacob", "Carol", "Gary", "Ruth", "Nicholas",
        "Sharon", "Eric", "Michelle", "Jonathan", "Laura", "Stephen", "Sarah",
        "Larry", "Kimberly", "Justin", "Deborah", "Scott", "Dorothy", "Brandon",
        "Lisa", "Benjamin", "Nancy", "Samuel", "Karen", "Gregory", "Betty",
        "Alexander", "Helen", "Patrick", "Sandra", "Jack", "Donna", "Dennis",
        "Carol", "Jerry", "Ruth", "Tyler", "Sharon", "Aaron", "Michelle",
        "Jose", "Laura", "Henry", "Sarah", "Adam", "Kimberly", "Douglas",
        "Deborah", "Nathan", "Dorothy", "Peter", "Lisa", "Zachary", "Nancy",
        "Kyle", "Karen", "Noah", "Betty", "Alan", "Helen", "Ethan", "Sandra",
        "Jeremy", "Donna", "Christian", "Carol", "Sean", "Ruth", "Eric",
        "Sharon", "Ian", "Michelle", "Nathaniel", "Laura", "Timothy", "Sarah"
    ]
    
    # Common last names
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
        "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
        "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
        "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
        "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
        "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
        "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
        "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
        "Ross", "Foster", "Jimenez"
    ]
    
    # Common email domains for students
    EMAIL_DOMAINS = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "student.edu",
        "university.edu", "college.edu", "school.edu", "academic.edu"
    ]
    
    # Common phone number patterns
    PHONE_PATTERNS = [
        "+1-{}-{}-{}",  # US format
        "+44-{}-{}-{}",  # UK format
        "+91-{}-{}-{}",  # India format
        "+86-{}-{}-{}",  # China format
        "+61-{}-{}-{}",  # Australia format
    ]
    
    @classmethod
    def create_student(
        cls,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> Student:
        """
        Create a single Student instance with dummy data.
        
        Args:
            name: Custom name (if None, will be generated)
            email: Custom email (if None, will be generated)
            phone: Custom phone (if None, will be generated)
            notes: Custom notes (if None, will be generated)
            **kwargs: Additional fields to set
            
        Returns:
            Student instance with dummy data
        """
        # Generate name if not provided
        if name is None:
            first_name = random.choice(cls.FIRST_NAMES)
            last_name = random.choice(cls.LAST_NAMES)
            name = f"{first_name} {last_name}"
        
        # Generate email if not provided
        if email is None:
            first_name, last_name = name.split(' ', 1)
            domain = random.choice(cls.EMAIL_DOMAINS)
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
        
        # Generate phone if not provided
        if phone is None:
            pattern = random.choice(cls.PHONE_PATTERNS)
            phone = pattern.format(
                random.randint(100, 999),
                random.randint(100, 999),
                random.randint(1000, 9999)
            )
        
        # Generate notes if not provided
        if notes is None:
            notes = fake.sentence(nb_words=random.randint(5, 15))
        
        # Create student data
        student_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'notes': notes,
            **kwargs
        }
        
        return Student(**student_data)
    
    @classmethod
    def create_students(cls, count: int = 10, **kwargs) -> List[Student]:
        """
        Create multiple Student instances.
        
        Args:
            count: Number of students to create
            **kwargs: Additional fields to set for all students
            
        Returns:
            List of Student instances
        """
        students = []
        for _ in range(count):
            student = cls.create_student(**kwargs)
            students.append(student)
        return students
    
    @classmethod
    def create_and_save_students(cls, count: int = 10, **kwargs) -> List[Student]:
        """
        Create and save multiple Student instances to database.
        
        Args:
            count: Number of students to create
            **kwargs: Additional fields to set for all students
            
        Returns:
            List of saved Student instances
        """
        students = cls.create_students(count, **kwargs)
        
        # Save to database
        for student in students:
            student.save()
        
        return students


class ApplicationFactory:
    """Factory for creating Application instances with realistic dummy data."""
    
    # University names
    UNIVERSITIES = [
        "Harvard University", "Stanford University", "Massachusetts Institute of Technology",
        "University of California, Berkeley", "Yale University", "Princeton University",
        "Columbia University", "University of Chicago", "University of Pennsylvania",
        "California Institute of Technology", "Duke University", "Northwestern University",
        "Johns Hopkins University", "Dartmouth College", "Brown University",
        "Vanderbilt University", "Rice University", "Washington University in St. Louis",
        "Cornell University", "University of Notre Dame", "Emory University",
        "Georgetown University", "Carnegie Mellon University", "University of Virginia",
        "University of North Carolina at Chapel Hill", "Wake Forest University",
        "Tufts University", "University of Southern California", "New York University",
        "University of Rochester", "Boston University", "Georgia Institute of Technology",
        "University of Illinois at Urbana-Champaign", "University of Wisconsin-Madison",
        "University of Washington", "University of Texas at Austin", "Ohio State University",
        "Pennsylvania State University", "University of Michigan", "University of California, Los Angeles",
        "University of California, San Diego", "University of California, Davis",
        "University of California, Irvine", "University of California, Santa Barbara",
        "University of California, Santa Cruz", "University of California, Riverside",
        "University of California, Merced", "University of California, San Francisco",
        "University of California, Hastings", "University of California, Berkeley Extension"
    ]
    
    # Program names
    PROGRAMS = [
        "Computer Science", "Data Science", "Artificial Intelligence", "Machine Learning",
        "Software Engineering", "Information Technology", "Cybersecurity", "Computer Engineering",
        "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Chemical Engineering",
        "Biomedical Engineering", "Aerospace Engineering", "Industrial Engineering", "Materials Science",
        "Physics", "Mathematics", "Statistics", "Applied Mathematics", "Pure Mathematics",
        "Biology", "Chemistry", "Biochemistry", "Molecular Biology", "Genetics", "Neuroscience",
        "Psychology", "Cognitive Science", "Economics", "Business Administration", "Finance",
        "Marketing", "International Business", "Accounting", "Management", "Entrepreneurship",
        "Public Policy", "Political Science", "International Relations", "Law", "Medicine",
        "Nursing", "Pharmacy", "Dentistry", "Veterinary Medicine", "Public Health",
        "Social Work", "Education", "Journalism", "Communications", "Media Studies",
        "Film Studies", "Theater", "Music", "Fine Arts", "Graphic Design", "Architecture",
        "Urban Planning", "Environmental Science", "Sustainability", "Climate Science",
        "Geology", "Geography", "Anthropology", "Sociology", "History", "Philosophy",
        "Literature", "Creative Writing", "Linguistics", "Foreign Languages", "Translation"
    ]
    
    # Intake periods
    INTAKES = [
        "Fall 2024", "Spring 2025", "Summer 2025", "Fall 2025", "Spring 2026",
        "Summer 2026", "Fall 2026", "Spring 2027", "Summer 2027", "Fall 2027",
        "Winter 2025", "Winter 2026", "Winter 2027"
    ]
    
    # Application statuses with weights
    STATUSES = [
        "Building Application",
        "Application Submitted to University",
        "Offer Received",
        "Offer Accepted by Student",
        "Visa Approved",
        "Dropped"
    ]
    
    @classmethod
    def create_application(
        cls,
        student_id: int,
        university_name: Optional[str] = None,
        program_name: Optional[str] = None,
        intake: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> Application:
        """
        Create a single Application instance with dummy data.
        
        Args:
            student_id: ID of the student this application belongs to
            university_name: Custom university name (if None, will be generated)
            program_name: Custom program name (if None, will be generated)
            intake: Custom intake period (if None, will be generated)
            status: Custom status (if None, will be generated)
            **kwargs: Additional fields to set
            
        Returns:
            Application instance with dummy data
        """
        # Generate university name if not provided
        if university_name is None:
            university_name = random.choice(cls.UNIVERSITIES)
        
        # Generate program name if not provided
        if program_name is None:
            program_name = random.choice(cls.PROGRAMS)
        
        # Generate intake if not provided
        if intake is None:
            intake = random.choice(cls.INTAKES)
        
        # Generate status if not provided
        if status is None:
            # Weight the statuses - more likely to be in earlier stages
            status_weights = [0.3, 0.25, 0.2, 0.15, 0.08, 0.02]  # Building, Submitted, Offer, etc.
            status = random.choices(cls.STATUSES, weights=status_weights)[0]
        
        # Create application data
        application_data = {
            'student_id': student_id,
            'university_name': university_name,
            'program_name': program_name,
            'intake': intake,
            'status': status,
            **kwargs
        }
        
        return Application(**application_data)
    
    @classmethod
    def create_applications_for_student(
        cls,
        student_id: int,
        count: int = 3,
        **kwargs
    ) -> List[Application]:
        """
        Create multiple Application instances for a specific student.
        
        Args:
            student_id: ID of the student
            count: Number of applications to create
            **kwargs: Additional fields to set for all applications
            
        Returns:
            List of Application instances
        """
        applications = []
        for _ in range(count):
            application = cls.create_application(student_id, **kwargs)
            applications.append(application)
        return applications
    
    @classmethod
    def create_and_save_applications_for_student(
        cls,
        student_id: int,
        count: int = 3,
        **kwargs
    ) -> List[Application]:
        """
        Create and save multiple Application instances for a specific student.
        
        Args:
            student_id: ID of the student
            count: Number of applications to create
            **kwargs: Additional fields to set for all applications
            
        Returns:
            List of saved Application instances
        """
        applications = cls.create_applications_for_student(student_id, count, **kwargs)
        
        # Save to database
        for application in applications:
            application.save()
        
        return applications


class DataFactory:
    """Main factory class for creating comprehensive dummy data."""
    
    @classmethod
    def create_sample_data(
        cls,
        student_count: int = 20,
        applications_per_student: int = 3,
        update_student_status: bool = True
    ) -> Dict[str, Any]:
        """
        Create a complete set of sample data with students and applications.
        
        Args:
            student_count: Number of students to create
            applications_per_student: Number of applications per student
            update_student_status: Whether to update student highest status
            
        Returns:
            Dictionary with created data summary
        """
        print(f"Creating {student_count} students with {applications_per_student} applications each...")
        
        # Create students
        students = StudentFactory.create_and_save_students(student_count)
        print(f"✅ Created {len(students)} students")
        
        # Create applications for each student
        total_applications = 0
        for student in students:
            applications = ApplicationFactory.create_and_save_applications_for_student(
                student.id, applications_per_student
            )
            total_applications += len(applications)
            
            # Update student's highest status if requested
            if update_student_status:
                StatusCalculator.update_student_highest_status(student.id)
        
        print(f"✅ Created {total_applications} applications")
        
        return {
            'students_created': len(students),
            'applications_created': total_applications,
            'students': students,
            'total_students': Student.query.filter_by(is_deleted=False).count(),
            'total_applications': Application.query.filter_by(is_deleted=False).count()
        }
    
    @classmethod
    def create_realistic_scenario(cls) -> Dict[str, Any]:
        """
        Create a realistic scenario with varied student profiles.
        
        Returns:
            Dictionary with created data summary
        """
        print("Creating realistic student scenario...")
        
        # Create students with different profiles
        students = []
        
        # High-achieving student with multiple offers
        high_achiever = StudentFactory.create_student(
            name="Alex Johnson",
            email="alex.johnson@student.edu",
            phone="+1-555-0123",
            notes="Excellent academic record, multiple scholarship offers"
        )
        high_achiever.save()
        students.append(high_achiever)
        
        # Create applications for high achiever
        ApplicationFactory.create_and_save_applications_for_student(
            high_achiever.id, 5,
            university_name="Harvard University",
            program_name="Computer Science",
            status="Offer Received"
        )
        ApplicationFactory.create_and_save_applications_for_student(
            high_achiever.id, 1,
            university_name="Stanford University",
            program_name="Data Science",
            status="Offer Accepted by Student"
        )
        
        # Average student with mixed results
        average_student = StudentFactory.create_student(
            name="Sarah Williams",
            email="sarah.williams@student.edu",
            phone="+1-555-0456",
            notes="Good student, exploring different options"
        )
        average_student.save()
        students.append(average_student)
        
        # Create mixed applications
        ApplicationFactory.create_and_save_applications_for_student(
            average_student.id, 1,
            university_name="University of California, Berkeley",
            program_name="Psychology",
            status="Application Submitted to University"
        )
        ApplicationFactory.create_and_save_applications_for_student(
            average_student.id, 1,
            university_name="University of Michigan",
            program_name="Business Administration",
            status="Building Application"
        )
        ApplicationFactory.create_and_save_applications_for_student(
            average_student.id, 1,
            university_name="Pennsylvania State University",
            program_name="Marketing",
            status="Dropped"
        )
        
        # Struggling student
        struggling_student = StudentFactory.create_student(
            name="Mike Chen",
            email="mike.chen@student.edu",
            phone="+1-555-0789",
            notes="Working on improving grades, considering gap year"
        )
        struggling_student.save()
        students.append(struggling_student)
        
        # Create applications for struggling student
        ApplicationFactory.create_and_save_applications_for_student(
            struggling_student.id, 2,
            university_name="Community College",
            program_name="General Studies",
            status="Building Application"
        )
        
        # Create some random students
        random_students = StudentFactory.create_and_save_students(7)
        students.extend(random_students)
        
        # Create applications for random students
        for student in random_students:
            app_count = random.randint(1, 4)
            ApplicationFactory.create_and_save_applications_for_student(
                student.id, app_count
            )
        
        # Update all student statuses
        for student in students:
            StatusCalculator.update_student_highest_status(student.id)
        
        print(f"✅ Created realistic scenario with {len(students)} students")
        
        return {
            'students_created': len(students),
            'scenario_type': 'realistic',
            'total_students': Student.query.filter_by(is_deleted=False).count(),
            'total_applications': Application.query.filter_by(is_deleted=False).count()
        }
    
    @classmethod
    def export_data_to_dict(cls) -> Dict[str, Any]:
        """
        Export all current data to dictionary format.
        
        Returns:
            Dictionary with all students and applications
        """
        students = Student.query.filter_by(is_deleted=False).all()
        applications = Application.query.filter_by(is_deleted=False).all()
        
        return {
            'students': [student.to_dict(include_applications=True) for student in students],
            'applications': [application.to_dict() for application in applications],
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_students': len(students),
            'total_applications': len(applications)
        }
    
    @classmethod
    def clear_all_data(cls, hard_delete: bool = False) -> Dict[str, int]:
        """
        Clear all students and applications from database.
        
        Args:
            hard_delete: If True, permanently delete records. If False, soft delete.
        
        Returns:
            Dictionary with deletion summary
        """
        # Get counts before deletion
        student_count = Student.query.filter_by(is_deleted=False).count()
        application_count = Application.query.filter_by(is_deleted=False).count()
        
        if hard_delete:
            # Hard delete all applications first (due to foreign key constraints)
            Application.query.delete()
            # Hard delete all students
            Student.query.delete()
            db.session.commit()
        else:
            # Soft delete all applications
            applications = Application.query.filter_by(is_deleted=False).all()
            for application in applications:
                application.soft_delete()
            
            # Soft delete all students
            students = Student.query.filter_by(is_deleted=False).all()
            for student in students:
                student.soft_delete()
        
        print(f"✅ Deleted {student_count} students and {application_count} applications")
        
        return {
            'students_deleted': student_count,
            'applications_deleted': application_count
        }
