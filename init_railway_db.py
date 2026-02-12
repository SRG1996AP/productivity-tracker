"""
Initialize database for Railway deployment
"""
import os
from app import create_app, db, bcrypt
from app.models import Department, User

# Department data from the Excel file - MUST match local init_db.py
DEPARTMENTS = [
    {
        'name': 'IT - Daily Tracking',
        'description': 'Information Technology - Daily operational tracking for systems and applications'
    },
    {
        'name': 'HR - Daily Tracking',
        'description': 'Human Resources - Daily tracking for employee processes and requirements'
    },
    {
        'name': 'TA - Daily Tracking',
        'description': 'Talent Acquisition - Daily tracking for hiring projects and campaigns'
    },
    {
        'name': 'Finance - Daily Tracking',
        'description': 'Finance - Daily tracking for financial operations and transactions'
    },
    {
        'name': 'QA - Daily Tracking',
        'description': 'Quality Assurance - Daily tracking for quality audits and standards'
    },
    {
        'name': 'Training - Daily Tracking',
        'description': 'Training - Daily tracking for training programs and employee development'
    },
    {
        'name': 'RTA - Daily Tracking',
        'description': 'Recruitment - Daily tracking for recruitment and talent management'
    },
    {
        'name': 'Operations Leaders - Daily',
        'description': 'Operations Leaders - Daily tracking for operations leadership activities'
    },
    {
        'name': 'Management',
        'description': 'Management - Department for administrative and managerial users with access to all dashboards'
    }
]

def init_db():
    """Create all database tables and add initial departments"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create instance folder if it doesn't exist
            os.makedirs('instance', exist_ok=True)
            
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Check if departments exist, if not create them
            if Department.query.count() == 0:
                for dept_data in DEPARTMENTS:
                    dept = Department(**dept_data)
                    db.session.add(dept)
                    print(f"  → Added department: {dept_data['name']}")
                
                db.session.commit()
                print(f"✓ Created {len(DEPARTMENTS)} departments")
            else:
                print(f"✓ Found {Department.query.count()} existing departments")
            
            # Create default admin user if no users exist
            if User.query.count() == 0:
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(
                    name='Admin User',
                    employee_id='ADMIN001',
                    department='Management',
                    login_id='admin',
                    password=hashed_pw,
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✓ Created default admin user (login: admin, password: admin123)")
            else:
                print(f"✓ Found {User.query.count()} existing users")
            
            print("✓ Database initialization complete!")
            return True
            
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = init_db()
    exit(0 if success else 1)
