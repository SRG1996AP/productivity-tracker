from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(min=1, max=50)])
    department = SelectField('Department', validators=[DataRequired()], coerce=int)
    login_id = StringField('Login ID', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    login_id = StringField('Login ID', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Login')

class DepartmentTrackingForm(FlaskForm):
    activity_description = TextAreaField('Activity Description', validators=[DataRequired(), Length(min=5, max=1000)])
    ticket_request_type = StringField('Ticket / Request Type', validators=[Optional(), Length(max=200)])
    system_application = StringField('System / Application Used', validators=[Optional(), Length(max=200)])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Urgent', 'Urgent')], validators=[Optional()])
    sla_tat = StringField('SLA / TAT', validators=[Optional(), Length(max=100)])
    tool_platform_used = StringField('Tool / Platform Used', validators=[Optional(), Length(max=200)])
    duration_mins = IntegerField('Duration (minutes)', validators=[Optional()])
    frequency_per_day = IntegerField('Frequency per Day', validators=[Optional()])
    submit = SubmitField('Log Activity')

class AddUserForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(min=1, max=50)])
    department = SelectField('Department', validators=[DataRequired()], coerce=int)
    login_id = StringField('Login ID', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Make Admin')
    submit = SubmitField('Add User')

class EditUserForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(min=1, max=50)])
    department = SelectField('Department', validators=[DataRequired()], coerce=int)
    login_id = StringField('Login ID', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password (leave blank to keep current)', validators=[Optional(), Length(min=6)])
    is_admin = BooleanField('Make Admin')
    submit = SubmitField('Update User')

