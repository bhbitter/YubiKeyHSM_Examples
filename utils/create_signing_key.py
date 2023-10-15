import sys
import argparse

from yubihsm import YubiHsm
from yubihsm import exceptions
from yubihsm.defs import CAPABILITY, ALGORITHM
from yubihsm.objects import AsymmetricKey

from cryptography.hazmat.primitives import serialization

parser = argparse.ArgumentParser(
                    prog='create_signing_key',
                    description='Create a new ecp384 signing key.')

parser.add_argument('-k', '--authkey_id', default=1, type=int, help='Authentication Key ID to use for the session. (Default: 1)')
parser.add_argument('-p', '--authkey_password', required=True, help='Password used to unlock the HSM')
parser.add_argument('-d', '--domain', default=1, type=int, help='Domain assigned to the new authentication key. (Default: 1)')
parser.add_argument('--id', type=int, default=0, help='ID for the new asymmetric key. If not specified, an ID will be generated.')
parser.add_argument('label', help='Label for the key.')

args = parser.parse_args()

# Connect to the YubiHSM via the connector using the default password:
# hsm = YubiHsm.connect('http://localhost:12345')
try:
    hsm = YubiHsm.connect('yhusb://')
    session = hsm.create_session_derived(args.authkey_id, args.authkey_password)

    print('Key generation can take several minutes to complete. Please be patient.')
    # Generate a private key on the YubiHSM for creating signatures:
    key = AsymmetricKey.generate(  # Generate a new key object in the YubiHSM.
        session,                   # Secure YubiHsm session to use.
        args.id,                   # Object ID, 0 to get one assigned.
        args.label,                # Label for the object.
        args.domain,               # Domain(s) for the object.
        CAPABILITY.SIGN_ECDSA | CAPABILITY.EXPORTABLE_UNDER_WRAP,   # Capabilities for the object.
        ALGORITHM.EC_P384          # Algorithm for the key.
    )

    print('Key generation complete.')

    # pub_key is a cryptography.io ec.PublicKey, see https://cryptography.io
    pub_key = key.get_public_key()

    pub_key_str = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('ascii')

    print(pub_key_str)

    # Write the public key to a file:
    with open(f'./public_key_{key.id}.pem', 'w') as f:
        f.write(pub_key_str)

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
    print(f'ERROR: Failed to create signing key. [{e}]')
    sys.exit(-3)

sys.exit(0)

