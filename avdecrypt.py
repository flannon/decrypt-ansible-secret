#!/usr/bin/env python
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
        #sdir = "./test"
        sdir = expanduser("~") + "/.secrets"
        sfile = sdir + "/secrets.yml"
        dfile = sdir + "/decrypted"
        #sfile = sdir + "/secrets"
        user = getpass.getuser()
        uid = getpwnam(user).pw_uid
        sdstat = os.stat(sdir)
        sfstat = os.stat(sfile)
    except KeyError:
        print ".secrets bad permissions"
        sys.exit(1)

    sduid = sdstat.st_uid
    sfuid = sfstat.st_uid
    sdperm = sdstat.st_mode
    sfperm = sfstat.st_mode

    #if check file perms

    print "sdperm: " + str(sdperm) + " sfperm: " + str(sfperm)
    print "sduid: " + str(sduid)

    return sfile, dfile


def decrypt(secrets_file, decrypted_file):

    #secrets_file = expanduser("~") + "/.secrets/secrets.yml"

    try:
        vault_password_file = os.environ["ANSIBLE_VAULT_PASSWORD_FILE"]
    except KeyError:
        print "export ANSIBLE_VAULT_PASSWORD_FILE"
        sys.exit(2)

    with open(vault_password_file, 'r') as vpf:
        vault_password = vpf.read().replace('\n', '')

    print "vault_passwordi: " + vault_password

    # Load vault password and prepare secrets for decryption
    loader = DataLoader()
    secret = vault.get_file_vault_secret(filename=vault_password_file, loader=loader)
    secret.load()
    vault_secrets = [('default', secret)]
    _vault = vault.VaultLib(vault_secrets)

    # Load encrypted yml for processing
    with codecs.open(secrets_file, 'r', encoding='utf-8') as f:
        loaded_yaml = AnsibleLoader(f, vault_secrets=_vault.secrets).get_single_data()

    # Modify yml with new encrypted values
    new_encrypted_variable = objects.AnsibleVaultEncryptedUnicode \
        .from_plaintext(vault_password, _vault, vault_secrets[0][1])

    # Write a new encrypted yml
    with open('new_variables.yml','w') as fd:
        yaml.dump(loaded_yaml, fd, Dumper=AnsibleDumper, encoding=None, default_flow_style=False)

    #print(loaded_yaml)
    #print type(loaded_yaml)

    sf_out = open(decrypted_file, "w")
    for k,v in loaded_yaml.items():
        line = "export " + str(k) + "=" + str(v) + "\n"
        print line
        #print "type k:", type(k)
        #print "Key: ", key
        sf_out.write(line)
        #print k,":", v
        #os.environ[k] = str(v)
        #os.putenv(k, str(v))
    sf_out.close()


def main():
    secrets_file, decrypted_file = init()
    print secrets_file
    print type(secrets_file)
    decrypt(secrets_file, decrypted_file)


if __name__ == '__main__':
    main()
