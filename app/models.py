from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json

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
    tracking_fields = db.relationship('TrackingField', backref='department', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Department {self.name}>'

class TrackingField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    field_name = db.Column(db.String(200), nullable=False)
    field_type = db.Column(db.String(50), nullable=False, default='text')  # text, textarea, select, number, date
    field_label = db.Column(db.String(200), nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    choices = db.Column(db.Text)  # JSON array of choices for select fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TrackingField {self.field_name}>'
    
    def get_choices(self):
        """Parse choices JSON"""
        if self.choices:
            return json.loads(self.choices)
        return []
    
    def set_choices(self, choices_list):
        """Store choices as JSON"""
        self.choices = json.dumps(choices_list) if choices_list else None

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
    status = db.Column(db.String(50), default='Completed')
    # New field to store custom field values as JSON
    custom_fields_data = db.Column(db.Text)  # JSON object with custom field values
    date_logged = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DepartmentTracking {self.activity_description}>'
    
    def get_custom_fields_data(self):
        """Parse custom fields data JSON"""
        if self.custom_fields_data:
            return json.loads(self.custom_fields_data)
        return {}
    
    def set_custom_fields_data(self, data_dict):
        """Store custom fields data as JSON"""
        self.custom_fields_data = json.dumps(data_dict) if data_dict else None

class Grievance(db.Model):
    """Model for employee grievances"""
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    employee_name = db.Column(db.String(150), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False, index=True)
    campaign = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    grievance_text = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    
    # AI-generated fields
    ai_category = db.Column(db.String(100))  # Workplace Harassment, Payroll, etc.
    ai_priority = db.Column(db.String(20))  # High, Medium, Low
    ai_sentiment_score = db.Column(db.Float)  # -1.0 to 1.0
    ai_keywords_flagged = db.Column(db.Text)  # JSON array of flagged keywords
    
    # Case management
    status = db.Column(db.String(50), default='Open', nullable=False, index=True)  # Open, Under Review, Investigation, Escalated, Resolved, Closed
    hr_remarks = db.Column(db.Text)
    escalated_to_senior_hr = db.Column(db.Boolean, default=False)
    escalation_reason = db.Column(db.String(200))
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    audit_entries = db.relationship('GrievanceAudit', backref='grievance', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('GrievanceAttachment', backref='grievance', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Grievance {self.case_id}>'
    
    def get_flagged_keywords(self):
        """Parse flagged keywords JSON"""
        if self.ai_keywords_flagged:
            return json.loads(self.ai_keywords_flagged)
        return []
    
    def set_flagged_keywords(self, keywords_list):
        """Store flagged keywords as JSON"""
        self.ai_keywords_flagged = json.dumps(keywords_list) if keywords_list else None


class GrievanceAudit(db.Model):
    """Audit trail for grievance status changes"""
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey('grievance.id'), nullable=False, index=True)
    changed_by = db.Column(db.String(150), nullable=False)  # HR officer name or system
    from_status = db.Column(db.String(50))
    to_status = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<GrievanceAudit {self.grievance_id} {self.to_status}>'


class GrievanceAttachment(db.Model):
    """Model for file attachments to grievances"""
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey('grievance.id'), nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    mime_type = db.Column(db.String(100))
    uploaded_by = db.Column(db.String(150), default='employee')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sha256_hash = db.Column(db.String(64))  # for integrity verification
    
    def __repr__(self):
        return f'<GrievanceAttachment {self.original_filename}>'