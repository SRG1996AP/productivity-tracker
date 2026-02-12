#!/usr/bin/env python3
"""
Script to create test users for the application.
"""

from app import create_app, db, bcrypt
from app.models import User

def create_test_users():
    """Create test users (admin and regular user)."""
    app = create_app()
    
    with app.app_context():
        # Create admin user
        admin_user = User.query.filter_by(login_id='admin').first()
        if not admin_user:
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
            print("Admin user created successfully!")
            print("Login ID: admin")
            print("Password: admin123")
            print("Access: Management Dashboard")
        
        # Create regular test user
        test_user = User.query.filter_by(login_id='testuser').first()
        if not test_user:
            hashed_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            test = User(
                name='Test User',
                employee_id='TEST001',
                department='IT - Daily Tracking',
                login_id='testuser',
                password=hashed_pw,
                is_admin=False
            )
            db.session.add(test)
            db.session.commit()
            print("\nRegular test user created successfully!")
            print("Login ID: testuser")
            print("Password: password123")
            print("Access: Department Dashboard only")

if __name__ == '__main__':
    create_test_users()

