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
                    prog='export_asymkey',
                    description='Export an asymmetric key wrapped with AES-256.')

parser.add_argument('-k', '--authkey_id', default=1, type=int, help='Authentication Key ID to use for the session. (Default: 1)')
parser.add_argument('-p', '--authkey_password', required=True, help='Password used to unlock the HSM')
parser.add_argument('-d', '--domain', default=1, type=int, help='Domain assigned to the wrapping key. (Default: 1)')
parser.add_argument('id', type=int, help='ID of key to export.')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey_id, args.authkey_password)

    # Generate an AES-128 key
    aes_key = session.get_pseudo_random(32)

    print(f'Wrapping AES-256 Key: {bs.hexlify(aes_key).decode("ascii")}')

    wrap_key = WrapKey.put( session, 
                            100, 
                            "Wrapping Key", 
                            args.domain, 
                            CAP.EXPORT_WRAPPED | CAP.IMPORT_WRAPPED,
                            ALGORITHM.AES256_CCM_WRAP, 
                            CAP.SIGN_ECDSA | CAP.EXPORTABLE_UNDER_WRAP,
                            aes_key )
    
    print(wrap_key)

    print(f'Exporting asymmetric key. [ID: {args.id}]')

    asym_key = session.get_object(args.id, OBJECT.ASYMMETRIC_KEY)

    # Export Asymmetric key wrapped with the AES-256 key.
    exported_key = wrap_key.export_wrapped(asym_key)

    # Wrapped AsymmetricKey
    # print('Wrapped Asymmetric Key:')
    # print(bs.hexlify(exported_key))

    # Delete the AES key
    WrapKey.delete(wrap_key)

    filename = f'./wrapped_key_{args.id}.bin'

    print(f'Key exported to {filename}.')
    with open(filename, 'bw') as fd:
        fd.write(exported_key)

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
