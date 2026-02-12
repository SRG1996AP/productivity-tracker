from flask import Blueprint, render_template, url_for, flash, redirect, session, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Department, DepartmentTracking
from app.forms import RegistrationForm, LoginForm, DepartmentTrackingForm, AddUserForm, EditUserForm
from datetime import datetime, timedelta
from sqlalchemy import func

# Create a Blueprint
main = Blueprint('main', __name__)

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
    
    form = DepartmentTrackingForm()
    
    # Remove department field since it's automatically set to user's department
    if form.validate_on_submit():
        entry = DepartmentTracking(
            user_id=current_user.id,
            department_id=user_dept.id,
            activity_description=form.activity_description.data,
            ticket_request_type=form.ticket_request_type.data,
            system_application=form.system_application.data,
            priority=form.priority.data,
            sla_tat=form.sla_tat.data,
            tool_platform_used=form.tool_platform_used.data,
            duration_mins=form.duration_mins.data,
            frequency_per_day=form.frequency_per_day.data
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Activity logged successfully!', 'success')
        return redirect(url_for('main.department_tracking'))
    
    return render_template('add_department_entry.html', form=form, department=user_dept)


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
    
    users = User.query.order_by(User.department, User.name).all()
    departments = Department.query.all()
    
    return render_template('admin_users.html', users=users, departments=departments)


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

