import sys
import argparse

from yubihsm import YubiHsm
from yubihsm.defs import OBJECT
from yubihsm.objects import AsymmetricKey
from yubihsm import exceptions

parser = argparse.ArgumentParser(
                    prog='delete_asymkey',
                    description='Delete an asymmetric key.')

parser.add_argument('-k', '--authkey_id', default=1, type=int, help='Authentication Key ID to use for the session. (Default: 1)')
parser.add_argument('-p', '--authkey_password', required=True, help='Password used to unlock the HSM')
parser.add_argument('id', type=int, help='ID key to delete.')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey_id, args.authkey_password)

    print(f'Deleting asymmetric key. [ID: {args.id}]')
    
    key = session.get_object(args.id, OBJECT.ASYMMETRIC_KEY)

    # Ask if user is sure
    confirm = input('Warning! Are you sure you wish to delete the key? (y/N)')

    if confirm != 'y':
        sys.exit(0)

    AsymmetricKey.delete(key)

    print('Key deleted.')

    # Clean up:
    session.close()
    hsm.close()
except exceptions.YubiHsmAuthenticationError as e:
    print(f'ERROR: Failed to authenticate. [{e}]')
    sys.exit(-1)
except exceptions.YubiHsmConnectionError as e:
    print(f'ERROR: Failed to connect to HSM over USB. [{e}]')
    sys.exit(-2)
except exceptions.YubiHsmDeviceError as e:
    print(f'ERROR: Failed to delete asymmetric key. [{e}]')
    sys.exit(-3)

sys.exit(0)
