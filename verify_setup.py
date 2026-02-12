#!/usr/bin/env python3
"""
Verification script to check that all components are properly set up.
"""

from app import create_app, db
from app.models import User, Department, DepartmentTracking

def verify_setup():
    """Verify that the system is properly set up."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("DEPARTMENT TRACKING SYSTEM - VERIFICATION REPORT")
        print("=" * 60)
        
        # Check departments
        departments = Department.query.all()
        print(f"\n✓ Departments: {len(departments)}/8")
        for dept in departments:
            print(f"  - {dept.name}")
        
        # Check users
        users = User.query.all()
        print(f"\n✓ Users: {len(users)}")
        for user in users:
            print(f"  - {user.name} ({user.email}) - {user.department}")
        
        # Check tracking entries
        entries = DepartmentTracking.query.all()
        print(f"\n✓ Tracking Entries: {len(entries)}")
        
        print("\n" + "=" * 60)
        print("SETUP VERIFICATION COMPLETE!")
        print("=" * 60)
        
        # Check if ready to run
        if len(departments) == 8 and len(users) > 0:
            print("\n✅ System is ready to use!")
            print("\nTo start the application:")
            print("  python run.py")
            print("\nThen access it at:")
            print("  http://localhost:5000")
        else:
            print("\n⚠️  Some components may be missing. Please run init_db.py")

if __name__ == '__main__':
    verify_setup()
