"""
Default tracking fields per department.
"""

DEFAULT_PRIORITY_CHOICES = ["Low", "Medium", "High", "Urgent"]


def _fields(*items):
    return list(items)


def get_default_tracking_fields_by_key():
    """Return default fields keyed by normalized department type."""
    return {
        "operations_leaders": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "campaign_account", "label": "Campaign / Account", "type": "text"},
            {"name": "client_ops_requirement", "label": "Client / OPS Requirement", "type": "text"},
            {"name": "activity_category", "label": "Activity Category", "type": "text"},
            {"name": "kpi_sla_impacted", "label": "KPI / SLA Impacted", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_evidence", "label": "Output / Evidence", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "rta": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "supporting_campaign_project", "label": "Supporting Campaign/Project", "type": "text"},
            {"name": "client_ops_requirement", "label": "Client/OPS Requirement", "type": "text"},
            {"name": "report_name", "label": "Report Name", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "tool_crm_telephony_used", "label": "Tool/CRM/Telephony Used", "type": "text"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "training": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "training_program_batch", "label": "Training Program / Batch", "type": "text"},
            {"name": "ops_client_requirement", "label": "OPS / Client Requirement", "type": "text"},
            {"name": "training_type", "label": "Training Type", "type": "text"},
            {"name": "no_of_trainees", "label": "No. of Trainees", "type": "number"},
            {"name": "training_mode", "label": "Training Mode", "type": "text"},
            {"name": "tool_lms_used", "label": "Tool / LMS Used", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_report", "label": "Output / Report", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "qa": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "campaign_process_audited", "label": "Campaign / Process Audited", "type": "text"},
            {"name": "ops_client_requirement", "label": "OPS / Client Requirement", "type": "text"},
            {"name": "audit_type", "label": "Audit Type", "type": "text"},
            {"name": "sample_size", "label": "Sample Size", "type": "number"},
            {"name": "qa_standard_kpi", "label": "QA Standard / KPI", "type": "text"},
            {"name": "qa_tool_used", "label": "QA Tool Used", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_scorecard", "label": "Output / Scorecard", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "finance": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "financial_area", "label": "Financial Area", "type": "text"},
            {"name": "ops_business_requirement", "label": "OPS / Business Requirement", "type": "text"},
            {"name": "transaction_type", "label": "Transaction Type", "type": "text"},
            {"name": "amount_if_applicable", "label": "Amount (if applicable)", "type": "number"},
            {"name": "approval_level", "label": "Approval Level", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_report", "label": "Output / Report", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "ta": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "hiring_project_campaign", "label": "Hiring Project / Campaign", "type": "text"},
            {"name": "ops_client_requirement", "label": "OPS / Client Requirement", "type": "text"},
            {"name": "position_role", "label": "Position / Role", "type": "text"},
            {"name": "hiring_volume", "label": "Hiring Volume", "type": "number"},
            {"name": "stage_of_hiring", "label": "Stage of Hiring", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_report", "label": "Output / Report", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "hr": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "hr_process_area", "label": "HR Process Area", "type": "text"},
            {"name": "ops_employee_requirement", "label": "OPS / Employee Requirement", "type": "text"},
            {"name": "request_type", "label": "Request Type", "type": "text"},
            {"name": "policy_sop_reference", "label": "Policy / SOP Reference", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_report", "label": "Output / Report", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
        "it": _fields(
            {"name": "entry_no", "label": "No", "type": "number"},
            {"name": "system_application", "label": "System / Application Supported", "type": "text"},
            {"name": "ops_business_requirement", "label": "OPS / Business Requirement", "type": "text"},
            {"name": "ticket_request_type", "label": "Ticket / Request Type", "type": "text"},
            {
                "name": "priority",
                "label": "Priority",
                "type": "select",
                "choices": DEFAULT_PRIORITY_CHOICES,
            },
            {"name": "sla_tat", "label": "SLA / TAT", "type": "text"},
            {"name": "tool_platform_used", "label": "Tool / Platform Used", "type": "text"},
            {"name": "duration_mins", "label": "Duration (mins)", "type": "number"},
            {"name": "output_report", "label": "Output / Report", "type": "textarea"},
            {"name": "remarks", "label": "Remarks", "type": "textarea"},
        ),
    }


def match_department_key(department_name):
    """Match a department name to a default field group key."""
    if not department_name:
        return None

    name = department_name.lower()
    if "management" in name:
        return None
    if "operations" in name or "operation" in name:
        return "operations_leaders"
    if "rta" in name or "real time analyst" in name:
        return "rta"
    if "training" in name:
        return "training"
    if "qa" in name or "quality" in name:
        return "qa"
    if "finance" in name:
        return "finance"
    if "talent" in name or "ta" in name:
        return "ta"
    if "human resource" in name or "hr" in name:
        return "hr"
    if "information technology" in name or "it" in name:
        return "it"
    return None
