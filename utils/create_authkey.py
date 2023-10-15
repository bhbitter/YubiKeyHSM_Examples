import sys
import argparse

from yubihsm import YubiHsm
from yubihsm.defs import CAPABILITY as CAP
from yubihsm.objects import AuthenticationKey
from yubihsm import exceptions

parser = argparse.ArgumentParser(
                    prog='create_authkey',
                    description='Create a new authentication key.')

parser.add_argument('-k', '--authkey_id', default=1, type=int, help='Authentication Key ID to use for the session. (Default: 1)')
parser.add_argument('-p', '--authkey_password', required=True, help='Password used to unlock the HSM')
parser.add_argument('-a', '--admin', action='store_true', help='Add administrative capabilities.')
parser.add_argument('-d', '--domain', default=1, type=int, help='Domain assigned to the new authentication key. (Default: 1)')
parser.add_argument('id', type=int, help='ID for the new authentication key.')
parser.add_argument('label', help='Label for the key.')
parser.add_argument('password', help='Password to use to unlock the new authentication key.')

args = parser.parse_args()

admin_caps = CAP.GENERATE_ASYMMETRIC_KEY | CAP.EXPORT_WRAPPED | CAP.GET_PSEUDO_RANDOM | CAP.PUT_WRAP_KEY | CAP.IMPORT_WRAPPED | CAP.DELETE_ASYMMETRIC_KEY | CAP.DELETE_WRAP_KEY | CAP.DELETE_AUTHENTICATION_KEY

admin_delegated_caps = CAP.EXPORTABLE_UNDER_WRAP | CAP.EXPORT_WRAPPED | CAP.IMPORT_WRAPPED 

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey_id, args.authkey_password)

    # Generate a new authentication key
    # put authkey 0 2 DevKey 1 generate-asymmetric-key,export-wrapped,get-pseudo-random,put-wrap-key,import-wrapped,delete-asymmetric-key,decrypt-oaep decrypt-oaep,exportable-under-wrap,export-wrapped,import-wrapped 9gROdJPLi64lPWgTyY81btjPYxYUjad3
    #
    caps = CAP.SIGN_ECDSA

    delegated_caps = CAP.SIGN_ECDSA

    if args.admin:
        print('Setting admin capabilities.')
        caps = caps | admin_caps
        delegated_caps = delegated_caps | admin_delegated_caps

    print(f'Creating a new authentication key. [ID: {args.id}, Domain: {args.domain}. Label: {args.label}]')
    key = AuthenticationKey.put_derived(
            session,     # Session
            args.id,     # AuthKey ID
            args.label,  # Label
            args.domain, # Domain
            caps,        # Capabilities  
            delegated_caps,   # Delegated Capabilities
            args.password
        )

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
    print(f'ERROR: Failed to create authentication key. [{e}]')
    sys.exit(-3)
except Exception as e:
    print(f'ERROR: [{e}]')
    sys.exit(-4)
    
sys.exit(0)
