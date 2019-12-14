from flask import Flask, render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', title="Homepage")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html', form=form, title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        return redirect(url_for('index'))

    return render_template('register.html', form=form, title="Registration")

if __name__ == '__main__':
    app.run(debug=True)