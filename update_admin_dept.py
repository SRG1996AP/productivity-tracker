#!/usr/bin/env python3
"""
Script to update admin user's department to Management
"""

from app import create_app, db
from app.models import User, Department

def update_admin_department():
    """Update all admin users to Management department."""
    app = create_app()
    
    with app.app_context():
        # Check if Management department exists
        mgmt_dept = Department.query.filter_by(name='Management').first()
        if not mgmt_dept:
            print("Error: Management department not found in database.")
            print("Please run init_db.py first to create the Management department.")
            return
        
        # Find all admin users
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("No admin users found in database.")
            return
        
        # Update each admin user's department
        updated_count = 0
        for admin in admin_users:
            if admin.department != 'Management':
                old_dept = admin.department
                admin.department = 'Management'
                print(f"Updated user '{admin.name}' (ID: {admin.id}): {old_dept} -> Management")
                updated_count += 1
            else:
                print(f"User '{admin.name}' (ID: {admin.id}) already in Management department")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully updated {updated_count} admin user(s) to Management department.")
        else:
            print("\n✓ All admin users already have Management department.")

if __name__ == '__main__':
    update_admin_department()
