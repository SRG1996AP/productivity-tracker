# Employee Grievance Management Portal

## System Overview

The Employee Grievance Management Portal is a secure, web-based application that allows employees to formally submit workplace concerns, complaints, or grievances directly to the Human Resources (HR) department. The system ensures confidentiality, proper documentation, structured case tracking, and timely resolution of employee issues using AI-assisted categorization and prioritization.

## Key Features

### 🔐 Employee Features
- **Confidential Submission**: Submit grievances with full confidentiality
- **Anonymous Option**: Option to submit grievances anonymously
- **Case ID Generation**: Automatic unique case ID (format: GR-YYYYMMDD-XXXX)
- **Responsive Form**: User-friendly web form with real-time validation
- **Acknowledgment**: Instant confirmation with case ID for reference

### 🎯 HR Admin Features
- **Comprehensive Dashboard**: View all grievances with metrics and analytics
- **Advanced Filtering**: Filter by date, department, status, priority
- **Status Management**: Update case status with audit trail
- **AI Analysis**: AI-powered categorization, priority detection, and sentiment analysis
- **Analytics**: Charts showing grievance distribution by category, priority, status, and department
- **Export Capability**: Export grievance data for reporting
- **Audit Trail**: Complete history of all status changes with timestamps

### 🤖 AI Features
- **Automatic Categorization**: Classify grievances into categories like:
  - Workplace Harassment
  - Payroll / Salary Issue
  - Supervisor Misconduct
  - Discrimination
  - Workload Concern
  - Policy Violation
  - IT / System Issue
  - Others

- **Priority Detection**: Automatic priority assignment (High, Medium, Low)
  - High: Urgent, legal risk, harassment keywords
  - Medium: Time-sensitive concerns
  - Low: Standard grievances

- **Sentiment Analysis**: Detect emotional distress and urgency
  - Sentiment score range: -1.0 to 1.0
  - Identifies concerning language patterns

- **Keyword Flagging**: Automatic flagging and escalation for sensitive keywords:
  - Harassment, bullying, threat, illegal, discrimination, resign, suicide
  - Auto-escalates to Senior HR when critical keywords detected

## Project Structure

```
app/
  __init__.py           # Flask app initialization
  models.py             # SQLAlchemy models for Grievance, GrievanceAudit, GrievanceAttachment
  routes.py             # API endpoints and web routes
  forms.py              # WTForms for validation
  templates/            # HTML templates
    base.html
    submit_grievance.html
    grievance_dashboard.html
  static/               # CSS, JavaScript, assets
    style.css
    department.js

migrations_add_grievance_tables.py   # Database migration script
test_grievance_api.py                # Test suite for API endpoints
run.py                               # Flask app entry point
requirements.txt                     # Python dependencies
README.md                            # This file
```

## Database Schema

### Table: `grievance`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique database ID |
| case_id | VARCHAR(50) UNIQUE | Human-readable case ID (GR-YYYYMMDD-XXXX) |
| employee_name | VARCHAR(150) | Employee name or "Anonymous" |
| employee_id | VARCHAR(50) | Employee ID or "ANONYMOUS" |
| campaign | VARCHAR(100) | Department/Team |
| contact_number | VARCHAR(20) | Contact phone number |
| grievance_text | TEXT | Complete grievance description |
| is_anonymous | BOOLEAN | Anonymous submission flag |
| ai_category | VARCHAR(100) | AI-assigned category |
| ai_priority | VARCHAR(20) | AI-assigned priority (High, Medium, Low) |
| ai_sentiment_score | FLOAT | Sentiment score (-1.0 to 1.0) |
| ai_keywords_flagged | TEXT | JSON array of flagged keywords |
| status | VARCHAR(50) | Current status |
| hr_remarks | TEXT | HR comments and notes |
| escalated_to_senior_hr | BOOLEAN | Escalation flag |
| escalation_reason | VARCHAR(200) | Reason for escalation |
| submitted_at | TIMESTAMP | Submission timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Table: `grievance_audit`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique audit entry ID |
| grievance_id | INTEGER FK | Reference to grievance |
| changed_by | VARCHAR(150) | HR officer or "System" |
| from_status | VARCHAR(50) | Previous status |
| to_status | VARCHAR(50) | New status |
| remarks | TEXT | Status change notes |
| changed_at | TIMESTAMP | Change timestamp |

### Table: `grievance_attachment`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique attachment ID |
| grievance_id | INTEGER FK | Reference to grievance |
| file_path | VARCHAR(500) | Server file path |
| original_filename | VARCHAR(255) | Original filename |
| file_size | INTEGER | File size in bytes |
| mime_type | VARCHAR(100) | MIME type |
| uploaded_by | VARCHAR(150) | Uploader name |
| uploaded_at | TIMESTAMP | Upload timestamp |
| sha256_hash | VARCHAR(64) | File integrity hash |

## API Endpoints

### Public Endpoints (No Authentication)

#### POST `/api/grievances`
Submit a new grievance.

**Request:**
```json
{
  "employee_name": "John Smith",
  "employee_id": "EMP001",
  "campaign": "Sales Department",
  "contact_number": "9876543210",
  "grievance_text": "Detailed description of the grievance...",
  "is_anonymous": false
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Your grievance has been successfully submitted. Case ID: GR-20260213-248B",
  "case_id": "GR-20260213-248B",
  "status": "Open"
}
```

### Protected Endpoints (HR Admin Only)

#### GET `/api/grievances`
Retrieve grievances list with filters.

**Query Parameters:**
- `date_from`: YYYY-MM-DD
- `date_to`: YYYY-MM-DD
- `campaign`: Department name
- `status`: Open, Under Review, Investigation, Escalated, Resolved, Closed
- `priority`: High, Medium, Low
- `search`: Case ID or Employee ID
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20)

**Response:**
```json
{
  "success": true,
  "grievances": [
    {
      "id": 1,
      "case_id": "GR-20260213-248B",
      "employee_name": "John Smith",
      "employee_id": "EMP001",
      "campaign": "Sales Department",
      "ai_category": "Workload Concern",
      "ai_priority": "Medium",
      "status": "Open",
      "submitted_at": "2026-02-13T10:30:00",
      "is_escalated": false
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

#### GET `/api/grievances/<case_id>`
Retrieve detailed information for a specific grievance.

**Response:**
```json
{
  "success": true,
  "grievance": {
    "id": 1,
    "case_id": "GR-20260213-248B",
    "employee_name": "John Smith",
    "grievance_text": "...",
    "ai_category": "Workload Concern",
    "ai_priority": "Medium",
    "ai_sentiment_score": -0.45,
    "ai_keywords_flagged": [],
    "status": "Open",
    "hr_remarks": null,
    "escalated_to_senior_hr": false,
    "audit_trail": [
      {
        "changed_at": "2026-02-13T10:30:00",
        "changed_by": "System",
        "from_status": null,
        "to_status": "Open",
        "remarks": "Grievance submitted - AI analysis completed"
      }
    ]
  }
}
```

#### PUT `/api/grievances/<case_id>/status`
Update grievance status.

**Request:**
```json
{
  "status": "Under Review",
  "remarks": "Assigned to investigation team"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Grievance GR-20260213-248B status updated to Under Review",
  "status": "Under Review"
}
```

#### GET `/api/grievances/dashboard/metrics`
Retrieve dashboard metrics and analytics.

**Response:**
```json
{
  "success": true,
  "metrics": {
    "total_grievances": 125,
    "open_cases": 45,
    "resolved_cases": 60,
    "high_priority_cases": 12,
    "escalated_cases": 8,
    "monthly_totals": [...],
    "status_breakdown": {...},
    "priority_breakdown": {...},
    "category_breakdown": {...},
    "campaign_breakdown": {...}
  }
}
```

## Web Pages

### `/submit-grievance`
Public grievance submission form. Employees can:
- Fill in all required fields
- Submit grievances anonymously
- Get instant confirmation with case ID
- See validation feedback in real-time

### `/grievance-dashboard` (HR Admin Only)
HR management dashboard with:
- Live metrics cards
- Advanced filtering panel
- Grievances table with sorting
- Action buttons (View, Update Status)
- Analytics charts (category, priority, status, department)
- Pagination support

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip/virtual environment

### Steps

1. **Clone repository and navigate to project directory**
   ```bash
   cd c:\Users\edwin\Desktop\productivity_tracker
   ```

2. **Activate virtual environment**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install requests  # For testing
   ```

4. **Run database migration**
   ```bash
   python migrations_add_grievance_tables.py
   ```

5. **Configure environment variables** (optional)
   ```bash
   # Create .env file
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:password@localhost/grievance_db
   FLASK_ENV=development
   ```

6. **Start the Flask application**
   ```bash
   python run.py
   ```

   The application will run on `http://localhost:5000`

## Testing

### Run API Tests
```bash
python test_grievance_api.py
```

This tests:
- ✓ Successful grievance submission
- ✓ Anonymous submission
- ✓ High-priority keyword escalation
- ✓ AI category detection
- ✓ Missing fields validation
- ✓ Contact number validation
- ✓ Grievance text length validation

## Case Status Workflow

```
Open (Initial Submission)
  ↓
Under Review (HR reviews)
  ↓
Investigation in Progress (If needed)
  ↓
Resolved (Issue addressed)
  ↓
Closed (Final documentation)

Alternative: Escalated (If critical keywords detected or manually escalated)
```

## Security Features

1. **Authentication**: Role-based access control (RBAC)
   - Employees: Public submission endpoint
   - HR Admins: Protected dashboard and management endpoints

2. **Data Protection**:
   - HTTPS support (enable in production)
   - Database encryption ready
   - Secure password hashing (Bcrypt)
   - CSRF protection enabled

3. **Privacy**:
   - Anonymous submission option
   - Name redaction support
   - Confidentiality notices in UI

4. **Audit Trail**:
   - Immutable status change history
   - Timestamp tracking
   - HR officer attribution
   - Complete remarks logging

5. **Validation**:
   - Input sanitization
   - Contact number format validation
   - Required field enforcement
   - Minimum text length validation

## Configuration

### Database Configuration
Update in `app/__init__.py`:
```python
# SQLite (development)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# PostgreSQL (production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:5432/grievance_db'
```

### AI Configuration
To integrate with OpenAI API, modify `analyze_grievance_with_ai()` in `routes.py`:
```python
import openai

def analyze_grievance_with_ai(grievance_text):
    # Call OpenAI API for better categorization
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "You are an HR assistant analyzing employee grievances...",
            "role": "user",
            "content": f"Analyze this grievance: {grievance_text}"
        }]
    )
    # Parse response and return categorization
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:create_app()"]
```

### Heroku Deployment
```bash
git push heroku main
heroku run python migrations_add_grievance_tables.py
```

### Requirements for Production
- SSL/HTTPS certificate
- Database backup strategy
- Monitoring and logging (ELK stack)
- Rate limiting (Redis)
- Email notifications (SMTP)
- File virus scanning for attachments

## Future Enhancements

1. **Email Notifications**: Auto-notify employees on status changes
2. **File Uploads**: Support for document attachments with virus scanning
3. **Advanced AI**: Integration with ML models for better categorization
4. **Scheduled Reports**: Automated monthly/weekly reports to management
5. **Multi-language Support**: Localization for diverse workforce
6. **Mobile App**: React Native mobile application
7. **Workflow Automation**: Automated routing to specific teams
8. **Survey Integration**: Post-resolution satisfaction surveys
9. **Predictive Analytics**: Identify trends and proactive interventions
10. **SSO Integration**: Active Directory / Azure AD login

## Support & Maintenance

### Common Issues

**Issue**: Database tables don't exist
**Solution**: 
```bash
python migrations_add_grievance_tables.py
```

**Issue**: Port 5000 already in use
**Solution**: 
```bash
netstat -ano | findstr :5000  # Find PID
taskkill /PID <PID> /F        # Kill process
```

**Issue**: CORS errors when testing API
**Solution**: Add Flask-CORS to `app/__init__.py`:
```python
from flask_cors import CORS
CORS(app)
```

## License

This application is proprietary and confidential. All rights reserved.

## Contact

For support or questions, contact HR Department.

---

**Version**: 1.0.0  
**Last Updated**: February 13, 2026  
**Status**: Production Ready
