#!/usr/bin/env python
from __future__ import print_function

import codecs
import getpass
import os
from os.path import expanduser
from pwd import getpwnam
import stat
import sys
import yaml
from ansible.parsing import vault
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.yaml import objects
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.parsing.yaml.loader import AnsibleLoader


def init():

    try:
        secrets_dir_path = expanduser("~") + "/.ansible-vault-secrets"
        secrets_file_path = secrets_dir_path + "/secrets.yml"
        decrypted_file_path = secrets_dir_path + "/decrypted"
        user = getpass.getuser()
        uid = getpwnam(user).pw_uid
        sdstat = os.stat(secrets_dir_path)
        sfstat = os.stat(secrets_file_path)
        sduid = sdstat.st_uid
        sfuid = sfstat.st_uid
        sdperm = sdstat.st_mode
        sfperm = sfstat.st_mode
    except KeyError:
        print (".secrets imporperly configured")
        sys.exit(1)

    # Check that directory and file permissions are set properly
    if (sduid != uid or sdperm != 16832 or sfperm != 33152):
        print (secrets_dir_path, "is misconfigured.")
        sys.exit(2)

    return secrets_file_path, decrypted_file_path


def decrypt(secrets_file_path, decrypted_file_path):

    try:
        vault_password_file = os.environ["ANSIBLE_VAULT_PASSWORD_FILE"]
    except KeyError:
        #print ("export ANSIBLE_VAULT_PASSWORD_FILE")
        sys.exit(3)

    with open(vault_password_file, 'r') as vpf:
        vault_password = vpf.read().replace('\n', '')

    # Load vault password and prepare secrets for decryption
    loader = DataLoader()
    secret = vault.get_file_vault_secret(filename=vault_password_file, loader=loader)
    secret.load()
    vault_secrets = [('default', secret)]
    _vault = vault.VaultLib(vault_secrets)

    # Load encrypted yml for processing
    with codecs.open(secrets_file_path, 'r', encoding='utf-8') as f:
        loaded_yaml = AnsibleLoader(f, vault_secrets=_vault.secrets).get_single_data()

    # Modify yml with new encrypted values
    new_encrypted_variable = objects.AnsibleVaultEncryptedUnicode \
        .from_plaintext(vault_password, _vault, vault_secrets[0][1])

    # Write a new encrypted yml
    with open('new_variables.yml','w') as fd:
        yaml.dump(loaded_yaml, fd, Dumper=AnsibleDumper, encoding=None, default_flow_style=False)


    # Define decrypted file params
    open_flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    open_mode = stat.S_IRUSR | stat.S_IWUSR # 0o600 in octal
    open_umask = os.umask(0) # Save current umask to prevent downgrading to 0

    # Delete and replace decrypted secrets to ensure file permissions
    try:
        os.remove(decrypted_file_path)
    except OSError:
        pass

    # Open the file descriptor
    umask_original = os.umask(open_umask)
    try:
        decrypted_file_fd = os.open(decrypted_file_path, open_flags, open_mode)
    finally:
        os.umask(umask_original)
        #os.umask(0o777)

    # Open file handle and write the decrypted file
    decrypted_file_out = os.fdopen(decrypted_file_fd, 'w')
    for k,v in loaded_yaml.items():
        line = "export " + str(k) + "=" + str(v) + "\n"
        decrypted_file_out.write(line)
    decrypted_file_out.close()


def main():
    secrets_file, decrypted_file = init()
    decrypt(secrets_file, decrypted_file)


if __name__ == '__main__':
    main()
