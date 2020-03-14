from app.api import bp
from flask import request, jsonify, g
from app.models import User, Metadata, StaticInformation, DynamicInformation
from app import db
from app.api.errors import bad_request, error_response
from app.api.auth import token_auth


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_user():
    user = g.current_user
    if user:
        return jsonify(user.to_dict())

    return error_response(404, "User not found")


@bp.route('/users/', methods=['POST'])
def create_user():
    data = request.get_json()

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
        return error_response(409, "Email already exists")

    u = User.query.filter_by(phone_number=data['phone_number']).first()

    if u is not None:
        return error_response(409, 'Phone number already exists')

    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    m = Metadata(
        user_id=user.id
    )
    db.session.add(m)
    db.session.commit()

    data = {
        'status': 200,
        'message': 'User registered successfully!'
    }

    return jsonify(data)


@bp.route('/users/all', methods=['GET'])
def users():
    users = User.query.all()
    data = []

    for user in users:
        data.append(user.to_dict())

    return jsonify(data)


@bp.route('/users/static_information')
@token_auth.login_required
def static_information():
    user = g.current_user

    if user is None:
        return error_response(404, "User not found")

    info = StaticInformation.query.filter_by(user_id=user.id).first()

    if info is None:
        return error_response(204, message="No data found")

    return jsonify(info.to_dict())


@bp.route('/users/dynamic_information')
@token_auth.login_required
def dynamic_information():
    user = g.current_user

    records = DynamicInformation.query.filter_by(user_id=user.id).first()
    if records is None:
        return error_response(204, "No data found")

    data = []

    for record in records:
        data.append(record.to_dict())

    return jsonify(data)
