from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, \
    SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from wtforms.fields.html5 import EmailField, TelField, DateField
from app.models import User
from app.verify import verify_aadhar_card


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login In')


class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname:', validators=[DataRequired()])
    middlename = StringField('Middlename:', validators=[DataRequired()])
    lastname = StringField('Lastname:', validators=[DataRequired()])
    aadhar_card = StringField('Aadhar Card:', validators=[DataRequired()])
    phone_number = TelField('Phone Number:', validators=[DataRequired()])
    email = EmailField('Email:', validators=[DataRequired(), Email()])
    address = TextAreaField('Address:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password:', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Sorry! This email is already in use')

    def validate_aadhar_card(self, aadhar_card):
        user = User.query.filter_by(aadhar_card=aadhar_card.data).first()
        if user is not None:
            raise ValidationError('''
        Sorry! This aadhar number is already in use.''')

        if not verify_aadhar_card(aadhar_card):
            raise ValidationError('''
        Sorry! This aadhar number is not valid.''')

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user is not None:
            raise ValidationError('Sorry! This phone number is already in use.')


class EditProfileForm(FlaskForm):
    firstname = StringField('Firstname:', validators=[DataRequired()])
    middlename = StringField('Middlename:', validators=[DataRequired()])
    lastname = StringField('Lastname:', validators=[DataRequired()])
    aadhar_card = StringField('Aadhar Card:', validators=[DataRequired()])
    phone_number = TelField('Phone Number:', validators=[DataRequired()])
    email = EmailField('Email:', validators=[DataRequired(), Email()])
    address = TextAreaField('Address:', validators=[DataRequired()])
    submit = SubmitField('Update')


class PasswordResetForm(FlaskForm):
    current_password = PasswordField('Current Password:', validators=[
        DataRequired()])
    new_password = PasswordField('New Password:', validators=[DataRequired()])
    submit = SubmitField('Change')


class StaticInformationForm(FlaskForm):
    gender = SelectField('Gender:', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    dob = DateField('Date of Birth:', validators=[DataRequired()])
    emergency_contact = StringField('Emergency Contact:', validators=[
        DataRequired(), Length(min=10, max=10, message="Length should be 10")])
    height = StringField('Height (in cm):')
    weight = StringField('Weight (in kg):')
    bloodgroup = StringField('Bloodgroup:', validators=[DataRequired()])
    allergies = TextAreaField('Allergies:')
    current_medication = TextAreaField('Current Medication:')
    submit = SubmitField('Update')


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Enter new password:', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change your password')


class DoctorRegistrationForm(FlaskForm):
    hospital_name = StringField('Hospital name:', validators=[DataRequired()])
    designation = StringField('Designation:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class GetPatientInformationForm(FlaskForm):
    id = StringField('ID of the patient:', validators=[DataRequired()])
    submit = SubmitField('View')