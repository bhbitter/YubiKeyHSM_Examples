import sys
import argparse

from yubihsm import YubiHsm
from yubihsm.defs import OBJECT
from yubihsm.objects import AuthenticationKey
from yubihsm import exceptions

parser = argparse.ArgumentParser(
                    prog='change_authkey_passwd',
                    description='Change authentication key password.')

parser.add_argument('-k', '--authkey_id', default=1, type=int, help='Authentication Key ID to use for the session. (Default: 1)')
parser.add_argument('-p', '--authkey_password', required=True, help='Password used to unlock the HSM')
parser.add_argument('id', type=int, help='ID for the new authentication key.')
parser.add_argument('password', help='Password to use to unlock the new authentication key.')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey_id, args.authkey_password)

    print(f'Changing authentication key password. [ID: {args.id}]')
    
    key = session.get_object(args.id, OBJECT.AUTHENTICATION_KEY)

    AuthenticationKey.change_password(key, args.password)

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
    print(f'ERROR: Failed to change authentication key password. [{e}]')
    sys.exit(-3)
except Exception as e:
    print(f'ERROR: [{e}]')
    sys.exit(-4)

sys.exit(0)
