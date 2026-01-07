"""
Database initialization script
Creates initial admin, faculty, and student users, and sample exam
"""
from backend.app import app, db
from backend.models.models import User, Exam
from datetime import datetime, timedelta

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.create_all()
        
        # Check if users already exist
        if User.query.first():
            print("Database already initialized. Skipping...")
            return
        
        print("Creating sample users...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            full_name='System Administrator'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create faculty users
        faculty1 = User(
            username='faculty1',
            email='faculty1@example.com',
            role='faculty',
            full_name='Dr. John Smith'
        )
        faculty1.set_password('password123')
        db.session.add(faculty1)
        
        # Create student users
        students = [
            ('student1', 'student1@example.com', 'Alice Johnson'),
            ('student2', 'student2@example.com', 'Bob Williams'),
            ('student3', 'student3@example.com', 'Carol Davis'),
            ('student4', 'student4@example.com', 'David Brown'),
            ('student5', 'student5@example.com', 'Eve Martinez'),
        ]
        
        for username, email, full_name in students:
            student = User(
                username=username,
                email=email,
                role='student',
                full_name=full_name
            )
            student.set_password('password123')
            db.session.add(student)
        
        db.session.commit()
        print(f"Created {len(students) + 2} users (1 admin, 1 faculty, {len(students)} students)")
        
        # Create sample exam
        print("Creating sample exam...")
        exam = Exam(
            title='Final Exam - Computer Science 101',
            description='Final examination covering all course topics',
            duration_minutes=120,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=7),
            created_by=faculty1.id,
            is_active=True
        )
        db.session.add(exam)
        
        exam2 = Exam(
            title='Midterm Exam - Data Structures',
            description='Midterm examination on data structures and algorithms',
            duration_minutes=90,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=3),
            created_by=faculty1.id,
            is_active=True
        )
        db.session.add(exam2)
        
        db.session.commit()
        print("Created 2 sample exams")
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nSample Credentials:")
        print("-" * 50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nFaculty:")
        print("  Username: faculty1")
        print("  Password: password123")
        print("\nStudents:")
        print("  Username: student1 (or student2-5)")
        print("  Password: password123")
        print("="*50)

if __name__ == '__main__':
    init_database()
