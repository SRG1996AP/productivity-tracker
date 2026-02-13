#!/usr/bin/env python3
"""
Script to initialize the database with departments from the Excel file.
"""

from app import create_app, db
from app.models import Department, TrackingField
from default_tracking_fields import get_default_tracking_fields_by_key, match_department_key

# Department data from the Excel file
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
    """Initialize database with departments."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if departments already exist
        existing_depts = Department.query.all()
        if existing_depts:
            print(f"Database already has {len(existing_depts)} departments. Skipping initialization.")
            return
        
        defaults = get_default_tracking_fields_by_key()

        # Add departments
        for dept_data in DEPARTMENTS:
            dept = Department(**dept_data)
            db.session.add(dept)
            db.session.flush()

            key = match_department_key(dept.name)
            if key:
                fields = defaults.get(key, [])
                for order_index, field_def in enumerate(fields, start=1):
                    field = TrackingField(
                        department_id=dept.id,
                        field_name=field_def["name"],
                        field_label=field_def["label"],
                        field_type=field_def["type"],
                        is_required=False,
                        order=order_index,
                    )
                    if field_def.get("choices"):
                        field.set_choices(field_def["choices"])
                    db.session.add(field)

            print(f"Added department: {dept.name}")
        
        db.session.commit()
        print("\nDatabase initialized successfully!")

if __name__ == '__main__':
    init_db()
