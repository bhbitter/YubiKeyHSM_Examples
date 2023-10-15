#!/usr/bin/env python
import argparse
import sys

from yubihsm import YubiHsm
from yubihsm import exceptions

parser = argparse.ArgumentParser(
                    prog='get_objects',
                    description='Retrieve and print out the HSM objects')

parser.add_argument('-k', '--authkey', default=1, type=int, help='Authentication Key ID to use. Default is 1')
parser.add_argument('-p', '--password', required=True, help='Password used to unlock the HSM')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey, args.password)

    objs = session.list_objects()

    key = None

    for obj in objs:
        print(f'id: {obj.id} type: {obj.object_type}')
        info = obj.get_info()
        print(info)
        print("") # Newline

    # Clean up:
    session.close()
    hsm.close()
except exceptions.YubiHsmConnectionError as e:
    print(f'ERROR: Failed to connect to HSM over USB. [{e}]')
    sys.exit(-2)
except exceptions.YubiHsmAuthenticationError as e:
    print(f'ERROR: Failed to unlock HSM with supplied password. [{e}]')
    sys.exit(-3)
except Exception as e:
    print(f'ERROR: [{e}]')
    sys.exit(-4)
