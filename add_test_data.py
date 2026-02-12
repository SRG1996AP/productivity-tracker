#!/usr/bin/env python
from app import create_app, db
from app.models import User, Department, DepartmentTracking
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Get existing users and departments
    admin_user = User.query.filter_by(login_id='admin').first()
    test_user = User.query.filter_by(login_id='testuser').first()
    departments = Department.query.all()
    
    if not admin_user or not test_user:
        print("Error: Test users not found. Run create_test_user.py first.")
        exit(1)
    
    if not departments:
        print("Error: Departments not found. Run init_db.py first.")
        exit(1)
    
    # Sample activities data
    activities = [
        {
            'user_id': admin_user.id,
            'department_id': 1,  # IT
            'description': 'Fixed critical server issue',
            'type': 'Bug Fix',
            'priority': 'High',
            'duration': 120,
            'frequency': 1,
            'days_ago': 0
        },
        {
            'user_id': admin_user.id,
            'department_id': 1,  # IT
            'description': 'Deployed new feature to production',
            'type': 'Deployment',
            'priority': 'High',
            'duration': 90,
            'frequency': 1,
            'days_ago': 1
        },
        {
            'user_id': admin_user.id,
            'department_id': 2,  # HR
            'description': 'Conducted hiring interview',
            'type': 'Recruitment',
            'priority': 'Medium',
            'duration': 60,
            'frequency': 1,
            'days_ago': 2
        },
        {
            'user_id': test_user.id,
            'department_id': 3,  # TA
            'description': 'Analyzed user testing results',
            'type': 'Analysis',
            'priority': 'Medium',
            'duration': 75,
            'frequency': 1,
            'days_ago': 0
        },
        {
            'user_id': test_user.id,
            'department_id': 3,  # TA
            'description': 'Created test cases for new module',
            'type': 'QA',
            'priority': 'High',
            'duration': 110,
            'frequency': 2,
            'days_ago': 1
        },
        {
            'user_id': test_user.id,
            'department_id': 4,  # Finance
            'description': 'Reconciled monthly expenses',
            'type': 'Financial',
            'priority': 'High',
            'duration': 150,
            'frequency': 1,
            'days_ago': 2
        },
        {
            'user_id': admin_user.id,
            'department_id': 5,  # QA
            'description': 'Regression testing on release',
            'type': 'Testing',
            'priority': 'High',
            'duration': 180,
            'frequency': 1,
            'days_ago': 0
        },
        {
            'user_id': test_user.id,
            'department_id': 6,  # Training
            'description': 'Conducted staff training session',
            'type': 'Training',
            'priority': 'Medium',
            'duration': 120,
            'frequency': 1,
            'days_ago': 1
        }
    ]
    
    # Add activity entries
    for activity in activities:
        date_logged = datetime.utcnow() - timedelta(days=activity['days_ago'])
        
        entry = DepartmentTracking(
            user_id=activity['user_id'],
            department_id=activity['department_id'],
            activity_description=activity['description'],
            ticket_request_type=activity['type'],
            priority=activity['priority'],
            duration_mins=activity['duration'],
            frequency_per_day=activity['frequency'],
            date_logged=date_logged
        )
        db.session.add(entry)
    
    db.session.commit()
    print(f"✓ Added {len(activities)} test activities to the database!")
    print(f"  - {len([a for a in activities if a['user_id'] == admin_user.id])} entries by admin")
    print(f"  - {len([a for a in activities if a['user_id'] == test_user.id])} entries by testuser")
    print("\nThe Management Dashboard will now display actual data.")
