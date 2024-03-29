from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    PasswordResetForm, StaticInformationForm, ResetPasswordRequestForm, \
    ResetPasswordForm, DoctorRegistrationForm, GetPatientInformationForm, \
    AddDynamicInformationForm
from app.models import User, StaticInformation, Metadata, Doctor, \
    DynamicInformation
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email, send_email
from qrcode import qrcode_path, update_qrcode, qrcode_data, make_qrcode
from app.decorators import is_verified_doctor, is_admin, is_doctor, \
    check_email_confirmed


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
            return redirect(url_for('unconfirmed'))
        return redirect(next_page)

    return render_template('login.html', form=form, title="Login")


@app.route('/user/profile')
@login_required
@check_email_confirmed
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

        token = user.generate_confirmation_token()
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email/activate_account.html', confirm_url=confirm_url)
        text_body = render_template('email/activate_account.txt', confirm_url=confirm_url)
        subject = 'Please confirm your email'
        send_email(subject, app.config['ADMINS'][0], [user.email], text_body, html)

        flash('Congratulations, you are now a registered user')
        return redirect(url_for('unconfirmed'))

    return render_template('register.html', form=form, title="Registration")


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = User.confirm_token(token)
    except:
        flash('The confirmation link is invalid or expired.', 'danger')

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()

        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('index'))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('index'))

    flash('Please confirm your account.', 'warning')
    return render_template('unconfirmed.html')


@app.route('/resend')
@login_required
def resend_email_confirmation():
    token = current_user.generate_confirmation_token()
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('email/activate_account.html', confirm_url=confirm_url)
    text_body = render_template('email/activate_account.txt', confirm_url=confirm_url)
    subject = 'Please confirm your email'
    send_email(subject, app.config['ADMINS'][0], [current_user.email], text_body, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))


@app.route('/user/edit', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        # TODO: Inefficient?
        current_user.firstname = form.firstname.data
        current_user.middlename = form.middlename.data
        current_user.lastname = form.lastname.data
        current_user.address = form.address.data

        m = Metadata.query.filter_by(id=current_user.id).first()
        m.last_modified_on = datetime.utcnow()

        db.session.add(m)
        db.session.commit()

        # Update the QR code of the user
        info = StaticInformation.query.filter_by(user_id=current_user.id).first()
        if info:
            update_qrcode(current_user.id)

        flash('Your changes have been updated!')

        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.middlename.data = current_user.middlename
        form.lastname.data = current_user.lastname
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
    info = StaticInformation.query.filter_by(user_id=current_user.id).first()
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
        current_info = StaticInformation.query.filter_by(user_id=current_user.id).first()

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

            # Update the QR code of the user
            update_qrcode(current_user.id)

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
        current_info = StaticInformation.query.filter_by(user_id=current_user.id).first()

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
    return render_template('contact_us.html', title='Contact Us')


@app.route('/faqs')
def faqs():
    return render_template('faqs.html', title='FAQs')


@app.route('/about')
def about():
    return render_template('about_us.html', title='About Us')


@app.route('/user/qrcode')
@login_required
def qrcode():
    user = User.query.filter_by(id=current_user.id).first()
    static_info = StaticInformation.query.filter_by(
        user_id=current_user.id).first()

    if not static_info:
        flash('You need to enter some basic information about you before you can generate a QR code.')
        return redirect(url_for('edit_static_info'))

    '''
    This generates a QR code containing the following information:
        * Name (Firstname + Middlename + Lastname)
        * Phone Number
        * Emergency Mobile Number
        * Address
        * Blood group
    '''

    information = qrcode_data(user, static_info)

    path = qrcode_path(information)
    return render_template('qrcode.html', path=path, title='QR Code')


# Doctor
@app.route('/for_doctors')
@app.route('/doctor/')
def for_doctors():
    # only want to show some links if the user is a doctor
    is_doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    return render_template('for_doctors.html', is_doctor=is_doctor, title='Doctor')


@app.route('/doctor/register', methods=["GET", "POST"])
@login_required
def doctor_registration():
    # check if the doctor is already registered
    if Doctor.query.filter_by(user_id=current_user.id).first():
        flash('You are already registered as a doctor.')
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

    return render_template('doctor_registration.html', form=form, title='Doctor Registration')


@app.route('/doctor/profile')
@login_required
@is_doctor
def doctor_profile():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    data = {
        'doctor_id': doctor.doctor_id,
        'hospital_name': doctor.hospital_name,
        'designation': doctor.designation,
        'is_verified': doctor.verified
    }

    return render_template('doctor_profile.html', data=data, title="Doctor's Profile")


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

    return render_template('add_record.html', form=form, title='New Record')


@app.route('/doctor/add_record/rfid/', methods=['GET', 'POST'])
@login_required
@is_doctor
@is_verified_doctor
def add_record_from_rfid():
    # TODO: Refact, test & cleanup
    form = AddDynamicInformationForm()

    rfid = request.args.get('rfid')

    if rfid is not None:
        user = User.query.filter_by(rfid=rfid).first()

        if user:
            doctor_id = Doctor.query.filter_by(user_id=current_user.id).first().doctor_id

            form.user_id.data = user.id
            form.doctor_id.data = doctor_id
        elif not user:
            flash('Not a valid RFID')

    if form.validate_on_submit():
        dynamic_info = DynamicInformation(
                user_id=form.user_id.data,
                doctor_id=form.doctor_id.data,
                symptoms=form.symptoms.data,
                diagnosis=form.diagnosis.data,
                prescribed_medication=form.prescribed_medication.data,
                notes=form.notes.data
        )

        db.session.add(dynamic_info)
        db.session.commit()

    return render_template('add_record_rfid.html', form=form, title='[RFID] New Record')

@app.route('/doctor/static_record', methods=['GET', 'POST'])
@login_required
@is_doctor
@is_verified_doctor
def static_record():
    ''' This route is where doctors will go to view the static record of a patient. '''
    title = 'View Static Information'
    form = GetPatientInformationForm()

    user_data = None
    static_data = None

    if form.validate_on_submit():
        user_data = User.query.filter_by(id=form.id.data).first()

        if user_data:
            # The user exists. Now check for their 'static_data'
            static_data = StaticInformation.query.filter_by(user_id=user_data.id).first()
            if static_data:
                return render_template(
                    'view_static_record.html',
                    static_data=static_data,
                    data=user_data,
                    form=form,
                    title=title
                )

            # They have no 'static_data'
            return render_template(
                'view_static_record.html',
                static_data=static_data,
                data=user_data,
                form=form,
                title=title
            )

        flash('This user does not exist')

    return render_template('view_static_record.html', form=form, title=title)


@app.route('/doctor/dynamic_records', methods=['GET', 'POST'])
@login_required
@is_doctor
@is_verified_doctor
def dynamic_records():
    form = GetPatientInformationForm()
    title = 'View Dynamic Records'

    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()

        if user:
            doctor_id = Doctor.query.filter_by(user_id=current_user.id).first().doctor_id

            records = DynamicInformation.query.filter(
                DynamicInformation.user_id == form.id.data).filter(
                    DynamicInformation.doctor_id == doctor_id).all()

            return render_template(
                'view_dynamic_records.html',
                user=user,
                form=form,
                records=records,
                title=title,
            )

        flash('User does not exist.')

    return render_template('view_dynamic_records.html', form=form, title=title)


@app.route('/doctor/view_all_records')
@login_required
@is_doctor
@is_verified_doctor
def view_all_records():
    doctor_id = Doctor.query.filter_by(user_id=current_user.id).first().doctor_id
    records = DynamicInformation.query.filter_by(doctor_id=doctor_id).all()

    return render_template(
        'view_all_dynamic_records.html',
        records=records,
        title='All Dynamic Records'
    )


@app.route('/admin')
@login_required
@check_email_confirmed
@is_admin
def admin():
    doctors = Doctor.query.all()
    return render_template('admin.html', title='Admin', doctors=doctors)


@app.route('/admin/verify', methods=['POST'])
@login_required
@check_email_confirmed
@is_admin
def verify_doctors():
    args = request.get_json()
    doctor = Doctor.query.filter_by(doctor_id=args['id']).first()
    doctor.verified = not doctor.verified

    db.session.add(doctor)
    db.session.commit()
    return jsonify({'message': 'Successfully updated', 'account_state': str(doctor.verified)})


if __name__ == '__main__':
    app.run(debug=True)
