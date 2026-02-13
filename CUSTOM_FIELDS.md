# Custom Department Tracking Fields

## Overview

Each department can now customize and manage their own **productivity tracking fields**. Instead of using a fixed set of fields for all departments, each department can design their tracking form to match their specific needs.

## Features

✅ **Department-Specific Fields** - Each department has its own set of tracking fields
✅ **Multiple Field Types** - Text, Textarea, Number, Date, and Dropdown fields
✅ **Required/Optional** - Mark fields as required or optional
✅ **Custom Ordering** - Control the display order of fields
✅ **Flexible Configuration** - Add, edit, or delete fields anytime
✅ **Backward Compatible** - Old tracking data is preserved

## Getting Started

### 1. Initialize the Database

Before using the custom fields feature, you need to create the new database tables:

```bash
python migrate_tracking_fields.py
```

This will:
- Create the `TrackingField` table
- Add the `custom_fields_data` column to `DepartmentTracking` table

### 2. Access Department Field Configuration

1. Log in as an **Admin user**
2. Click **User Management** (from Management Dashboard)
3. In the "Departments" section, click **⚙️ Manage Tracking Fields** for the department
4. You'll see the field management page

## Managing Tracking Fields

### Adding a New Field

1. Click **"Add New Field"** button
2. Fill in the field details:
   - **Field Label**: The display name users will see (e.g., "System Used")
   - **Field Name**: Internal identifier (e.g., "system_used", lowercase no spaces)
   - **Field Type**: Choose from:
     - **Text**: Single-line text input
     - **Textarea**: Multi-line text input
     - **Number**: Numeric input only
     - **Date**: Date picker
     - **Dropdown**: Select from predefined options
   - **Required**: Check if this field must be filled
   - **Display Order**: Number determining field order (auto-calculated if left blank)

3. Click **"Save Field"**

### Editing an Existing Field

1. Click **"Edit"** next to the field in the list
2. Modify the field properties
3. Click **"Save Field"**

### Deleting a Field

1. Click **"Delete"** next to the field
2. Confirm the deletion
3. The field will be removed (existing entries keep their data)

## Field Types

### Text Input
Simple single-line text field. Good for:
- System names
- Application names
- Ticket IDs

✅ **Example**: Field Name: `system_used` | Label: `System / Application Used`

### Text Area
Multi-line text input. Good for:
- Detailed descriptions
- Notes and comments
- Problem statements

✅ **Example**: Field Name: `description` | Label: `Activity Description`

### Number
Numeric input only. Good for:
- Duration tracking
- Frequency counts
- Quantities

✅ **Example**: Field Name: `duration` | Label: `Duration (minutes)`

### Date
Date picker. Good for:
- Deadline tracking
- Event dates
- Completion dates

✅ **Example**: Field Name: `due_date` | Label: `Due Date`

### Dropdown
Select from a list of options. Good for:
- Priority levels
- Status selection
- Category selection

✅ **Example**: Field Name: `priority` | Label: `Priority` | Options: High, Medium, Low

## Example Configurations

### IT Support Department

```
1. Activity Description (Textarea) - Required
2. Ticket Number (Text) - Optional
3. Issue Type (Dropdown) - Required - Options: Incident, Service Request, Bug, Feature
4. Resolution Time (Number) - Optional
5. Software/System (Text) - Optional
```

### Human Resources Department

```
1. Activity Description (Textarea) - Required
2. Activity Type (Dropdown) - Required - Options: Recruitment, Onboarding, Training, Management
3. Number of People (Number) - Optional
4. Required Skills (Textarea) - Optional
5. Priority (Dropdown) - Optional - Options: High, Medium, Low
```

### Finance Department

```
1. Activity Description (Textarea) - Required
2. Transaction Type (Dropdown) - Required - Options: Invoice, Payment, Report, Reconciliation
3. Amount (Number) - Optional
4. Account Code (Text) - Optional
5. Due Date (Date) - Optional
```

## How Users See Custom Fields

When a user logs an activity for their department:

1. They'll see the **Activity Description** field (always present)
2. Below that, they'll see all the **Custom Fields** configured for their department
3. Fields marked as "Required" will have a **red asterisk (*)** next to them
4. Fields will appear in the order specified by the Display Order

## How Data is Stored

### Column Storage

**Old Fields** (for backward compatibility):
- `activity_description`
- `ticket_request_type`
- `system_application`
- `priority`
- `sla_tat`
- `tool_platform_used`
- `duration_mins`
- `frequency_per_day`

**New Fields**:
- `custom_fields_data` (JSON column storing all custom field values)

### Custom Fields JSON Structure

Custom field values are stored as JSON:

```json
{
  "system_used": "SAP",
  "issue_type": "Incident",
  "resolution_time": 45,
  "due_date": "2026-02-20"
}
```

## API & Data Retrieval

### Getting Custom Field Data in Code

```python
from app.models import DepartmentTracking

entry = DepartmentTracking.query.get(entry_id)

# Get all custom fields data
custom_data = entry.get_custom_fields_data()
# Returns: {'field_name': 'field_value', ...}

# Access specific field
system_used = custom_data.get('system_used')
```

### Setting Custom Field Data

```python
entry = DepartmentTracking(
    user_id=user.id,
    department_id=dept.id,
    activity_description="Resolved critical issue"
)

# Set custom fields
entry.set_custom_fields_data({
    'system_used': 'SAP',
    'issue_type': 'Incident',
    'resolution_time': 45
})

db.session.add(entry)
db.session.commit()
```

## Database Schema

### TrackingField Table

```sql
CREATE TABLE tracking_field (
    id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES department(id),
    field_name VARCHAR(200) NOT NULL,           -- Internal identifier
    field_type VARCHAR(50) NOT NULL,            -- text, textarea, number, date, select
    field_label VARCHAR(200) NOT NULL,          -- Display label
    is_required BOOLEAN DEFAULT TRUE,           -- Required field
    order INTEGER DEFAULT 0,                    -- Display order
    choices TEXT,                               -- JSON array for select fields
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### DepartmentTracking Changes

```sql
ALTER TABLE department_tracking 
ADD COLUMN custom_fields_data TEXT;  -- Stores JSON of custom field values
```

## Troubleshooting

### Fields Not Appearing in Entry Form
- **Problem**: Custom fields not showing when logging activity
- **Solution**: 
  1. Verify fields are configured for the department
  2. Check the field's `is_required` or other settings
  3. Refresh the browser page

### Dropdown Options Not Saving
- **Problem**: Can't see options when editing a dropdown field
- **Solution**: 
  1. Dropdown options are coming in the next update
  2. For now, use basic dropdown fields
  3. Text field is a good alternative

### Field Name Conflicts
- **Problem**: Getting error about duplicate field name
- **Solution**: 
  1. Field names must be unique within a department
  2. Field names cannot contain spaces or special characters
  3. Use lowercase letters, numbers, and underscores only

## Limitations & Future Enhancements

### Current Limitations
- Dropdown field options need to be added in the next version
- Field editing doesn't preserve existing data
- No field validation rules (min/max length)

### Planned Features
- ✨ Dropdown field options management
- ✨ Field validation rules (min/max values, regex patterns)
- ✨ Field descriptions/tooltips
- ✨ Export tracking data with custom fields
- ✨ Advanced filtering by custom fields

## Best Practices

1. **Keep Field Names Simple**: Use descriptive but short field names
   - ✅ Good: `ticket_number`, `resolution_time`, `priority_level`
   - ❌ Bad: `the_ticket_number_field`, `how_long_it_took`

2. **Use Appropriate Field Types**: Match the field type to the data
   - Numbers for quantities/durations
   - Dates for time-sensitive data
   - Dropdowns for fixed options
   - Textarea for descriptions

3. **Make Fields Required Only When Necessary**: Too many required fields can discourage logging
   - ✅ Always required: Activity Description
   - ⚠️ Often required: Type/Category, Priority
   - ❌ Rarely required: Duration, Notes

4. **Test Your Configuration**: Log a test entry after adding/changing fields
   - Verify fields appear correctly
   - Test required field validation
   - Check field order

5. **Document Your Fields**: Create a guide for your department users
   - Explain what each field should contain
   - Provide examples
   - Share with team members

## Support & Questions

For issues or questions about custom tracking fields:
1. Check the troubleshooting section above
2. Review the example configurations
3. Contact your system administrator

---

**Version**: 1.0 | **Last Updated**: February 2026
