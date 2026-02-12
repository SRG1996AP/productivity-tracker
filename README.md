# Department Daily Operational Tracking System

A Flask-based web application for tracking daily operational activities across 8 different departments.

## 📋 Overview

This tracking system allows users to log and manage daily operational activities for the following departments:

1. **IT - Daily Tracking** - Information Technology operations
2. **HR - Daily Tracking** - Human Resources processes  
3. **TA - Daily Tracking** - Talent Acquisition (hiring)
4. **Finance - Daily Tracking** - Financial operations
5. **QA - Daily Tracking** - Quality Assurance
6. **Training - Daily Tracking** - Employee training programs
7. **RTA - Daily Tracking** - Recruitment operations
8. **Operations Leaders - Daily** - Leadership operations

## 🚀 Setup Instructions

### Prerequisites
- Python 3.x
- Virtual Environment (venv)

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd c:\Users\edwin\Desktop\productivity_tracker
   ```

2. **Activate virtual environment:**
   ```bash
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database with departments:**
   ```bash
   python init_db.py
   ```

5. **Create test user (optional):**
   ```bash
   python create_test_user.py
   ```
   - Email: `test@example.com`
   - Password: `password123`

6. **Run the application:**
   ```bash
   python run.py
   ```

7. **Access the application:**
   - Navigate to `http://localhost:5000` in your web browser
   - Register a new account or login with test credentials

## 📊 Features

### User Management
- User registration with email, employee ID, and department
- Secure login with bcrypt password hashing
- User session management

### Department Tracking
- **Log Activities** - Record daily operational activities with detailed information:
  - Activity description
  - Ticket/Request type
  - System/Application used
  - Priority level (Low, Medium, High, Urgent)
  - SLA/TAT
  - Tool/Platform used
  - Duration (in minutes)
  - Frequency per day

### Tracking Dashboard
- View all departments
- See today's logged activities
- Track statistics:
  - Total logged activities
  - Total duration spent
  - Number of today's entries
- Department-specific statistics

### Department Details View
- View all activities for a specific department
- Filter by department
- See detailed activity information
- Track metrics:
  - Total activities
  - Total duration
  - Average duration per activity

## 📁 Project Structure

```
productivity_tracker/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models (User, Department, DepartmentTracking)
│   ├── routes.py                # Application routes
│   ├── forms.py                 # WTForms for user input
│   ├── static/
│   │   ├── style.css           # CSS styles
│   │   ├── department.js       # JavaScript utilities
│   │   └── Chart.js            # Chart.js library
│   └── templates/
│       ├── base.html           # Base template
│       ├── login.html          # Login page
│       ├── register.html       # Registration page
│       ├── dashboard.html      # Main dashboard
│       ├── department_tracking.html    # Department tracking dashboard
│       ├── add_department_entry.html   # Add activity form
│       └── department_details.html     # Department details view
├── instance/                    # Instance folder (ignored in git)
├── migration/                   # Database migrations folder
├── init_db.py                  # Database initialization script
├── create_test_user.py         # Test user creation script
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Database Schema

### User Model
- `id` - Primary key
- `name` - User's full name
- `employee_id` - Unique employee ID
- `department` - Department name
- `email` - Unique email address
- `password` - Hashed password
- `department_entries` - Relationship to DepartmentTracking

### Department Model
- `id` - Primary key
- `name` - Department name (unique)
- `description` - Department description
- `tracking_entries` - Relationship to DepartmentTracking

### DepartmentTracking Model
- `id` - Primary key
- `user_id` - Foreign key to User
- `department_id` - Foreign key to Department
- `activity_description` - Text description of activity
- `ticket_request_type` - Type of ticket/request
- `system_application` - System/app involved
- `priority` - Priority level
- `sla_tat` - SLA/TAT information
- `tool_platform_used` - Tool/platform used
- `duration_mins` - Duration in minutes
- `frequency_per_day` - Frequency per day
- `date_logged` - Timestamp of entry

## 🌐 Application Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home (redirects to login or dashboard) |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | User logout |
| `/dashboard` | GET | Main dashboard |
| `/department-tracking` | GET | Department tracking dashboard |
| `/add-department-entry` | GET, POST | Add new activity entry |
| `/department/<id>` | GET | View department details |

## 📝 Usage Guide

### Registering a New User
1. Click on "Register" link on the login page
2. Enter your details:
   - Full name
   - Employee ID
   - Department
   - Email address
   - Password (minimum 6 characters)
3. Click "Register" button
4. Login with your credentials

### Logging an Activity
1. Navigate to "Department Tracking" from the dashboard
2. Click "+ Log New Activity"
3. Select department from dropdown
4. Fill in activity details:
   - Activity description (required)
   - Ticket/Request type (optional)
   - Priority level (optional)
   - System/Application (optional)
   - Tool/Platform (optional)
   - Duration (optional)
   - Frequency (optional)
   - SLA/TAT (optional)
5. Click "Log Activity"

### Viewing Department Activities
1. Go to Department Tracking page
2. Click on a department card to view its details
3. See all activities logged for that department
4. View statistics for that department

## 🔐 Security Features

- **Password Hashing** - Uses bcrypt for secure password storage
- **Authentication** - Flask-Login for session management
- **CSRF Protection** - Flask-WTF for form protection
- **Database Validation** - Input validation on all forms

## 📦 Dependencies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM for database
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling with CSRF protection
- **Flask-Bcrypt** - Password hashing
- **pandas** - Data manipulation
- **openpyxl** - Excel file support

## 🚨 Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can specify a different port:
```bash
python run.py --port 5001
```

### Database Issues
To reset the database, delete `instance/site.db` and run:
```bash
python init_db.py
python create_test_user.py
```

### Missing Dependencies
Install all dependencies:
```bash
pip install -r requirements.txt
```

## 📈 Future Enhancements

- Dashboard analytics and charts
- Export tracking data to Excel
- Department performance metrics
- Team-wide tracking views
- Email notifications for high-priority items
- Advanced filtering and search
- Multi-user department tracking
- Automated reporting

## 📧 Support

For issues or questions, please contact the development team.

## 📄 License

This project is internal use only.

---

**Last Updated:** February 11, 2026
