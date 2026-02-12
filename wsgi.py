"""
WSGI entry point for production servers (Gunicorn, Waitress, etc.)
"""
import os
from app import create_app, db, bcrypt
from app.models import Department, User

app = create_app()

# Department data from the Excel file - MUST match local init_db.py
DEPARTMENTS = [
    {'name': 'IT - Daily Tracking', 'description': 'Information Technology - Daily operational tracking for systems and applications'},
    {'name': 'HR - Daily Tracking', 'description': 'Human Resources - Daily tracking for employee processes and requirements'},
    {'name': 'TA - Daily Tracking', 'description': 'Talent Acquisition - Daily tracking for hiring projects and campaigns'},
    {'name': 'Finance - Daily Tracking', 'description': 'Finance - Daily tracking for financial operations and transactions'},
    {'name': 'QA - Daily Tracking', 'description': 'Quality Assurance - Daily tracking for quality audits and standards'},
    {'name': 'Training - Daily Tracking', 'description': 'Training - Daily tracking for training programs and employee development'},
    {'name': 'RTA - Daily Tracking', 'description': 'Recruitment - Daily tracking for recruitment and talent management'},
    {'name': 'Operations Leaders - Daily', 'description': 'Operations Leaders - Daily tracking for operations leadership activities'},
    {'name': 'Management', 'description': 'Management - Department for administrative and managerial users with access to all dashboards'}
]

# Ensure database is initialized on startup
with app.app_context():
    try:
        # Create instance folder if it doesn't exist
        os.makedirs('instance', exist_ok=True)
        
        # Create all tables
        db.create_all()
        print("Database tables verified/created")
        
        # Ensure departments exist
        if Department.query.count() == 0:
            for dept_data in DEPARTMENTS:
                dept = Department(**dept_data)
                db.session.add(dept)
            db.session.commit()
            print(f"Created {len(DEPARTMENTS)} departments")
        
        # Ensure default admin exists
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
            print("Created default admin user")
    except Exception as e:
        print(f"Warning: Database initialization issue: {e}")

if __name__ == "__main__":
    app.run()
