#!/usr/bin/env python3
"""
Data Management CLI for Student Platform API
Manage dummy data creation, export, and deletion.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models import db, Student, Application
from app.factories import DataFactory, StudentFactory, ApplicationFactory


def setup_app():
    """Set up Flask application context."""
    app = create_app()
    return app


def create_sample_data(args):
    """Create sample data."""
    with setup_app().app_context():
        if args.scenario == 'realistic':
            result = DataFactory.create_realistic_scenario()
        else:
            result = DataFactory.create_sample_data(
                student_count=args.students,
                applications_per_student=args.applications,
                update_student_status=not args.no_status_update
            )
        
        print(f"\n📊 Data Creation Summary:")
        print(f"   Students created: {result['students_created']}")
        print(f"   Total students in DB: {result['total_students']}")
        print(f"   Total applications in DB: {result['total_applications']}")
        
        if args.export:
            export_data(args)


def export_data(args):
    """Export data to JSON file."""
    with setup_app().app_context():
        data = DataFactory.export_data_to_dict()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = args.output or f"student_data_export_{timestamp}.json"
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"\n📁 Data exported to: {filename}")
        print(f"   Students: {data['total_students']}")
        print(f"   Applications: {data['total_applications']}")
        print(f"   Export time: {data['export_timestamp']}")


def import_data(args):
    """Import data from JSON file."""
    with setup_app().app_context():
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return
        
        with open(args.file, 'r') as f:
            data = json.load(f)
        
        print(f"📥 Importing data from: {args.file}")
        print(f"   Students to import: {data.get('total_students', 0)}")
        print(f"   Applications to import: {data.get('total_applications', 0)}")
        
        if not args.force:
            response = input("\n⚠️  This will add data to the existing database. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Import cancelled.")
                return
        
        # Import students
        students_imported = 0
        applications_imported = 0
        student_id_mapping = {}  # Map old IDs to new IDs
        
        for student_data in data.get('students', []):
            # Store the old ID before removing it
            old_id = student_data.get('id')
            
            # Remove fields that shouldn't be set during creation
            student_data.pop('id', None)
            student_data.pop('created_at', None)
            student_data.pop('updated_at', None)
            student_data.pop('applications', None)  # Will be imported separately
            student_data.pop('active_applications_count', None)  # Computed field
            student_data.pop('total_applications_count', None)  # Computed field
            student_data.pop('has_active_applications', None)  # Computed field
            student_data.pop('display_name', None)  # Computed field
            
            # Handle None values for optional fields
            if 'notes' not in student_data:
                student_data['notes'] = None
            
            try:
                student = Student(**student_data)
                student.save()
                students_imported += 1
                
                # Map old ID to new ID
                if old_id is not None:
                    student_id_mapping[old_id] = student.id
                    
            except Exception as e:
                print(f"Error creating student {student_data.get('name', 'Unknown')}: {e}")
                print(f"Student data: {student_data}")
                raise
        
        # Import applications
        for application_data in data.get('applications', []):
            # Map old student ID to new student ID
            old_student_id = application_data.get('student_id')
            if old_student_id in student_id_mapping:
                application_data['student_id'] = student_id_mapping[old_student_id]
            else:
                print(f"Warning: No mapping found for student_id {old_student_id}, skipping application")
                continue
            
            # Remove fields that shouldn't be set during creation
            application_data.pop('id', None)
            application_data.pop('created_at', None)
            application_data.pop('updated_at', None)
            application_data.pop('status_weight', None)  # Computed field
            application_data.pop('is_active', None)  # Computed field
            application_data.pop('is_successful', None)  # Computed field
            
            try:
                application = Application(**application_data)
                application.save()
                applications_imported += 1
            except Exception as e:
                print(f"Error creating application: {e}")
                print(f"Application data: {application_data}")
                raise
        
        # Update student statuses
        if not args.no_status_update:
            from app.services.status_calculator import StatusCalculator
            students = Student.query.filter_by(is_deleted=False).all()
            for student in students:
                try:
                    StatusCalculator.update_student_highest_status(student.id)
                except Exception as e:
                    print(f"Error updating status for student {student.name}: {e}")
                    raise
        
        print(f"\n✅ Import completed:")
        print(f"   Students imported: {students_imported}")
        print(f"   Applications imported: {applications_imported}")
        print(f"   Total students in DB: {Student.query.filter_by(is_deleted=False).count()}")
        print(f"   Total applications in DB: {Application.query.filter_by(is_deleted=False).count()}")


def clear_data(args):
    """Clear all data from database."""
    with setup_app().app_context():
        # Get current counts
        student_count = Student.query.filter_by(is_deleted=False).count()
        application_count = Application.query.filter_by(is_deleted=False).count()
        
        if student_count == 0 and application_count == 0:
            print("📭 Database is already empty.")
            return
        
        print(f"🗑️  Current data:")
        print(f"   Students: {student_count}")
        print(f"   Applications: {application_count}")
        
        if not args.force:
            response = input(f"\n⚠️  This will delete ALL data. Are you sure? (y/N): ")
            if response.lower() != 'y':
                print("Deletion cancelled.")
                return
        
        result = DataFactory.clear_all_data(hard_delete=args.hard_delete)
        
        print(f"\n✅ Data cleared:")
        print(f"   Students deleted: {result['students_deleted']}")
        print(f"   Applications deleted: {result['applications_deleted']}")


def show_stats(args):
    """Show database statistics."""
    with setup_app().app_context():
        student_count = Student.query.filter_by(is_deleted=False).count()
        application_count = Application.query.filter_by(is_deleted=False).count()
        
        # Get status distribution
        status_counts = {}
        applications = Application.query.filter_by(is_deleted=False).all()
        for app in applications:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1
        
        # Get students with highest status
        students_with_status = Student.query.filter(
            Student.highest_status.isnot(None),
            Student.is_deleted == False
        ).count()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total Students: {student_count}")
        print(f"   Total Applications: {application_count}")
        print(f"   Students with calculated status: {students_with_status}")
        
        if status_counts:
            print(f"\n📈 Application Status Distribution:")
            for status, count in sorted(status_counts.items()):
                percentage = (count / application_count) * 100
                print(f"   {status}: {count} ({percentage:.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Manage dummy data for Student Platform API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
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
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create sample data')
    create_parser.add_argument('--students', type=int, default=20, help='Number of students to create')
    create_parser.add_argument('--applications', type=int, default=3, help='Applications per student')
    create_parser.add_argument('--scenario', choices=['basic', 'realistic'], default='basic', help='Data scenario type')
    create_parser.add_argument('--no-status-update', action='store_true', help='Skip updating student status')
    create_parser.add_argument('--export', action='store_true', help='Export data after creation')
    create_parser.add_argument('--output', help='Output file for export')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to JSON')
    export_parser.add_argument('--output', help='Output filename')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from JSON')
    import_parser.add_argument('--file', required=True, help='JSON file to import')
    import_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    import_parser.add_argument('--no-status-update', action='store_true', help='Skip updating student status')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all data')
    clear_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    clear_parser.add_argument('--hard-delete', action='store_true', help='Permanently delete records (not just soft delete)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Set up environment
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/student_platform_db')
    os.environ.setdefault('FLASK_ENV', 'development')
    
    try:
        if args.command == 'create':
            create_sample_data(args)
        elif args.command == 'export':
            export_data(args)
        elif args.command == 'import':
            import_data(args)
        elif args.command == 'clear':
            clear_data(args)
        elif args.command == 'stats':
            show_stats(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
