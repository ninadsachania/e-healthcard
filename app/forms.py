from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField, TelField


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login In')


class RegistrationForm(FlaskForm):
    name = StringField(u'Username:', validators=[DataRequired()])
    aadhar_number = IntegerField(u'Aadhar Card:', validators=[DataRequired()])
    address = TextAreaField(u'Address:', validators=[DataRequired()])
    phone_number = TelField(u'Phone Number:', validators=[DataRequired()])
    email = EmailField(u'Email:', validators=[DataRequired()])
    submit = SubmitField(u'Reigster')
