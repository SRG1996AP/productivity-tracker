# Custom Tracking Fields - Setup Guide

## Quick Setup (2 minutes)

### For Admins ONLY

1. **Login** with your admin account
2. Go to **Department Tracking** (or dashboard)
3. Click **⚙️ Configure Tracking Fields** button
4. Click **"Add New Field"** button
5. Fill in the field details:
   - **Field Label**: What users will see (e.g., "Issue Type")
   - **Field Name**: Internal code in lowercase (e.g., "issue_type")
   - **Field Type**: Choose one:
     - `text` - Single line input
     - `textarea` - Multiple lines
     - `number` - Numbers only
     - `date` - Date picker
     - `select` - Dropdown menu
   - **Required**: Check if users must fill it
6. Click **"Save Field"**

---

## What Users Will See

When a user logs an activity, they'll see:

```
Activity Description              [Textarea field]

Custom Fields for [Department]
├─ Field 1                        [Input...]
├─ Field 2                        [Input...]
└─ Field 3                        [Input...]

[Log Activity]  [Cancel]
```

---

## Example: Setting Up HR Department

### Field 1: Activity Type
- **Label**: Activity Type
- **Name**: activity_type
- **Type**: select
- **Required**: YES ✓

### Field 2: Hours Spent
- **Label**: Hours Spent
- **Name**: hours_spent
- **Type**: number
- **Required**: NO

### Field 3: Notes
- **Label**: Additional Notes
- **Name**: notes
- **Type**: textarea
- **Required**: NO

---

## Important: Using Proper Field Names

**Field names must be:**
- Lowercase letters and numbers only
- No spaces or special characters
- Use underscores instead of spaces: `ticket_number`, `issue_type`

**Good examples:**
```
activity_type
hours_spent
ticket_number
system_used
priority_level
issue_category
```

**Bad examples:**
```
Activity Type          ❌ (has spaces)
Issue-Type            ❌ (has hyphen)
IssueType             ✓ Actually ok but use: issue_type
```

---

## Field Types Explained

| Type | Usage | Example |
|------|-------|---------|
| **text** | Single line input | System name, User name, Ticket ID |
| **textarea** | Multi-line text | Detailed description, Notes, Comments |
| **number** | Numbers only | Hours, Minutes, Count, Quantity |
| **date** | Date picker | Due date, Completion date, Deadline |
| **select** | Dropdown list | Status, Priority, Category, Type |

---

## Quick Access Paths

### From Department Tracking Page (Easiest)
1. Login as admin
2. You'll see: **⚙️ Configure Tracking Fields** button
3. Click it → Field management page opens

### From User Management
1. Login as admin
2. Go to **User Management**
3. Find your department
4. Click **⚙️ Manage Tracking Fields**

### From Management Dashboard
1. Login as admin
2. Click **👥 Manage Users**
3. Scroll to Departments section
4. Click **⚙️ Manage Tracking Fields** on the department card

---

## Troubleshooting

**Q: Users don't see my custom fields**
- A: Fields configured? Check the ⚙️ Configure Tracking Fields page
- Make sure at least one field is saved
- Users will see them in the Log Activity form

**Q: Activity Description field is missing**
- A: This is the required base field
- Should always appear at the top
- If missing, refresh browser (Ctrl+F5)

**Q: Can't edit field after creating it**
- A: Fields are immutable to preserve data
- Solution: Delete and recreate if needed
- Existing entries keep their values

**Q: Need to change field order**
- A: Edit field and change the "Display Order" number
- Fields display in numerical order

---

## Common Configurations by Department

### IT Department
1. Issue Type (select, required) - options: Incident, Request, Bug, Feature
2. System/App (text, required) - which system had the issue
3. Priority (select, required) - High, Medium, Low, Urgent
4. Resolution Time (number, optional) - minutes spent
5. Root Cause (textarea, optional) - explanation

### HR Department
1. Activity Type (select, required) - Recruitment, Training, Management, Onboarding
2. Number Involved (number, optional) - people count
3. Skills Required (textarea, optional) - list of skills

### Sales Department
1. Client Name (text, optional) - who you worked with
2. Deal Stage (select, optional) - Prospect, Negotiation, Closed
3. Deal Amount (number, optional) - financial value
4. Expected Close Date (date, optional) - when expecting closure

### Customer Support
1. Ticket ID (text, required) - support ticket number
2. Category (select, required) - Technical, Billing, General
3. Resolution Status (select, optional) - Pending, Resolved, Escalated
4. Customer Feedback (textarea, optional) - notes

---

## What Happens After Setup

1. **Fields are configured** - Admin sets up in ⚙️ Configure Tracking Fields
2. **Users see form** - When they log activity, custom fields appear
3. **Data is stored** - Values saved in the system
4. **Data is preserved** - Old entries not affected
5. **Can modify anytime** - Add/edit/delete fields as needed

---

## Video Guide (if available)

See QUICKSTART_CUSTOM_FIELDS.md for step-by-step with screenshots.

---

## Support

If you have questions:
1. Check this guide again
2. Review CUSTOM_FIELDS.md (full documentation)
3. Check QUICKSTART_CUSTOM_FIELDS.md (step-by-step guide)
4. Contact system administrator

---

**Version**: 1.0  
**Updated**: February 13, 2026  
**Status**: ✅ Ready to Use
