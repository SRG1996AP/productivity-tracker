# Quick Start - Custom Tracking Fields

## 1️⃣ Initialize the Database

```bash
python migrate_tracking_fields.py
```

You should see:
```
✓ Database schema updated successfully!
✓ TrackingField table created
✓ custom_fields_data column added to DepartmentTracking

📊 Migration completed!
```

## 2️⃣ Run the Application

```bash
python run.py
```

## 3️⃣ Configure Department Fields

### Step 1: Login as Admin
- Go to http://localhost:5000
- Login with admin credentials

### Step 2: Access Department Field Management
- Click **User Management** or **Management Dashboard**
- Click **👥 User Management** 
- In the "Departments" section, click **⚙️ Manage Tracking Fields** for your department

### Step 3: Add Your First Field
- Click **"Add New Field"** button
- Fill in the form:
  - **Field Label**: "Issue Type"
  - **Field Name**: "issue_type"
  - **Field Type**: "Dropdown"
  - **Required**: Check the box
- Click **"Save Field"**

### Step 4: Add More Fields
Repeat Step 3 for additional fields:

**Example for IT Department:**
```
1. Activity Description (Textarea, Required) - Built-in
2. Issue Type (Dropdown, Required)
3. System Affected (Text, Optional)
4. Resolution Time (Number, Optional)
5. Priority (Dropdown, Required)
```

## 4️⃣ Test with a Regular User

### Step 1: Logout and Login as Department User
- Logout from admin account
- Login with a regular user account

### Step 2: Log an Activity
- Click **Log New Activity**
- You'll see:
  - **Activity Description** field (required)
  - Your **Custom Fields** below

### Step 3: Fill the Form
- Activity Description: "Resolved printer connectivity issue"
- Issue Type: "Incident"
- System Affected: "Network Printer"
- Resolution Time: "45"
- Priority: "High"

### Step 4: Submit
- Click **Log Activity**
- Success message appears
- Activity logged with all custom fields

## 5️⃣ View Your Data

### For Users:
- Go to **Department Tracking** dashboard
- See all logged activities
- Custom field values are stored

### For Admins:
- Go to **Management Dashboard**
- See overall statistics
- (View custom fields per entry coming in next version)

## 🎯 Example Configurations

### Sales Department
```
1. Activity Description (Textarea, Required)
2. Client Name (Text, Required)
3. Deal Amount (Number, Optional)
4. Sales Stage (Dropdown, Required) - Prospect, Negotiation, Closed
5. Expected Closure Date (Date, Optional)
```

### Customer Support Department
```
1. Activity Description (Textarea, Required)
2. Ticket ID (Text, Required)
3. Customer Name (Text, Optional)
4. Issue Category (Dropdown, Required) - Technical, Billing, General
5. Resolution Status (Dropdown, Optional) - Pending, Resolved, Escalated
```

### Project Management Department
```
1. Activity Description (Textarea, Required)
2. Project Name (Text, Optional)
3. Task Completed (Textarea, Optional)
4. Hours Spent (Number, Optional)
5. Status (Dropdown, Required) - On Track, At Risk, Blocked
```

## ⚠️ Important Notes

1. **Field Names Matter**: Use lowercase, no spaces
   - ✅ Good: `ticket_number`, `issue_type`, `hours_spent`
   - ❌ Bad: `Ticket Number`, `issue-type`

2. **Required Fields**: Only mark as required if truly necessary
   - This helps with completion rates

3. **Field Order**: Set display order from 1, 2, 3...
   - Leave blank for auto-ordering (creation order)

4. **Test Changes**: After adding fields, log a test activity
   - Verify fields appear correctly
   - Test required field validation
   - Check field ordering

## 🆘 Troubleshooting

**Q: Fields not showing in entry form**
- A: Refresh the browser page (Ctrl+F5)
- Check if fields are configured for your department
- Verify you're logged in with correct department user

**Q: Getting error when adding field**
- A: Ensure field name is unique (no duplicates in department)
- Field name should be lowercase with no spaces
- Check all required fields are filled

**Q: Can't access field management**
- A: You need to be logged in as an Admin user
- Check your user role in admin users list
- Contact administrator if you need admin access

**Q: Custom field values not saving**
- A: Check the field is not in the required fields without value
- Verify you clicked "Log Activity" button
- Check browser console for JavaScript errors

## 📚 More Information

- Full documentation: `CUSTOM_FIELDS.md`
- Technical details: `IMPLEMENTATION.md`
- User guide for admins: `CUSTOM_FIELDS.md`

## 🚀 Next Steps

1. ✅ Initialize database with migration
2. ✅ Configure fields for your departments
3. ✅ Test with regular users
4. ✅ Train team on new custom fields
5. ⏭️ Monitor usage and refine fields as needed

---

**Ready to go!** Your department can now customize tracking fields 🎉
