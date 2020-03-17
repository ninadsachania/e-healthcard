#! /usr/bin/env python3

import os
import json
import segno
from app.models import User, StaticInformation

def update_qrcode(user_id):
    user = User.query.filter_by(id=user_id).first()
    info = StaticInformation.query.filter_by(user_id=user.id).first()

    return make_qrcode(qrcode_data(user, info))

# Helper function to make QR code
def qrcode_data(user, static_info):
    ''' Returns the data to be stored in QR code. '''
    return {
        'id': user.id,
        'name': '{} {} {}'.format(user.firstname, user.middlename, user.lastname),
        'phone_number': user.phone_number,
        'emergency_contact_number': static_info.emergency_contact,
        'address': user.address,
        'boodgroup': static_info.bloodgroup
    }


def make_qrcode(information: {}):
    qrcode = segno.make(str(json.dumps(information)), micro=False)
    path = os.path.join(
        os.path.abspath(os.getcwd()),
        'app',
        'static',
        'qrcodes',
        '{}.png'.format(information['id'])
    )

    return qrcode.save(path, scale=5)


def qrcode_path(information: {}):
    # Check to see if QR code has already been generated
    path = os.path.join(
        os.path.abspath(os.getcwd()),
        'app',
        'static',
        'qrcodes',
        '{}.png'.format(information['id'])
    )

    if not os.path.exists(path):
        make_qrcode(information)

    path = '/static/qrcodes/{}.png'.format(information['id'])
    return path
