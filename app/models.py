from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
import jwt
from time import time
import os
import base64
from itsdangerous import URLSafeTimedSerializer


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    middlename = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    aadhar_card = db.Column(db.String(12), index=True, unique=True)
    phone_number = db.Column(db.String(10), index=True, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(512))
    rfid = db.Column(db.String(7), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    is_token_valid = db.Column(db.Boolean, default=False)
    is_administrator = db.Column(db.Boolean, default=False)

    def get_token(self):
        if self.is_token_valid:
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.is_token_valid = True
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.is_token_valid = False

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or not user.is_token_valid:
            return None
        return user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.email)

    def __str__(self):
        return '{}'.format(self.email)

    def avatar(self, size=128):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        url = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'
        return url.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'],
            'HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def generate_confirmation_token(self):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt=app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def confirm_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
        except:
            return False
        return email

    def to_dict(self):
        data = {
            'id': self.id,
            'firstname': self.firstname,
            'middlename': self.middlename,
            'lastname': self.lastname,
            'email': self.email,
            'aadhar_card': self.aadhar_card,
            'phone_number': self.phone_number,
            'address': self.address,
            'rfid': self.rfid,
            'avatar': self.avatar()
        }

        return data


class StaticInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    gender = db.Column(db.String(16), nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    emergency_contact = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    bloodgroup = db.Column(db.String(3), nullable=False)
    allergies = db.Column(db.String(512), nullable=True)
    current_medication = db.Column(db.String(512), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "gender": self.gender,
            "dob": self.dob,
            "emergency_contact": self.emergency_contact,
            "height": self.height,
            "weight": self.weight,
            "bloodgroup": self.bloodgroup,
            "allergies": self.allergies,
            "current_medication": self.current_medication
        }


class DynamicInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    symptoms = db.Column(db.String(512), nullable=True)
    diagnosis = db.Column(db.String(512), nullable=False)
    prescribed_medication = db.Column(db.String(512), nullable=False)
    notes = db.Column(db.String(1024), nullable=True)
    previous_case_id = db.Column(db.Integer, default=0, nullable=True)
    next_case_id = db.Column(db.Integer, default=0, nullable=True)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "symptoms": self.symptoms,
            "diagnosis": self.diagnosis,
            "prescribed_medication": self.prescribed_medication,
            "notes": self.notes,
            "previous_case_id": self.previous_case_id,
            "next_case_id": self.next_case_id,
            "date_created": self.date_created
        }


class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    last_logged_in = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    last_modified_on = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    static_info_last_modified_on = db.Column(
        db.DateTime,
        nullable=True,
    )


class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False, unique=True)
    hospital_name = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(256), nullable=False)
    verified = db.Column(db.Boolean, default=False)
