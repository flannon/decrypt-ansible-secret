# decrypt-ansible-secrets
An evaluation of ansible-vault as a generic secrets management utility


## Table of Contents

1. [Overview](#overview)
2. [Initial assumptions](#initial-assumptions)
2. [Ansible Examples](#ansible-examples)
2. [YAML](#yaml)
3. [decryptas.sh](#decryptas.sh)
3. [Other Condiserations](#other)


#### Overview


Ansible-vault is a secrets managements systems that provides encryption and decryption services for managing secrets inside of ansible playbooks.  Within the ansible enviroment ansible-vault does a nice job of secrets management, but how does it perform as a generic secrets management service?

#### Initial assumptions

-	Encrypted passwords will be stored in repositories
-	The operating system’s security context is implicitly trusted: i.e. given a properly configured user environment, and properly configured permissions that allow only user access, values from configuration files and exported environment variables are assumed to be trusted
-	

#### Ansible examples
 
#### File encryption
    `ansible-vault encrypt_string 'mysecretword' --name encryptedpasswd --vault-password-file=vault_password > defaults/secrets.yml`


Save your ansible-vault password in ~/.ansible/vault_password

    export ANSIBLE_VAULT_PASSWORD_FILE="~/.ansible/vault_password"


You can use ansible-vault to encrypt a file, or to encrypt values in a yaml file.

After exporting ANSIBLE_VAULT_PASSWORD_FILE you can encrypt a file like this,

    ansible-vault encrypt secretsfile.yaml

The encrypted file can be decrypted,

    ansible-vault decrypt secretsfile.yaml

Or edited in place without decrypting,

    ansible-vault edit secretsfile.yaml

 #Key Encryption
Here’s where things kind of start to break down.  Since ansible-secrets was designed as an internal mechanism for ansible the cli doesn’t have a straight forward way to decrypt an encrypted value.  To decrypt and encrypted string you have to manually feed it back in,

$ echo '$ANSIBLE_VAULT;1.1;AES256
386433646437643838303964343461666561656666383734653465613639363731626334633039303739656331363539303432656434343466313631386263340a316264656364363463626165373764313135333862616332396639646266356566383235376432623731393635303438326661303735633764663430626566650a30666439653964643233623561616633356264323264373438613437353361373831623336326339333032323036393336613633666362316666393536313139' | ansible-vault decrypt /dev/stdin --output=/dev/stderr --vault-password-file="~/.ansible/vault_password" > /dev/null

#### YAML

An example of a yamle structure made by ansible-vault

    ansible_secret_1: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          33663338626365666433383562383134396264326530646165373966633534366137366537353638
          3062303739643434376631366330313162613765343734370a636564613166623564656165343230
          34666432646637616162646465643531626231393339636435363264386239353831396234306363
          3635643736613164640a623435663163623932353266616438343038363330643534613162346466
          31623130363039376166636664383638343062373833326332306438356332653533 

#### decryptas.sh

  #python3
  #cfn-flip
  #jq

## Other considerations not included in the current analysis
 --rprecommit hooks to ensure only encrypted values are checked in to your repo.

