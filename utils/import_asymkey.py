import sys
import argparse

from yubihsm import YubiHsm
from yubihsm.defs import OBJECT
from yubihsm.defs import ALGORITHM
from yubihsm.objects import AsymmetricKey, WrapKey
from yubihsm.defs import CAPABILITY as CAP
from yubihsm import exceptions

import binascii as bs

parser = argparse.ArgumentParser(
                    prog='import_asymkey',
                    description='Import an asymmetric key wrapped with AES-256.')

parser.add_argument('-k', '--authkey_id', default=1, type=int, help='Authentication Key ID to use for the session. (Default: 1)')
parser.add_argument('-p', '--authkey_password', required=True, help='Password used to unlock the HSM')
parser.add_argument('-d', '--domain', default=1, type=int, help='Domain assigned to the wrapping key. (Default: 1)')
# parser.add_argument('id', type=int, help='ID of key to import.')
parser.add_argument('filename', type=str, help='Filename of the wrapped key to import.')
parser.add_argument('aes_key', type=str, help='AES-256 wrapping key as a hex string.')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey_id, args.authkey_password)

    # Create the AES-128 wrapping key from the passed in aes_key value
    wrap_key = WrapKey.put( session, 
                            100, 
                            "Wrapping Key", 
                            args.domain, 
                            CAP.EXPORT_WRAPPED | CAP.IMPORT_WRAPPED,
                            ALGORITHM.AES256_CCM_WRAP, 
                            CAP.SIGN_ECDSA | CAP.EXPORTABLE_UNDER_WRAP,
                            bs.unhexlify(args.aes_key) )
    
    print(wrap_key)

    print(f'Importing asymmetric key.')

    # Read in the wrapped key
    with open(args.filename, 'br') as fd:
        wrapped_key = fd.read()

    key = wrap_key.import_wrapped(wrapped_key)

    print(f'Import successful. [ID: {key.id}]')

    # Delete the AES key
    WrapKey.delete(wrap_key)

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
    print(f'ERROR: Failed to export asymmetric key. [{e}]')
    sys.exit(-3)

sys.exit(0)
