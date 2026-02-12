"""
Initialize database for Railway deployment
"""
import os
from app import create_app, db, bcrypt
from app.models import Department, User

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
            
            # Check if departments exist, if not create them
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
                print(f"✓ Created {len(departments)} departments")
            else:
                print(f"✓ Found {Department.query.count()} existing departments")
            
            # Create default admin user if no users exist
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
                print("✓ Created default admin user (login: admin, password: admin123)")
            else:
                print(f"✓ Found {User.query.count()} existing users")
            
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
