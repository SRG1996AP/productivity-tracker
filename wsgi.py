"""
WSGI entry point for production servers (Gunicorn, Waitress, etc.)
"""
import os
from app import create_app, db
from app.models import Department

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
    except Exception as e:
        print(f"Warning: Database initialization issue: {e}")

if __name__ == "__main__":
    app.run()
