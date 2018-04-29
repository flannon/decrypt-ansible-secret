#!/usr/bin/env python
# References used for this descriptor
#  I barrowed heavily from andrunah's solution for decrypting
#  ansible vaulted variables, available at
#    https://github.com/andrunah/ansible-vault-variable-updater
#  As well as the following material
#    https://github.com/ansible/ansible/issues/26190
#    https://stackoverfow.com/a/15015748/3447107
#    https://security.openstack.org/guidelines/dg_apply-restrictive-file-permissions.html
#
from __future__ import print_function

import codecs
import getpass
import os
from os.path import expanduser
from pwd import getpwnam
import stat
import sys
from ansible.parsing import vault
from ansible.parsing.dataloader import DataLoader
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
    if (sduid != uid or sfuid != uid or sdperm != 16832 or sfperm != 33152):
        print (secrets_dir_path, "is misconfigured.")
        sys.exit(2)

    return secrets_file_path, decrypted_file_path


def decrypt(secrets_file_path, decrypted_file_path):

    try:
        vault_password_file = os.environ["ANSIBLE_VAULT_PASSWORD_FILE"]
    except KeyError:
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

    # Define decrypted file params
    flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    mode = stat.S_IRUSR | stat.S_IWUSR  # 0o600 in octal
    umask = os.umask(0)  # Save current umask to prevent downgrading to 0

    # Delete and replace decrypted secrets to ensure file permissions
    try:
        os.remove(decrypted_file_path)
    except OSError:
        pass

    # Open the file descriptor
    umask_original = os.umask(umask)
    try:
        decrypted_file_fd = os.open(decrypted_file_path, flags, mode)
    finally:
        os.umask(umask_original)

    # Open file handle and write the decrypted file
    decrypted_file_out = os.fdopen(decrypted_file_fd, 'w')
    for k, v in loaded_yaml.items():
        line = "export " + str(k) + "=" + str(v) + "\n"
        decrypted_file_out.write(line)
    decrypted_file_out.close()


def main():
    secrets_file, decrypted_file = init()
    decrypt(secrets_file, decrypted_file)


if __name__ == '__main__':
    main()
