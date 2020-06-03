#! /usr/bin/env python3

import serial
import webbrowser
import sys

# url where the data will go
domain = 'https://68.183.87.252'
url = '{}/doctor/add_record/rfid/'.format(domain)

if sys.platform == 'win32':
    port = 'COM10'
elif sys.platform == 'linux':
    port = '/dev/ttyACM0'

baudrate = 9600

try:
    ser = serial.Serial(port, baudrate, timeout=1)  # open serial port
except Exception as e:
    sys.stderr.write(str(e) + '\n')
    sys.exit(1)  # cannot open the port

while True:
    rfid_uid = ''

    # I don't know if these help
    ser.reset_output_buffer()
    ser.reset_input_buffer()

    print('Please keep your card nearby: ')

    while True:
        line = ser.readline().decode('utf-8')
        if line != '':
            rfid_uid = line.strip()  # remove trailing whitespaces and newline
            break

    print('\nUID: {}'.format(rfid_uid))
    answer = input('Is this okay? (y/n): ')

    if answer.lower() == 'y':
        # open the link in the browser
        webbrowser.open('{}?rfid={}'.format(url, rfid_uid))

    print()
