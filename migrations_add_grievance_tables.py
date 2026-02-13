#!/usr/bin/env python
"""
Migration script to add Grievance, GrievanceAudit, and GrievanceAttachment tables.
Run this script after updating the models.
"""

from app import create_app, db
from app.models import Grievance, GrievanceAudit, GrievanceAttachment

def run_migration():
    app = create_app()
    with app.app_context():
        try:
            # Check if tables already exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'grievance' in existing_tables:
                print("✓ Grievance table already exists.")
            else:
                print("Creating Grievance table...")
                Grievance.__table__.create(db.engine)
                print("✓ Grievance table created.")
            
            if 'grievance_audit' in existing_tables:
                print("✓ GrievanceAudit table already exists.")
            else:
                print("Creating GrievanceAudit table...")
                GrievanceAudit.__table__.create(db.engine)
                print("✓ GrievanceAudit table created.")
            
            if 'grievance_attachment' in existing_tables:
                print("✓ GrievanceAttachment table already exists.")
            else:
                print("Creating GrievanceAttachment table...")
                GrievanceAttachment.__table__.create(db.engine)
                print("✓ GrievanceAttachment table created.")
            
            print("\n✓ Migration completed successfully!")
        
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    run_migration()
