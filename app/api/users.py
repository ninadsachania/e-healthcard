from app.api import bp
from flask import request, jsonify
from app.models import User, Metadata
from app import db
from app.api.errors import bad_request, error_response


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id).first()

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


@bp.route('/users/', methods=['GET'])
def users():
    users = User.query.all()
    data = []

    for user in users:
        data.append(user.to_dict())

    return jsonify(data)
