from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    PasswordResetForm, StaticInformationForm, ResetPasswordRequestForm, \
    ResetPasswordForm, DoctorRegistrationForm, GetPatientInformationForm, \
    AddDynamicInformationForm
from app.models import User, StaticInformation, Metadata, Doctor, DynamicInformation
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from functools import wraps


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

        m = Metadata.query.filter_by(id=user.id).first()
        m.last_logged_in = datetime.utcnow()

        db.session.add(m)
        db.session.commit()

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
        db.session.flush()

        m = Metadata(
            user_id=user.id
        )
        db.session.add(m)
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

        m = Metadata.query.filter_by(id=current_user.id).first()
        m.last_modified_on = datetime.utcnow()

        db.session.add(m)
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
@login_required
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


@app.route('/user/information')
@login_required
def medical_information():
    return render_template('medical_information.html', title='Medical Information')


@app.route('/user/static_info')
@login_required
def static_info():
    info = StaticInformation.query.filter_by(id=current_user.id).first()
    return render_template('static_info.html', title='Static Information', info=info)


@app.route('/user/dynamic_info')
def dynamic_info():
    dynamic_records = DynamicInformation.query.filter_by(user_id=current_user.id).all()

    records = []

    for record in dynamic_records:
        doctor = Doctor.query.filter_by(doctor_id=record.doctor_id).first()

        user = User.query.filter_by(id=doctor.user_id).first()

        records.append({
            'id': record.id,
            'doctor_name': "Dr, {} {}, {}".format(user.firstname, user.lastname, doctor.designation),
            'hospital_name': doctor.hospital_name,
            'symptoms': record.symptoms,
            'diagnosis': record.diagnosis,
            'prescribed_medication': record.prescribed_medication,
            'notes': record.notes,
            'date_created': record.date_created
        })

    return render_template('dynamic_info.html', title='Dynamic Information', records=records)


@app.route('/user/edit_static_info', methods=['POST', 'GET'])
@login_required
def edit_static_info():
    # TODO: Cleanup & better representation of data
    form = StaticInformationForm()

    if form.validate_on_submit():
        current_info = StaticInformation.query.filter_by(id=current_user.id).first()

        if current_info:
            current_info.dob = form.dob.data
            current_info.gender = form.gender.data
            current_info.emergency_contact = form.emergency_contact.data
            current_info.height = form.height.data
            current_info.weight = form.weight.data
            current_info.bloodgroup = form.bloodgroup.data
            current_info.allergies = form.allergies.data
            current_info.current_medication = form.current_medication.data

            m = Metadata.query.filter_by(id=current_user.id).first()
            m.static_info_last_modified_on = datetime.utcnow()

            db.session.add(m)
            db.session.commit()

            flash('Information updated!')
        else:
            info = StaticInformation(
                user_id=current_user.id,
                gender=form.gender.data,
                dob=form.dob.data,
                emergency_contact=form.emergency_contact.data,
                height=form.height.data,
                weight=form.weight.data,
                bloodgroup=form.bloodgroup.data,
                allergies=form.allergies.data,
                current_medication=form.current_medication.data
            )
            m = Metadata.query.filter_by(id=current_user.id).first()
            m.static_info_last_modified_on = datetime.utcnow()

            db.session.add(info)
            db.session.commit()

            flash('Information created!')

        return redirect(url_for('static_info'))
    elif request.method == 'GET':
        current_info = StaticInformation.query.filter_by(id=current_user.id).first()

        if current_info:
            form.dob.data = current_info.dob
            form.gender.data = current_info.gender
            form.emergency_contact.data = current_info.emergency_contact
            form.height.data = current_info.height
            form.weight.data = current_info.weight
            form.bloodgroup.data = current_info.bloodgroup
            form.allergies.data = current_info.allergies
            form.current_medication.data = current_info.current_medication

    return render_template('edit_static_info.html', title='Edit Static Information', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash('DEBUGGING: Correct email!')
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form, title='Reset Password')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('login'))

    return render_template('reset_password_form.html', form=form, title='Reset Password')


@app.route('/contact')
def contact():
    return render_template('contact_us.html')


@app.route('/faqs')
def faqs():
    return render_template('faqs.html')


@app.route('/about')
def about():
    return render_template('about_us.html')


# Doctor
def is_doctor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Doctor.query.filter_by(user_id=current_user.id).first():
            flash("You do not have permission to view that page", "warning")
            return redirect(url_for('for_doctors'))

        return f(*args, **kwargs)
    return decorated_function


@app.route('/for_doctors')
@app.route('/doctor/')
def for_doctors():
    # only want to show some links if the user is a doctor
    is_doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    return render_template('for_doctors.html', is_doctor=is_doctor)


@app.route('/doctor/register', methods=["GET", "POST"])
@login_required
def doctor_registration():
    # check if the doctor is already registered
    if Doctor.query.filter_by(user_id=current_user.id).first():
        flash('Doctor is already registered!')
        return redirect(url_for('for_doctors'))

    form = DoctorRegistrationForm()

    if form.validate_on_submit():
        doctor = Doctor(
            user_id=current_user.id,
            hospital_name=form.hospital_name.data,
            designation=form.designation.data
        )

        db.session.add(doctor)
        db.session.commit()

        flash("Congratulations! You're now registered")
        return redirect(url_for('for_doctors'))

    return render_template('doctor_registration.html', form=form)


@app.route('/doctor/profile')
@login_required
@is_doctor
def doctor_profile():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    data = {
        'hospital_name': doctor.hospital_name,
        'designation': doctor.designation,
        'is_verified': doctor.verified
    }

    return render_template('doctor_profile.html', data=data)


def is_verified_doctor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        is_verified = doctor.verified

        if not is_verified:
            return render_template('not_verified.html')

        return f(*args, **kwargs)
    return decorated_function


@app.route('/doctor/add_record', methods=['GET', 'POST'])
@login_required
@is_doctor
@is_verified_doctor
def add_record():
    form = AddDynamicInformationForm()

    doctor_id = Doctor.query.filter_by(user_id=current_user.id).first().doctor_id
    form.doctor_id.data = doctor_id

    if form.validate_on_submit():
        user = User.query.filter_by(id=form.user_id.data).first()

        if user:
            # The user does exist.

            dynamic_info = DynamicInformation(
                user_id=form.user_id.data,
                doctor_id=form.doctor_id.data,
                symptoms=form.symptoms.data,
                diagnosis=form.diagnosis.data,
                prescribed_medication=form.prescribed_medication.data,
                notes=form.notes.data
            )

            # Add the data to the table
            db.session.add(dynamic_info)
            db.session.commit()

            flash("Data successfully added.")
            return redirect(url_for('add_record'))

        elif not user:
            flash("User ID: {} does not exist".format(form.user_id.data))

    return render_template('add_record.html', form=form)


@app.route('/doctor/static_record', methods=['GET', 'POST'])
@login_required
@is_doctor
@is_verified_doctor
def static_record():
    ''' This route is where doctors will go to view the static record of a patient. '''
    form = GetPatientInformationForm()

    user_data = None
    static_data = None

    if form.validate_on_submit():
        user_data = User.query.filter_by(id=form.id.data).first()

        if user_data:
            # The user exists. Now check for their 'static_data'
            static_data = StaticInformation.query.filter_by(id=user_data.id).first()
            if static_data:
                return render_template('view_static_record.html', static_data=static_data, data=user_data, form=form)

            # They have no 'static_data'
            return render_template('view_static_record.html', static_data=static_data, data=user_data, form=form)

        flash('This user does not exist')

    return render_template('view_static_record.html', title='View Static Record', form=form)


@app.route('/doctor/dynamic_records', methods=['GET', 'POST'])
@login_required
@is_doctor
@is_verified_doctor
def dynamic_records():
    form = GetPatientInformationForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()

        if user:
            doctor_id = Doctor.query.filter_by(user_id=current_user.id).first().doctor_id

            records = DynamicInformation.query.filter(
                DynamicInformation.user_id == form.id.data).filter(
                    DynamicInformation.doctor_id == doctor_id).all()

            return render_template('view_dynamic_records.html', title='View Dynamic Records', user=user, form=form, records=records)

        flash('User does not exist.')

    return render_template('view_dynamic_records.html', title='View Dynamic Records', form=form)


@app.route('/doctor/view_all_records')
@login_required
@is_doctor
@is_verified_doctor
def view_all_records():
    doctor_id = Doctor.query.filter_by(user_id=current_user.id).first().doctor_id
    records = DynamicInformation.query.filter_by(doctor_id=doctor_id).all()

    return render_template('view_all_dynamic_records.html', records=records)


if __name__ == '__main__':
    app.run(debug=True)
