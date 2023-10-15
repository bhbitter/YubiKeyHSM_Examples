#!/usr/bin/env python
import argparse
import sys 
import os

from yubihsm import YubiHsm
from yubihsm.objects import AsymmetricKey
from yubihsm import exceptions

parser = argparse.ArgumentParser(
                    prog='sign',
                    description='Create a signature of a file')

parser.add_argument('-k', '--authkey', default=1, type=int, help='Authentication Key ID to use. (Default: 1)')
parser.add_argument('id', type=int, help='ID of signing key to use.')
parser.add_argument('filename', help='File to sign.')
parser.add_argument('password', help='Authentication key password used to unlock the signing key on the HSM')

args = parser.parse_args()


if not os.path.isfile(args.filename):
    print('Error: File not found.')
    sys.exit(-1)
    
# Read in the file
with open(args.filename, 'rb') as fd:
    data = fd.read()

# Connect to the HSM via the USB connector
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey, args.password)

    key = AsymmetricKey(session, args.id)

    # Create signature of the data
    signature = key.sign_ecdsa(data)

    # Clean up:
    session.close()
    hsm.close()
except exceptions.YubiHsmConnectionError as e:
    print(f'ERROR: Failed to connect to HSM over USB. [{e}]')
    sys.exit(-2)
except exceptions.YubiHsmDeviceError as e:
    print(f'ERROR: Signing failed. [{e}]')
    sys.exit(-3)

# Write the signature to a file
with open(args.filename + '.sig', 'wb') as fd:
    fd.write(signature)

sys.exit(0)
