from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo
from wtforms.fields.html5 import EmailField, TelField


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
    email = EmailField('Email:', validators=[DataRequired()])
    address = TextAreaField('Address:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    