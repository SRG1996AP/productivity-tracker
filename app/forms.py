from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, BooleanField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from wtforms.fields import Field

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

class DynamicDepartmentTrackingForm(FlaskForm):
    """Dynamic form that builds fields based on department configuration"""
    activity_description = TextAreaField('Activity Description', validators=[DataRequired(), Length(min=5, max=1000)])
    submit = SubmitField('Log Activity')
    
    @staticmethod
    def create_form_for_department(department_obj):
        """
        Factory method to create a form with fields based on department configuration
        """
        class GeneratedForm(FlaskForm):
            activity_description = TextAreaField('Activity Description', validators=[DataRequired(), Length(min=5, max=1000)])
            pass
        
        # Add dynamic fields based on department's tracking_fields
        if department_obj and department_obj.tracking_fields:
            for field_def in sorted(department_obj.tracking_fields, key=lambda x: x.order):
                field_validators = []
                if field_def.is_required:
                    field_validators.append(DataRequired())
                else:
                    field_validators.append(Optional())
                
                field_obj = None
                
                if field_def.field_type == 'text':
                    field_obj = StringField(field_def.field_label, validators=field_validators)
                elif field_def.field_type == 'textarea':
                    field_obj = TextAreaField(field_def.field_label, validators=field_validators)
                elif field_def.field_type == 'number':
                    field_obj = IntegerField(field_def.field_label, validators=field_validators)
                elif field_def.field_type == 'date':
                    field_obj = StringField(field_def.field_label, validators=field_validators)  # Will use HTML5 date input in template
                elif field_def.field_type == 'select':
                    choices = field_def.get_choices()
                    field_obj = SelectField(field_def.field_label, choices=[(c, c) for c in choices], validators=field_validators)
                
                if field_obj:
                    setattr(GeneratedForm, field_def.field_name, field_obj)
        
        # Add submit button
        GeneratedForm.submit = SubmitField('Log Activity')
        
        return GeneratedForm()

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

class TrackingFieldForm(FlaskForm):
    """Form for managing individual tracking fields"""
    field_name = StringField('Field Name (Internal ID)', validators=[DataRequired(), Length(min=1, max=200)])
    field_label = StringField('Field Label (Display Name)', validators=[DataRequired(), Length(min=1, max=200)])
    field_type = SelectField('Field Type', choices=[
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('select', 'Dropdown')
    ], validators=[DataRequired()])
    is_required = BooleanField('Required Field')
    order = IntegerField('Display Order', validators=[Optional()])
    submit = SubmitField('Save Field')

