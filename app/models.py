from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    login_id = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    department_entries = db.relationship('DepartmentTracking', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    tracking_entries = db.relationship('DepartmentTracking', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'

class DepartmentTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    activity_description = db.Column(db.Text, nullable=False)
    ticket_request_type = db.Column(db.String(200))
    system_application = db.Column(db.String(200))
    priority = db.Column(db.String(50))
    sla_tat = db.Column(db.String(100))
    tool_platform_used = db.Column(db.String(200))
    duration_mins = db.Column(db.Integer)
    frequency_per_day = db.Column(db.Integer)
    date_logged = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DepartmentTracking {self.activity_description}>'
