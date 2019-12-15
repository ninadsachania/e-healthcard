from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


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
    confirmed = db.Column(db.Boolean, default=True)
    address = db.Column(db.String(512))
    password_hash = db.Column(db.String(128))

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
