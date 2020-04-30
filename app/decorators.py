from app.models import Doctor
from flask_login import current_user
from flask import render_template, flash, redirect, url_for
from functools import wraps


def is_verified_doctor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        is_verified = doctor.verified

        if not is_verified:
            return render_template('not_verified.html')

        return f(*args, **kwargs)
    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_administrator:
            flash('You are not an admin.')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function


def check_email_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


def is_doctor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Doctor.query.filter_by(user_id=current_user.id).first():
            flash("You do not have permission to view that page", "warning")
            return redirect(url_for('for_doctors'))

        return f(*args, **kwargs)
    return decorated_function
