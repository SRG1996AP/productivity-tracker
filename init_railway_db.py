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
            
            # Run migrations to add new columns and tables
            print("\n→ Running database migrations...")
            from migrate_tracking_fields import upgrade
            upgrade()
            print("✓ Migrations applied successfully")
            
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
            
            # Seed default tracking fields for departments
            print("\n→ Seeding default tracking fields...")
            try:
                from app.models import TrackingField
                
                # Map department names to their field definitions
                dept_fields_map = {
                    'Finance - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'financial_area', 'label': 'Financial Area', 'type': 'text'},
                        {'name': 'ops_business_requirement', 'label': 'OPS / Business Requirement', 'type': 'text'},
                        {'name': 'transaction_type', 'label': 'Transaction Type', 'type': 'text'},
                        {'name': 'amount_if_applicable', 'label': 'Amount (if applicable)', 'type': 'number'},
                        {'name': 'approval_level', 'label': 'Approval Level', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_report', 'label': 'Output / Report', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'IT - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'system_application', 'label': 'System / Application Supported', 'type': 'text'},
                        {'name': 'ops_business_requirement', 'label': 'OPS / Business Requirement', 'type': 'text'},
                        {'name': 'ticket_request_type', 'label': 'Ticket / Request Type', 'type': 'text'},
                        {'name': 'priority', 'label': 'Priority', 'type': 'select', 'choices': ['Low', 'Medium', 'High', 'Urgent']},
                        {'name': 'sla_tat', 'label': 'SLA / TAT', 'type': 'text'},
                        {'name': 'tool_platform_used', 'label': 'Tool / Platform Used', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_report', 'label': 'Output / Report', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'HR - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'hr_process_area', 'label': 'HR Process Area', 'type': 'text'},
                        {'name': 'ops_employee_requirement', 'label': 'OPS / Employee Requirement', 'type': 'text'},
                        {'name': 'request_type', 'label': 'Request Type', 'type': 'text'},
                        {'name': 'policy_sop_reference', 'label': 'Policy / SOP Reference', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_report', 'label': 'Output / Report', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'TA - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'hiring_project_campaign', 'label': 'Hiring Project / Campaign', 'type': 'text'},
                        {'name': 'ops_client_requirement', 'label': 'OPS / Client Requirement', 'type': 'text'},
                        {'name': 'position_role', 'label': 'Position / Role', 'type': 'text'},
                        {'name': 'hiring_volume', 'label': 'Hiring Volume', 'type': 'number'},
                        {'name': 'stage_of_hiring', 'label': 'Stage of Hiring', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_report', 'label': 'Output / Report', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'QA - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'campaign_process_audited', 'label': 'Campaign / Process Audited', 'type': 'text'},
                        {'name': 'ops_client_requirement', 'label': 'OPS / Client Requirement', 'type': 'text'},
                        {'name': 'audit_type', 'label': 'Audit Type', 'type': 'text'},
                        {'name': 'sample_size', 'label': 'Sample Size', 'type': 'number'},
                        {'name': 'qa_standard_kpi', 'label': 'QA Standard / KPI', 'type': 'text'},
                        {'name': 'qa_tool_used', 'label': 'QA Tool Used', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_scorecard', 'label': 'Output / Scorecard', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'Training - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'training_program_batch', 'label': 'Training Program / Batch', 'type': 'text'},
                        {'name': 'ops_client_requirement', 'label': 'OPS / Client Requirement', 'type': 'text'},
                        {'name': 'training_type', 'label': 'Training Type', 'type': 'text'},
                        {'name': 'no_of_trainees', 'label': 'No. of Trainees', 'type': 'number'},
                        {'name': 'training_mode', 'label': 'Training Mode', 'type': 'text'},
                        {'name': 'tool_lms_used', 'label': 'Tool / LMS Used', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_report', 'label': 'Output / Report', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'RTA - Daily Tracking': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'supporting_campaign_project', 'label': 'Supporting Campaign/Project', 'type': 'text'},
                        {'name': 'client_ops_requirement', 'label': 'Client/OPS Requirement', 'type': 'text'},
                        {'name': 'report_name', 'label': 'Report Name', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'tool_crm_telephony_used', 'label': 'Tool/CRM/Telephony Used', 'type': 'text'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                    'Operations Leaders - Daily': [
                        {'name': 'entry_no', 'label': 'No', 'type': 'number'},
                        {'name': 'campaign_account', 'label': 'Campaign / Account', 'type': 'text'},
                        {'name': 'client_ops_requirement', 'label': 'Client / OPS Requirement', 'type': 'text'},
                        {'name': 'activity_category', 'label': 'Activity Category', 'type': 'text'},
                        {'name': 'kpi_sla_impacted', 'label': 'KPI / SLA Impacted', 'type': 'text'},
                        {'name': 'duration_mins', 'label': 'Duration (mins)', 'type': 'number'},
                        {'name': 'output_evidence', 'label': 'Output / Evidence', 'type': 'textarea'},
                        {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea'},
                    ],
                }
                
                departments_configured = 0
                for dept in Department.query.all():
                    if dept.name not in dept_fields_map:
                        continue
                    
                    existing_fields = TrackingField.query.filter_by(department_id=dept.id).count()
                    if existing_fields > 0:
                        print(f"  ⊙ [{dept.name}] Has {existing_fields} fields, skipping")
                        continue
                    
                    fields_to_add = dept_fields_map[dept.name]
                    for idx, field_data in enumerate(fields_to_add, 1):
                        field = TrackingField(
                            department_id=dept.id,
                            field_name=field_data['name'],
                            field_label=field_data.get('label', field_data['name']),
                            field_type=field_data.get('type', 'text'),
                            choices=field_data.get('choices', []),
                            order=idx
                        )
                        db.session.add(field)
                    
                    db.session.commit()
                    departments_configured += 1
                    print(f"  ✓ [{dept.name}] Added {len(fields_to_add)} fields")
                
                print(f"✓ Seeded {departments_configured} departments")
            except Exception as e:
                print(f"✗ Seeding error: {e}")
                import traceback
                traceback.print_exc()
            
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
