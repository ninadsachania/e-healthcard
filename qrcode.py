#! /usr/bin/env python3

import os
import json
import segno


def make_qrcode(information: {}):
    qrcode = segno.make(str(json.dumps(information)), micro=False)
    path = os.path.join(
        os.path.abspath(os.getcwd()),
        'app',
        'static',
        'qrcodes',
        '{}.png'.format(information['id'])
    )

    # Check to see if QR code has already been generated
    if not os.path.exists(path):
        qrcode.save(path, scale=5)


def qrcode_path(information: {}):
    make_qrcode(information)
    path = '/static/qrcodes/{}.png'.format(information['id'])
    return path
