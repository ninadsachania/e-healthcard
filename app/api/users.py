from app.api import bp
from flask import request, jsonify, g, url_for, render_template
from app.models import User, Metadata, StaticInformation, DynamicInformation
from app import db, app
from app.api.errors import error_response, bad_request
from app.api.auth import token_auth
from qrcode import update_qrcode
from app.email import send_password_reset_email
from qrcode import qrcode_data, make_qrcode, qrcode_path
from datetime import datetime
from app.email import send_password_reset_email, send_email


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_user():
    user = g.current_user
    if user:
        return jsonify(user.to_dict())

    return error_response(404, "User not found")


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}

    user = User(
        firstname=data['firstname'],
        middlename=data['middlename'],
        lastname=data['lastname'],
        email=data['email'],
        aadhar_card=data['aadhar_card'],
        phone_number=data['phone_number'],
        address=data['address']
    )

    u = User.query.filter_by(email=data['email']).first()

    if u is not None:
        return error_response(409, "Sorry! This email is already in use")

    u = User.query.filter_by(phone_number=data['phone_number']).first()

    if u is not None:
        return error_response(409, 'Sorry! This phone number is already in use.')

    u = User.query.filter_by(aadhar_card=data['aadhar_card']).first()

    if u is not None:
        return error_response(409, 'Sorry! This aadhar number is already in use.')

    user.set_password(data['password'])
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

    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user')
    return response


@bp.route('/users', methods=['PUT'])
@token_auth.login_required
def update_user():
    # TODO: Make it more robust and clean it up.
    user = User.query.filter_by(id=g.current_user.id).first()
    data = request.get_json() or {}

    if 'email' in data or 'aadhar_card' in data or 'phone_number' in data:
        return bad_request("Can't change email, aadhar_card and phone_number.")

    unknown_keys = []

    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
        else:
            # TODO: Return a different error code when an unknown attribute is present
            unknown_keys.append(key)
            return bad_request("Unknown key: {}".format(key))

    info = StaticInformation.query.filter_by(user_id=user.id).first()
    if info:
        update_qrcode(user.id)
    db.session.commit()
    return jsonify(g.current_user.to_dict())


@bp.route('/users/all', methods=['GET'])
@token_auth.login_required
def users():
    users = User.query.all()
    data = []

    for user in users:
        data.append(user.to_dict())

    return jsonify(data)


@bp.route('/users/static_information', methods=['GET'])
@token_auth.login_required
def static_information():
    user = g.current_user

    info = StaticInformation.query.filter_by(user_id=user.id).first()
    if info is None:
        return error_response(204, message="No data found")

    return jsonify(info.to_dict())


@bp.route('/users/static_information', methods=['PUT'])
@token_auth.login_required
def update_static_information():
    user = g.current_user
    static_info = StaticInformation.query.filter_by(user_id=user.id).first()
    data = request.get_json() or {}

    if not static_info:
        info = StaticInformation(
            user_id=user.id,
            gender=data['gender'],
            dob=datetime.strptime(data['dob'], '%Y-%m-%d'),
            emergency_contact=data['emergency_contact'],
            height=data['height'],
            weight=data['weight'],
            bloodgroup=data['bloodgroup'],
            allergies=data['allergies'],
            current_medication=data['current_medication']
        )

        db.session.add(info)
        db.session.commit()

        return jsonify({'message': 'Static information has been created.'})

    for key, value in data.items():
        if hasattr(static_info, key):
            if key == 'dob':
                date = datetime.strptime(value, '%Y-%m-%d')
                setattr(static_info, key, date)
            else:
                setattr(static_info, key, value)
        else:
            return bad_request("Unknown key: {}".format(key))

    db.session.commit()
    update_qrcode(user.id)
    return jsonify(static_info.to_dict())

@bp.route('/users/dynamic_information', methods=['GET'])
@token_auth.login_required
def dynamic_information():
    user = g.current_user

    records = DynamicInformation.query.filter_by(user_id=user.id).all()
    if not records:
        return error_response(204, "No data found")

    data = [record.to_dict() for record in records]

    return jsonify(data)


@bp.route('/users/changepw', methods=['POST'])
@token_auth.login_required
def changepw():
    user = g.current_user
    data = request.get_json() or {}

    if 'current_password' not in data or 'new_password' not in data:
        return error_response(400, "'current_password' and 'new_password' fields are required.")

    if user.check_password(data['current_password']):
        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({"message": "Password successfully changed."})

    return error_response(400, "Current password incorrect. Please try again.")


@bp.route('/users/reset_password_request', methods=['POST'])
def reset_password_request():
    data = request.get_json() or {}

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return error_response(400, "Sorry! Email '{}' not found.".format(data['email']))

    send_password_reset_email(user)
    return jsonify({'message': 'Check your email for instructions to reset your password.'})


@bp.route('/users/qrcode', methods=['POST'])
@token_auth.login_required
def qrcode():
    user = g.current_user
    static_info = StaticInformation.query.filter_by(user_id=user.id).first()

    if not static_info:
        return error_response(400, 'To generate a QR code first fill out your static information.')

    path = qrcode_path(qrcode_data(user, static_info))

    return jsonify({'path': path[1:]})
