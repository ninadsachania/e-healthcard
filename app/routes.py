from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PasswordResetForm
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


@app.route('/user/profile')
@login_required
def account():
    return render_template('account.html', title='Profile')


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
            lastname=form.lastname.data,
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


@app.route('/user/edit', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        # TODO: Inefficient?
        current_user.firstname = form.firstname.data
        current_user.middlename = form.middlename.data
        current_user.lastname = form.lastname.data
        current_user.aadhar_card = form.aadhar_card.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Your changes have been updated!')

        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.middlename.data = current_user.middlename
        form.lastname.data = current_user.lastname
        form.aadhar_card.data = current_user.aadhar_card
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
        form.address.data = current_user.address

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/user/changepw', methods=['POST', 'GET'])
def change_password():
    form = PasswordResetForm()

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Congratulations! Password successfully changed.')
            return redirect(url_for('change_password'))

        flash('Current password incorrent. Please try again.')
        return redirect(url_for('change_password'))

    return render_template('change_password.html', title="Change Password", form=form)


if __name__ == '__main__':
    app.run(debug=True)
