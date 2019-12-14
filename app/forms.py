from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from wtforms.fields.html5 import EmailField, TelField
from app.models import User


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

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user is not None:
            raise ValidationError('Sorry! This phone number is already in use.')
