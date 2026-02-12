"""
WSGI entry point for production servers (Gunicorn, Waitress, etc.)
"""
import os
from app import create_app, db, bcrypt
from app.models import Department, User

app = create_app()

# Ensure database is initialized on startup
with app.app_context():
    try:
        # Create instance folder if it doesn't exist
        os.makedirs('instance', exist_ok=True)
        
        # Create all tables
        db.create_all()
        print("Database tables verified/created")
        
        # Ensure basic departments exist
        if Department.query.count() == 0:
            departments = [
                Department(name='IT Support', description='Information Technology Support and Maintenance'),
                Department(name='Customer Service', description='Customer Relations and Support'),
                Department(name='Operations', description='Day-to-day Operations Management'),
                Department(name='Finance', description='Financial Management and Accounting'),
                Department(name='HR', description='Human Resources Management')
            ]
            for dept in departments:
                db.session.add(dept)
            db.session.commit()
            print(f"Created {len(departments)} departments")
        
        # Ensure default admin exists
        if User.query.count() == 0:
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                name='Admin User',
                employee_id='ADMIN001',
                department='IT Support',
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
