#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
import yaml

import aws_encryption_sdk
import botocore.session

CMK_ARN = str(os.environ['CMK_ARN'])

print(CMK_ARN)

def init_kms():

    # kms_key_provider is essentially a session and a key arn
    kms_key_provider = aws_encryption_sdk.KMSMasterKeyProvider(key_ids=[
        CMK_ARN
        ])

    return kms_key_provider


#def encrypt(key_arn):
def encrypt(kms_key_provider, plaintext_secret):

    #key = sys.argv[2]
    #value_plaintext = sys.argv[3]

    ciphertext, encryptor_header = aws_encryption_sdk.encrypt(
            source=plaintext_secret,
            key_provider=kms_key_provider
    )

    return ciphertext


def secrets_writer(secrets_file, ciphertext):
    # Read secrets.yml into a dicitonary, update old keys or add new key
    # see https://stackoverflow.com/questions/48645391/how-to-append-data-to-yaml-file
    # for updating the dict

    key = sys.argv[2]
    data = {key: ciphertext}
    with open(secrets_file, 'r') as yaml_file:
        cur_yaml = yaml.load(yaml_file)
        cur_yaml.update(data)
        combined_yaml = cur_yaml

    with open(secrets_file, 'w') as yaml_file:
        yaml.dump(cur_yaml, yaml_file, default_flow_style=False)


def secrets_reader(secrets_file, lookup_key):
    with open(secrets_file, 'r') as f:
        secrets = yaml.safe_load(f)

    return secrets[lookup_key]


def decrypt(kms_key_provider, ciphertext):

    decrypted, decryptor_header = aws_encryption_sdk.decrypt(
            source=ciphertext,
            key_provider=kms_key_provider
            )

    print(decrypted)


def main():

    secrets_file = './result.yml'

    # Initialize the key provider
    kms_key_provider = init_kms()

    parser = argparse.ArgumentParser(description='Demo')
    parser.add_argument('--encrypt',
        action='store_true',
        help='encrypt flag')
    parser.add_argument('--decrypt',
        action='store_true',
        help='decrypt flag')
    parser.add_argument('pair', nargs='*')
    args = parser.parse_args()

    if args.encrypt:

        lookup_key = args.pair[0]
        plaintext_secret = args.pair[1]

        # Encrypt the value
        ciphertext = encrypt(kms_key_provider, plaintext_secret)
        print('Ciphertext: ', ciphertext)

        # Write the key and vaule to secrets.yml
        secrets_writer(secrets_file, ciphertext)

    elif args.decrypt:

        lookup_key = args.pair[0]
        ciphertext = secrets_reader(secrets_file, lookup_key)
        decrypt(kms_key_provider, ciphertext)

    else:

        print('No flag set')


if __name__ == "__main__":
    main()
