#!/usr/bin/env python
import argparse
import sys

from yubihsm import YubiHsm
from yubihsm.defs import OBJECT
from yubihsm import exceptions

from cryptography.hazmat.primitives import serialization

def save_pub_key(key):
    # pub_key is a cryptography.io ec.PublicKey, see https://cryptography.io
    pub_key = key.get_public_key()
    
    pub_key_str = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('ascii')

    print(pub_key_str)
 
    # Write the public key to a file:
    with open(f'./public_key_{key.id}.pem', 'w') as fd:
        fd.write(pub_key_str)

parser = argparse.ArgumentParser(
                    prog='get_pub_keys',
                    description='Retrieve and print out the public asymmetric keys stored in the HSM.')

parser.add_argument('-k', '--authkey', default=1, type=int, help='Authentication Key ID to use. Default is 1')
parser.add_argument('-p', '--password', required=True, help='Password used to unlock the RSA key on the HSM')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey, args.password)

    objs = session.list_objects()

    key = None

    for obj in objs:
        # print(f'id: {obj.id} type: {obj.object_type}')
    
        if obj.object_type == OBJECT.ASYMMETRIC_KEY:
            print('Found asymetric key')
            info = obj.get_info()
            print(info)
            save_pub_key(obj)

    # Clean up:
    session.close()
    hsm.close()
except exceptions.YubiHsmConnectionError as e:
    print(f'ERROR: Failed to connect to HSM over USB. [{e}]')
    sys.exit(-2)
except exceptions.YubiHsmDeviceError as e:
    print(f'ERROR: Wrapping key decryption failed. [{e}]')
    sys.exit(-3)

sys.exit(0)