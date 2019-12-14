from flask import Flask, render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, RegistrationForm

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', title="Homepage")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        flash('Login required for user: {}, remember_me: {}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))

    return render_template('login.html', form=form, title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        return redirect(url_for('index'))

    return render_template('register.html', form=form, title="Registration")

if __name__ == '__main__':
    app.run(debug=True)