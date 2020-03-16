from app.api import bp
from flask import request, jsonify, g, url_for
from app.models import User, Metadata, StaticInformation, DynamicInformation
from app import db
from app.api.errors import error_response, bad_request
from app.api.auth import token_auth


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
            #TODO: Return a different error code when an unknown attribute is present
            unknown_keys.append(key)
            return bad_request("Unknown key: {}".format(key))

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


@bp.route('/users/dynamic_information')
@token_auth.login_required
def dynamic_information():
    user = g.current_user

    records = DynamicInformation.query.filter_by(user_id=user.id).all()
    if not records:
        return error_response(204, "No data found")

    data = [record.to_dict() for record in records]

    return jsonify(data)
