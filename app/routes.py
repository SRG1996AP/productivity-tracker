from flask import Blueprint, render_template, url_for, flash, redirect, session, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Department, DepartmentTracking, TrackingField, Grievance, GrievanceAudit, GrievanceAttachment
from app.forms import RegistrationForm, LoginForm, DepartmentTrackingForm, DynamicDepartmentTrackingForm, AddUserForm, EditUserForm, TrackingFieldForm
from datetime import datetime, timedelta
from sqlalchemy import func
import uuid
import re
import csv
import io

# Create a Blueprint
main = Blueprint('main', __name__)


def _parse_sla_minutes(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower()
    if not text:
        return None
    match = re.search(r"\d+(\.\d+)?", text)
    if not match:
        return None
    number = float(match.group(0))
    if "hour" in text or "hr" in text or text.endswith("h"):
        return int(number * 60)
    return int(number)

# --------------------------
# Home Route
# --------------------------
@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('main.management_dashboard'))
        return redirect(url_for('main.department_tracking'))
    return redirect(url_for('main.login'))


# --------------------------
# Registration Route
# --------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.department_tracking'))

    form = RegistrationForm()
    
    # Populate department choices
    departments = Department.query.all()
    form.department.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        # Hash the password using bcrypt
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Get the department object
        dept = Department.query.get(form.department.data)

        # Create new user instance
        new_user = User(
            name=form.name.data,
            employee_id=form.employee_id.data,
            department=dept.name,
            login_id=form.login_id.data,
            password=hashed_pw
        )

        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


# --------------------------
# Login Route
# --------------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('main.management_dashboard'))
        return redirect(url_for('main.department_tracking'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(login_id=form.login_id.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session.permanent = True
            login_user(user, remember=True)
            # Custom welcome message based on role
            if user.is_admin:
                flash('Logged in successfully! Welcome to Management Dashboard', 'success')
            else:
                flash(f'Logged in successfully! Welcome to {user.department} tracking.', 'success')
            # Redirect based on admin status
            if user.is_admin:
                return redirect(url_for('main.management_dashboard'))
            else:
                return redirect(url_for('main.department_tracking'))
        else:
            flash('Login failed. Wrong login ID or password.', 'danger')
    elif form.is_submitted():
        # Form was submitted but failed validation
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')

    return render_template('login.html', form=form)


# --------------------------
# Logout Route
# --------------------------
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# --------------------------
# Dashboard Route (Protected)
# --------------------------
@main.route('/dashboard')
@login_required
def dashboard():
    # Redirect based on user role
    if current_user.is_admin:
        return redirect(url_for('main.management_dashboard'))
    return redirect(url_for('main.department_tracking'))


# --------------------------
# Department Tracking Dashboard
# --------------------------
@main.route('/department-tracking')
@login_required
def department_tracking():
    # Get user's department
    user_dept = Department.query.filter_by(name=current_user.department).first()
    
    if not user_dept:
        flash('Your department is not configured. Please contact support.', 'danger')
        return redirect(url_for('main.logout'))
    
    today = datetime.utcnow().date()
    
    # Get today's entries for current user in their department
    today_entries = DepartmentTracking.query.filter(
        DepartmentTracking.user_id == current_user.id,
        DepartmentTracking.department_id == user_dept.id,
        func.date(DepartmentTracking.date_logged) == today
    ).all()
    
    # Get overall stats for user's department
    all_entries = DepartmentTracking.query.filter(
        DepartmentTracking.user_id == current_user.id,
        DepartmentTracking.department_id == user_dept.id
    ).all()
    
    total_entries = len(all_entries)
    total_duration = sum(entry.duration_mins or 0 for entry in all_entries)
    
    return render_template('department_tracking.html', 
                         department=user_dept,
                         user_name=current_user.name,
                         today_entries=today_entries,
                         total_entries=total_entries,
                         total_duration=total_duration)


# --------------------------
# Add Department Entry
# --------------------------
@main.route('/add-department-entry', methods=['GET', 'POST'])
@login_required
def add_department_entry():
    # Get user's department
    user_dept = Department.query.filter_by(name=current_user.department).first()
    
    if not user_dept:
        flash('Your department is not configured. Please contact support.', 'danger')
        return redirect(url_for('main.department_tracking'))
    
    # Use dynamic form based on department configuration
    form = DynamicDepartmentTrackingForm.create_form_for_department(user_dept)

    next_entry_no = DepartmentTracking.query.filter_by(department_id=user_dept.id).count() + 1
    today = datetime.utcnow().date()
    today_entries = DepartmentTracking.query.filter(
        DepartmentTracking.department_id == user_dept.id,
        func.date(DepartmentTracking.date_logged) == today
    ).all()
    high_priority_count = sum(
        1 for entry in today_entries
        if (entry.priority or '').lower() in ['high', 'urgent']
    )
    sla_breached_count = 0
    for entry in today_entries:
        sla_minutes = _parse_sla_minutes(entry.sla_tat)
        if sla_minutes is None:
            continue
        if entry.duration_mins and entry.duration_mins > sla_minutes:
            sla_breached_count += 1

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')

    history_query = DepartmentTracking.query.filter_by(department_id=user_dept.id)
    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            history_query = history_query.filter(DepartmentTracking.date_logged >= start_date)
        except ValueError:
            date_from = None
    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            history_query = history_query.filter(DepartmentTracking.date_logged < end_date)
        except ValueError:
            date_to = None
    if status_filter:
        history_query = history_query.filter(DepartmentTracking.status == status_filter)
    if priority_filter:
        history_query = history_query.filter(DepartmentTracking.priority == priority_filter)

    history_entries = history_query.order_by(DepartmentTracking.date_logged.desc()).limit(100).all()

    if form.validate_on_submit():
        # Only set legacy fields if they exist in the form (backward compatibility)
        legacy_fields = [
            'ticket_request_type',
            'system_application',
            'priority',
            'sla_tat',
            'tool_platform_used',
            'duration_mins',
            'frequency_per_day'
        ]

        # Collect custom field data
        custom_fields_data = {}

        # Get all tracking fields for this department
        tracking_fields = TrackingField.query.filter_by(department_id=user_dept.id).all()

        # Collect custom field values from form
        for field_def in tracking_fields:
            if field_def.field_name in ['entry_no']:
                custom_fields_data['entry_no'] = next_entry_no
                continue
            if field_def.field_name in ['priority', 'sla_tat', 'duration_mins', 'frequency_per_day', 'status']:
                continue
            if hasattr(form, field_def.field_name):
                field_value = getattr(form, field_def.field_name).data
                if field_value:  # Only store non-empty values
                    custom_fields_data[field_def.field_name] = field_value

        entry = DepartmentTracking(
            user_id=current_user.id,
            department_id=user_dept.id,
            activity_description=form.activity_description.data
        )

        for field_name in legacy_fields:
            if hasattr(form, field_name):
                field_data = getattr(form, field_name).data
                if field_data:  # Only set if value exists
                    setattr(entry, field_name, field_data)

        if hasattr(form, 'status') and form.status.data:
            entry.status = form.status.data

        # Store custom fields data
        if custom_fields_data:
            entry.set_custom_fields_data(custom_fields_data)

        db.session.add(entry)
        db.session.commit()

        flash('Activity logged successfully!', 'success')
        return redirect(url_for('main.department_tracking'))

    return render_template(
        'add_department_entry.html',
        form=form,
        department=user_dept,
        next_entry_no=next_entry_no,
        today_date=today.strftime('%Y-%m-%d'),
        today_total=len(today_entries),
        high_priority_count=high_priority_count,
        sla_breached_count=sla_breached_count,
        history_entries=history_entries,
        date_from=date_from,
        date_to=date_to,
        status_filter=status_filter,
        priority_filter=priority_filter
    )


@main.route('/export-department-entries')
@login_required
def export_department_entries():
    user_dept = Department.query.filter_by(name=current_user.department).first()
    if not user_dept:
        flash('Your department is not configured. Please contact support.', 'danger')
        return redirect(url_for('main.department_tracking'))

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')

    export_query = DepartmentTracking.query.filter_by(department_id=user_dept.id)
    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            export_query = export_query.filter(DepartmentTracking.date_logged >= start_date)
        except ValueError:
            pass
    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            export_query = export_query.filter(DepartmentTracking.date_logged < end_date)
        except ValueError:
            pass
    if status_filter:
        export_query = export_query.filter(DepartmentTracking.status == status_filter)
    if priority_filter:
        export_query = export_query.filter(DepartmentTracking.priority == priority_filter)

    entries = export_query.order_by(DepartmentTracking.date_logged.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Activity No',
        'Date Logged',
        'Employee',
        'Priority',
        'SLA / TAT',
        'Duration (mins)',
        'Frequency per Day',
        'Status',
        'Activity Description',
        'Custom Fields'
    ])

    for entry in entries:
        custom_fields = entry.get_custom_fields_data() if entry.custom_fields_data else {}
        writer.writerow([
            custom_fields.get('entry_no', ''),
            entry.date_logged.strftime('%Y-%m-%d %H:%M'),
            entry.user.name if entry.user else '',
            entry.priority or '',
            entry.sla_tat or '',
            entry.duration_mins or '',
            entry.frequency_per_day or '',
            entry.status or '',
            entry.activity_description or '',
            custom_fields
        ])

    response = current_app.response_class(
        output.getvalue(),
        mimetype='text/csv'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=productivity_entries.csv'
    return response


# --------------------------
# Management Dashboard - Overall Productivity
# --------------------------
@main.route('/management-dashboard')
@login_required
def management_dashboard():
    """Display overall productivity metrics for all departments - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to the management dashboard.', 'danger')
        return redirect(url_for('main.department_tracking'))
    
    # Get all departments except 'Management'
    departments = Department.query.filter(Department.name != 'Management').all()
    
    # Compile department stats
    department_stats = []
    total_all_entries = 0
    total_all_duration = 0
    
    for dept in departments:
        entries = DepartmentTracking.query.filter_by(department_id=dept.id).all()
        total_entries = len(entries)
        total_duration = sum(entry.duration_mins or 0 for entry in entries)
        avg_duration = total_duration / total_entries if total_entries > 0 else 0
        
        # Count users in this department
        users_count = db.session.query(func.count(User.id)).filter(User.department == dept.name).scalar()
        
        department_stats.append({
            'id': dept.id,
            'name': dept.name,
            'total_entries': total_entries,
            'total_duration': total_duration,
            'avg_duration': round(avg_duration, 2),
            'users_count': users_count
        })
        
        total_all_entries += total_entries
        total_all_duration += total_duration
    
    # Get today's stats
    today = datetime.utcnow().date()
    today_entries = DepartmentTracking.query.filter(
        func.date(DepartmentTracking.date_logged) == today
    ).all()
    today_duration = sum(entry.duration_mins or 0 for entry in today_entries)
    
    # Get total users
    total_users = User.query.count()
    
    # Average stats
    overall_avg_duration = total_all_duration / total_all_entries if total_all_entries > 0 else 0
    
    return render_template('management_dashboard.html',
                         department_stats=department_stats,
                         total_entries=total_all_entries,
                         total_duration=total_all_duration,
                         overall_avg_duration=round(overall_avg_duration, 2),
                         today_entries=len(today_entries),
                         today_duration=today_duration,
                         total_users=total_users,
                         departments_count=len(departments))


@main.route('/api/management/activities-by-dept')
@login_required
def api_activities_by_dept():
    """Return JSON counts of activities per department. Optional query params: start, end (YYYY-MM-DD), dept, priority."""
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_filter = request.args.get('dept')
    priority_filter = request.args.get('priority')

    departments = Department.query.filter(Department.name != 'Management').order_by(Department.id).all()
    if dept_filter:
        try:
            dept_id = int(dept_filter)
            departments = [d for d in departments if d.id == dept_id]
        except Exception:
            pass
    
    labels = []
    counts = []

    for dept in departments:
        q = DepartmentTracking.query.filter_by(department_id=dept.id)
        if start:
            try:
                start_dt = datetime.strptime(start, '%Y-%m-%d')
                q = q.filter(DepartmentTracking.date_logged >= start_dt)
            except Exception:
                pass
        if end:
            try:
                end_dt = datetime.strptime(end, '%Y-%m-%d')
                end_dt = end_dt + timedelta(days=1)
                q = q.filter(DepartmentTracking.date_logged < end_dt)
            except Exception:
                pass
        if priority_filter:
            q = q.filter(DepartmentTracking.priority == priority_filter)

        labels.append(dept.name)
        counts.append(q.count())

    return jsonify({'labels': labels, 'counts': counts})


@main.route('/api/management/duration-by-dept')
@login_required
def api_duration_by_dept():
    """Return JSON duration totals per department broken down by priority.
    Optional query params: start, end (YYYY-MM-DD), dept, priority.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_filter = request.args.get('dept')
    priority_filter = request.args.get('priority')

    departments = Department.query.filter(Department.name != 'Management').order_by(Department.id).all()
    if dept_filter:
        try:
            dept_id = int(dept_filter)
            departments = [d for d in departments if d.id == dept_id]
        except Exception:
            pass

    # collect priority values present in the filtered set
    priority_set = set()
    base_q = DepartmentTracking.query
    if start:
        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            base_q = base_q.filter(DepartmentTracking.date_logged >= start_dt)
        except Exception:
            pass
    if end:
        try:
            end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
            base_q = base_q.filter(DepartmentTracking.date_logged < end_dt)
        except Exception:
            pass
    if dept_filter:
        try:
            dept_id = int(dept_filter)
            base_q = base_q.filter(DepartmentTracking.department_id == dept_id)
        except Exception:
            pass
    if priority_filter:
        base_q = base_q.filter(DepartmentTracking.priority == priority_filter)

    for p in base_q.with_entities(DepartmentTracking.priority).distinct().all():
        val = (p[0] or 'Other')
        priority_set.add(val)

    priorities = sorted(priority_set) if priority_set else ['High', 'Medium', 'Low', 'Other']

    labels = [d.name for d in departments]

    # Build series: for each priority, list total duration per department
    series = []
    for pr in priorities:
        durations = []
        for dept in departments:
            q = DepartmentTracking.query.filter_by(department_id=dept.id)
            if start:
                try:
                    start_dt = datetime.strptime(start, '%Y-%m-%d')
                    q = q.filter(DepartmentTracking.date_logged >= start_dt)
                except Exception:
                    pass
            if end:
                try:
                    end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
                    q = q.filter(DepartmentTracking.date_logged < end_dt)
                except Exception:
                    pass
            if priority_filter:
                q = q.filter(DepartmentTracking.priority == priority_filter)

            total = 0
            for entry in q.all():
                pval = entry.priority or 'Other'
                if pval == pr:
                    total += (entry.duration_mins or 0)
            durations.append(total)
        series.append({'priority': pr, 'durations': durations})

    return jsonify({'labels': labels, 'priorities': priorities, 'series': series})


@main.route('/api/management/avg-duration-by-dept')
@login_required
def api_avg_duration_by_dept():
    """Return JSON average duration per department. Optional query params: start, end (YYYY-MM-DD), dept, priority."""
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_filter = request.args.get('dept')
    priority_filter = request.args.get('priority')

    departments = Department.query.filter(Department.name != 'Management').order_by(Department.id).all()
    if dept_filter:
        try:
            dept_id = int(dept_filter)
            departments = [d for d in departments if d.id == dept_id]
        except Exception:
            pass
    
    labels = []
    averages = []

    for dept in departments:
        q = DepartmentTracking.query.filter_by(department_id=dept.id)
        if start:
            try:
                start_dt = datetime.strptime(start, '%Y-%m-%d')
                q = q.filter(DepartmentTracking.date_logged >= start_dt)
            except Exception:
                pass
        if end:
            try:
                end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
                q = q.filter(DepartmentTracking.date_logged < end_dt)
            except Exception:
                pass
        if priority_filter:
            q = q.filter(DepartmentTracking.priority == priority_filter)

        entries = q.all()
        total = sum(e.duration_mins or 0 for e in entries)
        avg = (total / len(entries)) if len(entries) > 0 else 0

        labels.append(dept.name)
        averages.append(round(avg, 2))

    return jsonify({'labels': labels, 'averages': averages})


@main.route('/api/management/activities-over-time')
@login_required
def api_activities_over_time():
    """Return daily activity counts for a date range.
    Query params: start, end (YYYY-MM-DD). Optional dept (department id) to filter.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_id = request.args.get('dept')

    # Default: last 30 days
    today = datetime.utcnow().date()
    if not end:
        end_date = today
    else:
        try:
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
        except Exception:
            end_date = today

    if not start:
        start_date = end_date - timedelta(days=29)
    else:
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
        except Exception:
            start_date = end_date - timedelta(days=29)

    # Query grouped by date
    q = db.session.query(func.date(DepartmentTracking.date_logged), func.count(DepartmentTracking.id))
    q = q.filter(DepartmentTracking.date_logged >= datetime.combine(start_date, datetime.min.time()))
    q = q.filter(DepartmentTracking.date_logged < datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
    if dept_id:
        try:
            did = int(dept_id)
            q = q.filter(DepartmentTracking.department_id == did)
        except Exception:
            pass

    q = q.group_by(func.date(DepartmentTracking.date_logged)).order_by(func.date(DepartmentTracking.date_logged))
    rows = q.all()

    # rows may return string dates depending on DB driver; normalize
    counts_by_date = {}
    for r in rows:
        d = r[0]
        if not hasattr(d, 'strftime'):
            # assume string 'YYYY-MM-DD'
            key = str(d)
        else:
            key = d.strftime('%Y-%m-%d')
        counts_by_date[key] = r[1]

    # Build full date range
    labels = []
    counts = []
    cur = start_date
    while cur <= end_date:
        key = cur.strftime('%Y-%m-%d')
        labels.append(key)
        counts.append(counts_by_date.get(key, 0))
        cur = cur + timedelta(days=1)

    return jsonify({'labels': labels, 'counts': counts})


@main.route('/api/management/top-users')
@login_required
def api_top_users():
    """Return top users by activity count.
    Optional query params: start, end (YYYY-MM-DD), dept (department id), limit (int)
    """
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_id = request.args.get('dept')
    limit = request.args.get('limit', 10)
    try:
        limit = int(limit)
    except Exception:
        limit = 10

    q = db.session.query(DepartmentTracking.user_id, func.count(DepartmentTracking.id).label('cnt'))
    if start:
        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            q = q.filter(DepartmentTracking.date_logged >= start_dt)
        except Exception:
            pass
    if end:
        try:
            end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
            q = q.filter(DepartmentTracking.date_logged < end_dt)
        except Exception:
            pass
    if dept_id:
        try:
            did = int(dept_id)
            q = q.filter(DepartmentTracking.department_id == did)
        except Exception:
            pass

    q = q.group_by(DepartmentTracking.user_id).order_by(func.count(DepartmentTracking.id).desc()).limit(limit)
    rows = q.all()

    user_ids = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    users = []
    if user_ids:
        user_objs = User.query.filter(User.id.in_(user_ids)).all()
        user_map = {u.id: u.name for u in user_objs}
        for uid in user_ids:
            users.append(user_map.get(uid, f'User {uid}'))

    return jsonify({'users': users, 'counts': counts})


@main.route('/api/management/users-by-dept')
@login_required
def api_users_by_dept():
    """Return user counts per department.
    Optional query params: start, end (YYYY-MM-DD), mode=(all|active). If mode=active, counts unique users with entries in date range.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    mode = request.args.get('mode', 'all')
    start = request.args.get('start')
    end = request.args.get('end')

    departments = Department.query.filter(Department.name != 'Management').order_by(Department.id).all()
    labels = [d.name for d in departments]
    counts = []

    if mode == 'active':
        # count distinct users who logged activities in the date range per department
        q = db.session.query(DepartmentTracking.department_id, func.count(func.distinct(DepartmentTracking.user_id))).group_by(DepartmentTracking.department_id)
        if start:
            try:
                start_dt = datetime.strptime(start, '%Y-%m-%d')
                q = q.filter(DepartmentTracking.date_logged >= start_dt)
            except Exception:
                pass
        if end:
            try:
                end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
                q = q.filter(DepartmentTracking.date_logged < end_dt)
            except Exception:
                pass
        rows = q.all()
        map_counts = {r[0]: r[1] for r in rows}
        for d in departments:
            counts.append(map_counts.get(d.id, 0))
    else:
        # default: total users per department from User.department field
        for d in departments:
            c = db.session.query(func.count(User.id)).filter(User.department == d.name).scalar()
            counts.append(c)

    return jsonify({'labels': labels, 'counts': counts, 'mode': mode})


@main.route('/api/management/ticket-types')
@login_required
def api_ticket_types():
    """Return counts of ticket_request_type values. Optional start/end (YYYY-MM-DD), dept, priority."""
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_filter = request.args.get('dept')
    priority_filter = request.args.get('priority')

    q = db.session.query(DepartmentTracking.ticket_request_type, func.count(DepartmentTracking.id))
    if start:
        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            q = q.filter(DepartmentTracking.date_logged >= start_dt)
        except Exception:
            pass
    if end:
        try:
            end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
            q = q.filter(DepartmentTracking.date_logged < end_dt)
        except Exception:
            pass
    if dept_filter:
        try:
            dept_id = int(dept_filter)
            q = q.filter(DepartmentTracking.department_id == dept_id)
        except Exception:
            pass
    if priority_filter:
        q = q.filter(DepartmentTracking.priority == priority_filter)

    q = q.group_by(DepartmentTracking.ticket_request_type).order_by(func.count(DepartmentTracking.id).desc())
    rows = q.all()

    labels = []
    counts = []
    for r in rows:
        typ = r[0] or 'Unknown'
        labels.append(typ)
        counts.append(r[1])

    return jsonify({'labels': labels, 'counts': counts})


@main.route('/api/management/day-hour-heatmap')
@login_required
def api_day_hour_heatmap():
    """Return counts by weekday and hour. Optional start/end (YYYY-MM-DD), dept, priority.
    Returns: {'weekdays': [...Sunday..Saturday...], 'hours': [0..23], 'matrix': [[counts]]}
    """
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_filter = request.args.get('dept')
    priority_filter = request.args.get('priority')

    q = db.session.query(func.strftime('%w', DepartmentTracking.date_logged), func.strftime('%H', DepartmentTracking.date_logged), func.count(DepartmentTracking.id))
    if start:
        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            q = q.filter(DepartmentTracking.date_logged >= start_dt)
        except Exception:
            pass
    if end:
        try:
            end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
            q = q.filter(DepartmentTracking.date_logged < end_dt)
        except Exception:
            pass
    if dept_filter:
        try:
            dept_id = int(dept_filter)
            q = q.filter(DepartmentTracking.department_id == dept_id)
        except Exception:
            pass
    if priority_filter:
        q = q.filter(DepartmentTracking.priority == priority_filter)

    q = q.group_by(func.strftime('%w', DepartmentTracking.date_logged), func.strftime('%H', DepartmentTracking.date_logged))
    rows = q.all()

    # Weekdays: SQLite '%w' => '0' = Sunday ... '6' = Saturday
    weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    hours = [h for h in range(24)]

    # initialize matrix [7][24]
    matrix = [[0 for _ in hours] for _ in weekdays]

    for r in rows:
        try:
            day_idx = int(r[0])
            hour_idx = int(r[1])
            cnt = int(r[2])
            if 0 <= day_idx <= 6 and 0 <= hour_idx <= 23:
                matrix[day_idx][hour_idx] = cnt
        except Exception:
            continue

    return jsonify({'weekdays': weekdays, 'hours': hours, 'matrix': matrix})


@main.route('/api/management/export')
@login_required
def api_export_activities():
    """Export activities as CSV. Optional filters: start, end (YYYY-MM-DD), dept (id), priority, ticket_type."""
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    start = request.args.get('start')
    end = request.args.get('end')
    dept_id = request.args.get('dept')
    priority = request.args.get('priority')
    ticket = request.args.get('ticket_type')

    q = DepartmentTracking.query
    if start:
        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            q = q.filter(DepartmentTracking.date_logged >= start_dt)
        except Exception:
            pass
    if end:
        try:
            end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
            q = q.filter(DepartmentTracking.date_logged < end_dt)
        except Exception:
            pass
    if dept_id:
        try:
            did = int(dept_id)
            q = q.filter(DepartmentTracking.department_id == did)
        except Exception:
            pass
    if priority:
        q = q.filter(DepartmentTracking.priority == priority)
    if ticket:
        q = q.filter(DepartmentTracking.ticket_request_type == ticket)

    rows = q.order_by(DepartmentTracking.date_logged.desc()).all()

    # Build CSV
    from io import StringIO
    import csv
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['id','date_logged','department_id','user_id','ticket_request_type','priority','duration_mins','frequency_per_day','activity_description'])
    for r in rows:
        writer.writerow([
            r.id,
            (r.date_logged.isoformat() if hasattr(r.date_logged, 'isoformat') else str(r.date_logged)),
            r.department_id,
            r.user_id,
            r.ticket_request_type or '',
            r.priority or '',
            r.duration_mins or '',
            r.frequency_per_day or '',
            (r.activity_description or '').replace('\n',' ')
        ])

    output = si.getvalue()
    from flask import Response
    resp = Response(output, mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename=activities_export.csv'
    return resp


@main.route('/debug/department-stats')
@login_required
def debug_department_stats():
    """Return department stats JSON for debugging (admin only)."""
    if not current_user.is_admin:
        return jsonify({'error': 'forbidden'}), 403

    departments = Department.query.all()
    department_stats = []
    total_all_entries = 0
    total_all_duration = 0

    for dept in departments:
        entries = DepartmentTracking.query.filter_by(department_id=dept.id).all()
        total_entries = len(entries)
        total_duration = sum(entry.duration_mins or 0 for entry in entries)
        avg_duration = total_duration / total_entries if total_entries > 0 else 0
        users_count = db.session.query(func.count(User.id)).filter(User.department == dept.name).scalar()

        department_stats.append({
            'id': dept.id,
            'name': dept.name,
            'total_entries': total_entries,
            'total_duration': total_duration,
            'avg_duration': round(avg_duration, 2),
            'users_count': users_count
        })

        total_all_entries += total_entries
        total_all_duration += total_duration

    return jsonify({
        'department_stats': department_stats,
        'total_entries': total_all_entries,
        'total_duration': total_all_duration,
        'overall_avg_duration': round((total_all_duration / total_all_entries) if total_all_entries > 0 else 0, 2),
        'departments_count': len(departments)
    })


# --------------------------
# View Department Details
# --------------------------
@main.route('/department/<int:dept_id>')
@login_required
def view_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    entries = DepartmentTracking.query.filter_by(
        department_id=dept_id,
        user_id=current_user.id
    ).order_by(DepartmentTracking.date_logged.desc()).all()
    
    # Get stats for this department
    total_entries = len(entries)
    total_duration = sum(entry.duration_mins or 0 for entry in entries)
    avg_duration = total_duration / total_entries if total_entries > 0 else 0
    
    return render_template('department_details.html',
                         department=department,
                         entries=entries,
                         total_entries=total_entries,
                         total_duration=total_duration,
                         avg_duration=avg_duration)


# --------------------------
# Admin - User Management
# --------------------------
@main.route('/admin/users')
@login_required
def admin_users():
    """Manage all users - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to user management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    try:
        users = User.query.order_by(User.department, User.name).all()
        departments = Department.query.order_by(Department.name).all()
        
        return render_template('admin_users.html', users=users, departments=departments)
    except Exception as e:
        print(f"Error in admin_users: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading users: {str(e)}', 'danger')
        return redirect(url_for('main.management_dashboard'))


@main.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """Add a new user - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to user management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    form = AddUserForm()
    departments = Department.query.all()
    form.department.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        # Check if login_id already exists
        existing_user = User.query.filter_by(login_id=form.login_id.data).first()
        if existing_user:
            flash(f'Login ID "{form.login_id.data}" already exists.', 'danger')
            return redirect(url_for('main.admin_add_user'))
        
        # Hash password and create user
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        dept = Department.query.get(form.department.data)
        
        new_user = User(
            name=form.name.data,
            employee_id=form.employee_id.data,
            department=dept.name,
            login_id=form.login_id.data,
            password=hashed_pw,
            is_admin=form.is_admin.data
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User "{form.name.data}" added successfully!', 'success')
        return redirect(url_for('main.admin_users'))
    
    return render_template('admin_add_user.html', form=form)


@main.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Edit a user - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to user management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    departments = Department.query.all()
    form.department.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        # Check if login_id is already used by another user
        existing_user = User.query.filter(User.login_id == form.login_id.data, User.id != user_id).first()
        if existing_user:
            flash(f'Login ID "{form.login_id.data}" is already in use.', 'danger')
            return redirect(url_for('main.admin_edit_user', user_id=user_id))
        
        # Update user fields
        user.name = form.name.data
        user.employee_id = form.employee_id.data
        user.login_id = form.login_id.data
        user.is_admin = form.is_admin.data
        
        # Update department
        dept = Department.query.get(form.department.data)
        user.department = dept.name
        
        # Update password if provided
        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        db.session.commit()
        
        flash(f'User "{user.name}" updated successfully!', 'success')
        return redirect(url_for('main.admin_users'))
    
    # Pre-fill form with current user data
    if request.method == 'GET':
        form.name.data = user.name
        form.employee_id.data = user.employee_id
        form.login_id.data = user.login_id
        form.is_admin.data = user.is_admin
        # Set department
        dept = Department.query.filter_by(name=user.department).first()
        if dept:
            form.department.data = dept.id
    
    return render_template('admin_edit_user.html', form=form, user=user)


@main.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete a user - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to user management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the last admin user
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Cannot delete the last admin user.', 'danger')
            return redirect(url_for('main.admin_users'))
    
    user_name = user.name
    
    # Delete user's activity logs
    DepartmentTracking.query.filter_by(user_id=user_id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{user_name}" deleted successfully!', 'success')
    return redirect(url_for('main.admin_users'))


# --------------------------
# Department Tracking Fields Management
# --------------------------
@main.route('/admin/department-fields/<int:dept_id>')
@login_required
def admin_department_fields(dept_id):
    """View and manage tracking fields for a department - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to field management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    department = Department.query.get_or_404(dept_id)
    fields = TrackingField.query.filter_by(department_id=dept_id).order_by(TrackingField.order).all()
    
    return render_template('admin_department_fields.html', department=department, fields=fields)


@main.route('/admin/department-fields/<int:dept_id>/add', methods=['GET', 'POST'])
@login_required
def admin_add_field(dept_id):
    """Add a new tracking field for a department - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to field management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    department = Department.query.get_or_404(dept_id)
    form = TrackingFieldForm()
    
    if form.validate_on_submit():
        # Check if field_name is unique for this department
        existing = TrackingField.query.filter_by(
            department_id=dept_id, 
            field_name=form.field_name.data
        ).first()
        
        if existing:
            flash(f'A field with name "{form.field_name.data}" already exists for this department.', 'danger')
            return redirect(url_for('main.admin_add_field', dept_id=dept_id))
        
        # Get the next order number
        max_order = db.session.query(db.func.max(TrackingField.order)).filter_by(department_id=dept_id).scalar()
        next_order = (max_order or 0) + 1
        
        field = TrackingField(
            department_id=dept_id,
            field_name=form.field_name.data,
            field_type=form.field_type.data,
            field_label=form.field_label.data,
            is_required=form.is_required.data,
            order=form.order.data or next_order
        )
        
        db.session.add(field)
        db.session.commit()
        
        flash(f'Field "{form.field_label.data}" added successfully!', 'success')
        return redirect(url_for('main.admin_department_fields', dept_id=dept_id))
    
    return render_template('admin_add_field.html', form=form, department=department)


@main.route('/admin/department-fields/edit/<int:field_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_field(field_id):
    """Edit a tracking field - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to field management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    field = TrackingField.query.get_or_404(field_id)
    department = field.department
    form = TrackingFieldForm()
    
    if form.validate_on_submit():
        # Check if field_name is unique for this department (excluding current field)
        existing = TrackingField.query.filter(
            TrackingField.department_id == field.department_id,
            TrackingField.field_name == form.field_name.data,
            TrackingField.id != field_id
        ).first()
        
        if existing:
            flash(f'A field with name "{form.field_name.data}" already exists for this department.', 'danger')
            return redirect(url_for('main.admin_edit_field', field_id=field_id))
        
        field.field_name = form.field_name.data
        field.field_type = form.field_type.data
        field.field_label = form.field_label.data
        field.is_required = form.is_required.data
        if form.order.data:
            field.order = form.order.data
        
        db.session.commit()
        
        flash(f'Field "{form.field_label.data}" updated successfully!', 'success')
        return redirect(url_for('main.admin_department_fields', dept_id=field.department_id))
    
    if request.method == 'GET':
        form.field_name.data = field.field_name
        form.field_type.data = field.field_type
        form.field_label.data = field.field_label
        form.is_required.data = field.is_required
        form.order.data = field.order
    
    return render_template('admin_edit_field.html', form=form, field=field, department=department)


@main.route('/admin/department-fields/delete/<int:field_id>', methods=['POST'])
@login_required
def admin_delete_field(field_id):
    """Delete a tracking field - Admin only"""
    if not current_user.is_admin:
        flash('You do not have access to field management.', 'danger')
        return redirect(url_for('main.management_dashboard'))
    
    field = TrackingField.query.get_or_404(field_id)
    dept_id = field.department_id
    field_label = field.field_label
    
    db.session.delete(field)
    db.session.commit()
    
    flash(f'Field "{field_label}" deleted successfully!', 'success')
    return redirect(url_for('main.admin_department_fields', dept_id=dept_id))

# --------------------------
# Grievance Management API
# --------------------------

@main.route('/submit-grievance')
def submit_grievance_form():
    """Display grievance submission form (public page)"""
    return render_template('submit_grievance.html')


@main.route('/grievance-dashboard')
@login_required
def grievance_dashboard():
    """Display HR grievance management dashboard"""
    if not current_user.is_admin:
        flash('Access denied. HR Admin privilege required.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('grievance_dashboard.html')


    """Generate unique case ID in format: GR-YYYYMMDD-XXXX"""
    timestamp = datetime.utcnow().strftime('%Y%m%d')
    random_suffix = str(uuid.uuid4().hex[:4]).upper()
    return f"GR-{timestamp}-{random_suffix}"


def analyze_grievance_with_ai(grievance_text):
    """
    AI Analysis stub for categorization, priority, and sentiment.
    This integrates with OpenAI or a local NLP model.
    
    Returns: {
        'category': str,
        'priority': str,
        'sentiment_score': float,
        'flagged_keywords': list,
        'should_escalate': bool,
        'escalation_reason': str
    }
    """
    # Deterministic keyword rules (can be enhanced with ML model)
    sensitive_keywords = {
        'harassment': True,
        'bullying': True,
        'threat': True,
        'illegal': True,
        'discrimination': True,
        'resign': True,
        'suicide': True,
        'harm': True
    }
    
    text_lower = grievance_text.lower()
    flagged = [kw for kw in sensitive_keywords.keys() if kw in text_lower]
    should_escalate = bool(flagged)
    
    # Simple category detection (rule-based; replace with ML model)
    category = 'Others'
    category_keywords = {
        'Workplace Harassment': ['harassment', 'bullying', 'abuse', 'intimidation'],
        'Payroll / Salary Issue': ['salary', 'payroll', 'payment', 'wage', 'bonus'],
        'Supervisor Misconduct': ['supervisor', 'manager', 'boss', 'manager', 'conduct'],
        'Discrimination': ['discrimination', 'bias', 'racist', 'sexist'],
        'Workload Concern': ['workload', 'overwork', 'overtime', 'stress', 'pressure'],
        'Policy Violation': ['policy', 'violation', 'breach', 'rule'],
        'IT / System Issue': ['it', 'system', 'computer', 'software', 'access']
    }
    
    for cat, keywords in category_keywords.items():
        if any(kw in text_lower for kw in keywords):
            category = cat
            break
    
    # Simple priority assignment
    priority = 'Low'
    if flagged or 'urgent' in text_lower or 'critical' in text_lower:
        priority = 'High'
    elif 'soon' in text_lower or 'asap' in text_lower or 'immediate' in text_lower:
        priority = 'Medium'
    
    # Sentiment score (simple negative word count; replace with proper sentiment model)
    negative_words = ['bad', 'worse', 'worst', 'angry', 'upset', 'frustrated', 'disappointed']
    negative_count = sum(1 for word in negative_words if word in text_lower)
    sentiment_score = max(-1.0, -0.1 * negative_count)
    
    if flagged:
        sentiment_score = min(sentiment_score - 0.2, -0.8)
    
    return {
        'category': category,
        'priority': priority,
        'sentiment_score': round(sentiment_score, 2),
        'flagged_keywords': flagged,
        'should_escalate': should_escalate,
        'escalation_reason': f"Keywords detected: {', '.join(flagged)}" if flagged else None
    }


def analyze_grievance_with_ai(grievance_text):
    """
    Submit a new grievance (public endpoint, no authentication required).
    
    Request JSON:
    {
        "employee_name": str,
        "employee_id": str,
        "campaign": str,
        "contact_number": str,
        "grievance_text": str,
        "is_anonymous": bool (optional, default False)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_name', 'employee_id', 'campaign', 'contact_number', 'grievance_text']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate field formats
        if not isinstance(data.get('contact_number'), str) or not re.match(r'^\d{10,}$', data['contact_number'].replace('-', '').replace(' ', '')):
            return jsonify({
                'success': False,
                'message': 'Invalid contact number format (must be at least 10 digits)'
            }), 400
        
        if len(data['grievance_text'].strip()) < 10:
            return jsonify({
                'success': False,
                'message': 'Grievance description must be at least 10 characters'
            }), 400
        
        # Generate case ID and analyze grievance
        case_id = generate_case_id()
        ai_analysis = analyze_grievance_with_ai(data['grievance_text'])
        
        # Create grievance record
        grievance = Grievance(
            case_id=case_id,
            employee_name=data['employee_name'] if not data.get('is_anonymous') else 'Anonymous',
            employee_id=data['employee_id'] if not data.get('is_anonymous') else 'ANONYMOUS',
            campaign=data['campaign'],
            contact_number=data['contact_number'],
            grievance_text=data['grievance_text'],
            is_anonymous=data.get('is_anonymous', False),
            ai_category=ai_analysis['category'],
            ai_priority=ai_analysis['priority'],
            ai_sentiment_score=ai_analysis['sentiment_score'],
            status='Open',
            escalated_to_senior_hr=ai_analysis['should_escalate'],
            escalation_reason=ai_analysis['escalation_reason']
        )
        
        grievance.set_flagged_keywords(ai_analysis['flagged_keywords'])
        
        db.session.add(grievance)
        
        # Create initial audit entry
        audit_entry = GrievanceAudit(
            grievance_id=grievance.id if grievance.id else None,  # Will be set after flush
            changed_by='System',
            from_status=None,
            to_status='Open',
            remarks='Grievance submitted - AI analysis completed'
        )
        
        db.session.flush()  # Ensure grievance.id is set
        audit_entry.grievance_id = grievance.id
        db.session.add(audit_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Your grievance has been successfully submitted. Case ID: {case_id}',
            'case_id': case_id,
            'status': 'Open'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500


@main.route('/api/grievances', methods=['GET'])
@login_required
def list_grievances():
    """
    Retrieve grievances (HR Admin only).
    
    Query parameters:
    - date_from: YYYY-MM-DD
    - date_to: YYYY-MM-DD
    - campaign: str
    - status: str (Open, Under Review, etc.)
    - priority: str (High, Medium, Low)
    - search: employee_id or case_id
    - page: int (default 1)
    - per_page: int (default 20)
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied. HR Admin privilege required.'}), 403
    
    try:
        # Parse filters
        query = Grievance.query
        
        if request.args.get('date_from'):
            date_from = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
            query = query.filter(Grievance.submitted_at >= date_from)
        
        if request.args.get('date_to'):
            date_to = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Grievance.submitted_at < date_to)
        
        if request.args.get('campaign'):
            query = query.filter(Grievance.campaign == request.args.get('campaign'))
        
        if request.args.get('status'):
            query = query.filter(Grievance.status == request.args.get('status'))
        
        if request.args.get('priority'):
            query = query.filter(Grievance.ai_priority == request.args.get('priority'))
        
        if request.args.get('search'):
            search_term = f"%{request.args.get('search')}%"
            query = query.filter(
                (Grievance.employee_id.ilike(search_term)) |
                (Grievance.case_id.ilike(search_term))
            )
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        paginated = query.order_by(Grievance.submitted_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        grievances_data = [{
            'id': g.id,
            'case_id': g.case_id,
            'employee_name': g.employee_name,
            'employee_id': g.employee_id,
            'campaign': g.campaign,
            'ai_category': g.ai_category,
            'ai_priority': g.ai_priority,
            'status': g.status,
            'submitted_at': g.submitted_at.isoformat() if g.submitted_at else None,
            'is_escalated': g.escalated_to_senior_hr
        } for g in paginated.items]
        
        return jsonify({
            'success': True,
            'grievances': grievances_data,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@main.route('/api/grievances/<case_id>', methods=['GET'])
@login_required
def view_grievance(case_id):
    """View grievance details (HR Admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied.'}), 403
    
    grievance = Grievance.query.filter_by(case_id=case_id).first_or_404()
    
    audit_trail = [{
        'changed_at': a.changed_at.isoformat() if a.changed_at else None,
        'changed_by': a.changed_by,
        'from_status': a.from_status,
        'to_status': a.to_status,
        'remarks': a.remarks
    } for a in grievance.audit_entries]
    
    return jsonify({
        'success': True,
        'grievance': {
            'id': grievance.id,
            'case_id': grievance.case_id,
            'employee_name': grievance.employee_name,
            'employee_id': grievance.employee_id,
            'campaign': grievance.campaign,
            'contact_number': grievance.contact_number,
            'grievance_text': grievance.grievance_text,
            'is_anonymous': grievance.is_anonymous,
            'ai_category': grievance.ai_category,
            'ai_priority': grievance.ai_priority,
            'ai_sentiment_score': grievance.ai_sentiment_score,
            'ai_keywords_flagged': grievance.get_flagged_keywords(),
            'status': grievance.status,
            'hr_remarks': grievance.hr_remarks,
            'escalated_to_senior_hr': grievance.escalated_to_senior_hr,
            'escalation_reason': grievance.escalation_reason,
            'submitted_at': grievance.submitted_at.isoformat() if grievance.submitted_at else None,
            'updated_at': grievance.updated_at.isoformat() if grievance.updated_at else None,
            'audit_trail': audit_trail
        }
    }), 200


@main.route('/api/grievances/<case_id>/status', methods=['PUT'])
@login_required
def update_grievance_status(case_id):
    """Update grievance status (HR Admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied.'}), 403
    
    grievance = Grievance.query.filter_by(case_id=case_id).first_or_404()
    data = request.get_json()
    
    valid_statuses = ['Open', 'Under Review', 'Investigation in Progress', 'Escalated', 'Resolved', 'Closed']
    if data.get('status') not in valid_statuses:
        return jsonify({'success': False, 'message': f'Invalid status. Valid statuses: {", ".join(valid_statuses)}'}), 400
    
    old_status = grievance.status
    grievance.status = data['status']
    grievance.hr_remarks = data.get('remarks', grievance.hr_remarks)
    grievance.updated_at = datetime.utcnow()
    
    audit_entry = GrievanceAudit(
        grievance_id=grievance.id,
        changed_by=current_user.name,
        from_status=old_status,
        to_status=data['status'],
        remarks=data.get('remarks')
    )
    
    db.session.add(audit_entry)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Grievance {case_id} status updated to {data["status"]}',
        'status': grievance.status
    }), 200


@main.route('/api/grievances/dashboard/metrics', methods=['GET'])
@login_required
def grievance_dashboard_metrics():
    """Get dashboard metrics (HR Admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied.'}), 403
    
    try:
        # Total grievances by month (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        monthly_totals = db.session.query(
            func.date_trunc('month', Grievance.submitted_at).label('month'),
            func.count(Grievance.id).label('count')
        ).filter(Grievance.submitted_at >= twelve_months_ago).group_by('month').all()
        
        monthly_data = [{
            'month': str(m[0]) if m[0] else 'Unknown',
            'count': m[1] or 0
        } for m in monthly_totals]
        
        # Status breakdown
        status_counts = db.session.query(
            Grievance.status,
            func.count(Grievance.id).label('count')
        ).group_by(Grievance.status).all()
        
        status_data = {s[0]: s[1] for s in status_counts}
        
        # Priority breakdown
        priority_counts = db.session.query(
            Grievance.ai_priority,
            func.count(Grievance.id).label('count')
        ).group_by(Grievance.ai_priority).all()
        
        priority_data = {p[0]: p[1] for p in priority_counts}
        
        # Category breakdown
        category_counts = db.session.query(
            Grievance.ai_category,
            func.count(Grievance.id).label('count')
        ).group_by(Grievance.ai_category).all()
        
        category_data = {c[0]: c[1] for c in category_counts}
        
        # Campaign breakdown
        campaign_counts = db.session.query(
            Grievance.campaign,
            func.count(Grievance.id).label('count')
        ).group_by(Grievance.campaign).all()
        
        campaign_data = {c[0]: c[1] for c in campaign_counts}
        
        return jsonify({
            'success': True,
            'metrics': {
                'total_grievances': Grievance.query.count(),
                'open_cases': Grievance.query.filter_by(status='Open').count(),
                'resolved_cases': Grievance.query.filter_by(status='Resolved').count(),
                'high_priority_cases': Grievance.query.filter_by(ai_priority='High').count(),
                'escalated_cases': Grievance.query.filter_by(escalated_to_senior_hr=True).count(),
                'monthly_totals': monthly_data,
                'status_breakdown': status_data,
                'priority_breakdown': priority_data,
                'category_breakdown': category_data,
                'campaign_breakdown': campaign_data
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500