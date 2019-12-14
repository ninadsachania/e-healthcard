from flask import Flask, render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

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

        if len(form.username.data) == 10:
            user = User.query.filter_by(phone_number=form.username.data).first()
        else:
            user = User.query.filter_by(email=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # 'netloc' is the first level domain (www.example.com)
            return redirect(url_for('index')) 
        return redirect(next_page)

    return render_template('login.html', form=form, title="Login")

@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Homepage')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            firstname=form.firstname.data,
            middlename=form.middlename.data,
            lastname=form.middlename.data,
            email=form.email.data,
            aadhar_card=form.aadhar_card.data,
            phone_number=form.phone_number.data,
            address=form.address.data
        )

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user')
        return redirect(url_for('index'))

    return render_template('register.html', form=form, title="Registration")

if __name__ == '__main__':
    app.run(debug=True)