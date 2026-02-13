# 🎯 Grievance System - Getting Started Guide

## What Was Built

A complete **Employee Grievance Management Portal** with:
- ✅ Employee submission form (public, no login required)
- ✅ HR admin dashboard with analytics
- ✅ AI-powered categorization, priority detection, sentiment analysis
- ✅ Automatic keyword flagging and escalation
- ✅ Complete audit trail and status tracking
- ✅ REST API for all functions
- ✅ Database with 3 tables (Grievance, GrievanceAudit, GrievanceAttachment)

## 5-Minute Quick Start

### 1. Start the Flask App
```powershell
cd c:\Users\edwin\Desktop\productivity_tracker
.\venv\Scripts\Activate.ps1
python run.py
```

The app starts on `http://localhost:5000`

### 2. Access the Employee Form
Open in browser: **`http://localhost:5000/submit-grievance`**

Fill in the form and submit a test grievance. You'll get a Case ID like: `GR-20260213-248B`

### 3. Access the HR Dashboard
Open in browser: **`http://localhost:5000/grievance-dashboard`**

(Must be logged in as admin user to access)

See all submitted grievances with AI analysis, filters, and charts.

### 4. Run Tests
```powershell
python test_grievance_api.py
```

This tests all 7 API scenarios and should show all ✓ passed.

## 📋 Files Related to Grievance System

### New Files Created
- `app/templates/submit_grievance.html` - Employee submission form
- `app/templates/grievance_dashboard.html` - HR admin dashboard
- `migrations_add_grievance_tables.py` - Database migration (already run)
- `test_grievance_api.py` - Comprehensive test suite
- `GRIEVANCE_SYSTEM_README.md` - Full system documentation
- `IMPLEMENTATION_SUMMARY.md` - What was implemented

### Modified Files
- `app/models.py` - Added Grievance, GrievanceAudit, GrievanceAttachment models
- `app/routes.py` - Added 7 new API endpoints and 2 web routes

### Database Tables (Created)
- `grievance` - Main grievance records
- `grievance_audit` - Status change audit trail
- `grievance_attachment` - File attachments (for future use)

## 🌐 All Endpoints

### For Employees (No Auth)
- `GET /submit-grievance` - Grievance submission form page
- `POST /api/grievances` - Submit grievance via API

### For HR Admins (Login Required)
- `GET /grievance-dashboard` - Dashboard with analytics
- `GET /api/grievances` - List all grievances (with filters)
- `GET /api/grievances/<case_id>` - View grievance details
- `PUT /api/grievances/<case_id>/status` - Update status and add remarks
- `GET /api/grievances/dashboard/metrics` - Get analytics data

## 🤖 AI Features in Action

When someone submits a grievance like:
> "My supervisor has been harassing me and I'm thinking about quitting"

The system automatically:
1. **Detects keywords**: harassment, resign (critical)
2. **Categorizes**: Workplace Harassment
3. **Assigns priority**: High
4. **Calculates sentiment**: -0.95 (very negative)
5. **Auto-escalates**: Sends to Senior HR due to keywords
6. **Audits**: Creates entry in audit trail

## 📊 Dashboard Features

The HR dashboard shows:
- **5 Metric Cards**: Total, Open, Resolved, High-Priority, Escalated
- **Filter Panel**: By Case ID, Status, Priority, Department
- **Grievance Table**: All cases with Category, Priority, Status
- **4 Charts**: 
  - Category distribution
  - Priority breakdown
  - Status breakdown
  - Department distribution
- **Actions**: View details or update status

## 🔄 Case Workflow

```
Employee Submits Grievance
         ↓
System Validates & AI Analysis
         ↓
Case Created with ID (Open status)
         ↓
HR Review (Under Review status)
         ↓
Investigation (if needed)
         ↓
Resolution (Resolved status)
         ↓
Documentation Closed (Closed status)

↔ Escalation (if critical keywords or manual escalation)
```

## 💡 Example: Try This Now

### Step 1: Submit a Test Grievance
1. Go to `http://localhost:5000/submit-grievance`
2. Fill in:
   - Name: Your Name
   - Employee ID: EMP123
   - Department: Sales Department
   - Contact: 9876543210
   - Grievance: "I have concerns about my workload and work-life balance"
3. Click Submit
4. **Save the Case ID** (e.g., GR-20260213-ABC1)

### Step 2: View in Dashboard
1. Go to `http://localhost:5000/grievance-dashboard` (as admin)
2. Search for your case ID in the search box
3. Click "View" to see all details and audit trail
4. Click "Update" to change status and add remarks

### Step 3: Check AI Analysis
In the View details popup, notice:
- Random case gets "Medium" priority (depends on keywords)
- Category detected as "Workload Concern"
- Sentiment score (negative if mentions concerns/balance)

## 🚀 Test All Keyword Escalations

Try these and observe auto-escalation:
- "I've been harassed by my manager"
- "Discriminatory treatment"
- "Illegal activity occurring"
- "Harassment and bullying"
- "I'm going to resign due to this"

All will be marked as escalated to Senior HR!

## 📚 Full Documentation

For detailed information:
- **GRIEVANCE_SYSTEM_README.md** - Complete system spec
  - Database schema
  - All API endpoints with examples
  - Deployment instructions
  - Configuration options
  
- **IMPLEMENTATION_SUMMARY.md** - What was built
  - Checklist of all components
  - Test results
  - Capabilities
  - Next steps

## 🐛 Troubleshooting

### Port 5000 in use?
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Database issues?
```powershell
# The migration was already run, but if needed:
python migrations_add_grievance_tables.py
```

### Can't see grievances in dashboard?
1. Make sure you're logged in as admin
2. Submit a test grievance first via `/submit-grievance`
3. Refresh the dashboard page
4. Check browser console for errors

### Tests not running?
```powershell
pip install requests  # If not already installed
python test_grievance_api.py
```

## ✨ Key Highlights

✅ **Fully functional** - All features implemented and working  
✅ **Production ready** - Security, validation, error handling included  
✅ **Well documented** - Comprehensive README and implementation guide  
✅ **Extensively tested** - 7 test scenarios all passing  
✅ **AI-powered** - Automatic categorization and analysis  
✅ **Audit compliant** - Full audit trail for every action  
✅ **User friendly** - Professional UI for both employees and HR  

## 🎉 What's Next?

1. **Explore the system** - Submit several test grievances with different content
2. **Review the analytics** - See how the dashboard charts update
3. **Read the docs** - See GRIEVANCE_SYSTEM_README.md for in-depth info
4. **Run the tests** - Verify everything works: `python test_grievance_api.py`
5. **Try the API** - Test endpoints using curl or Postman
6. **Deploy** - Follow deployment instructions in GRIEVANCE_SYSTEM_README.md

---

**Status**: ✅ Complete & Ready to Use  
**System Version**: 1.0.0  
**Last Updated**: February 13, 2026
