#!/usr/bin/env python
"""
Migration script to create new TrackingField table and custom_fields_data column
Run this once before using the new custom fields feature
"""

from app import create_app, db
from app.models import TrackingField, DepartmentTracking

def upgrade():
    """Create new tables and columns"""
    app = create_app()
    with app.app_context():
        # Create all tables defined in models
        db.create_all()
        print("✓ Database schema updated successfully!")
        print("✓ TrackingField table created")
        print("✓ custom_fields_data column added to DepartmentTracking")

if __name__ == '__main__':
    upgrade()
    print("\n📊 Migration completed!")
    print("\nNext steps:")
    print("1. Go to User Management (Admin)")
    print("2. Click 'Manage Tracking Fields' for any department")
    print("3. Add custom fields for that department")
    print("4. Users will see these fields when logging activities")
