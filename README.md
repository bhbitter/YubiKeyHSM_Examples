# Examples for Yubikey2 HSM

This project contains various example python programs that support different operations available for creating and verifying signatures using elliptic curve asymmetric keys.

**Note:** All programs are written in Python and tested using Python version 3.11.4

## Installation

To run the test programs make sure the python dependencies are installed. To do this, run the following command:

```bash
pip pip install -r requirements.txt
```

## Structure of the Project

The main programs of the project are in the base directory. Utility programs are in the utils directory. These programs are used for managing signing keys and other aspects of the HSM.

## Example of Setting Up an HSM, Signing, and Verifying a File

The following steps show how to setup an HSM and then create and verify a signature.

### Step 1: Create a new authentication key

This command will create a new authentication key that can be used to create signing keys and sign data. The authentication key is set for domain 2 with password: password

```bash
python3 utils/create_authkey.py -k 1 -p password  -d 2 -a 2 "Dev Auth Key" password
```

To get the public key for the new siging key, run the following command:

```bash
# This will save the public key to a file called public_key_2000.pem
python3 utils/get_pub_keys.py -k 2 -p password
```

### Step 2: Create a new signing key

Create a new signing ecp384 signing key:

```bash
python3 utils/create_signing_key.py -k 2 -p password -d 2 --id 2000 "Dev Signing Key"
```

### Step 3: Create a signature of the file README.md

Create a signature of README.md and store it into a binary file called README.md.sig.

```bash
python3 sign.py -k 2 2000 README.md password
```

### Step 4: Verify the signature using openssl

```bash
openssl dgst -sha256 -verify public_key_2000.pem -signature README.md.sig README.md
```
