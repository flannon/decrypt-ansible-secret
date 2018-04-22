#!/bin/bash

set -e

usage() {
  echo "Usage: $0 <Key> <Secrets_File>"
}
[[ -z $1 ]] && usage && exit 1
[[ -z $2 ]] && usage && exit 2
avp_usage() {
  echo "Usage: export ANSIBLE_VAULT_PASSWORD_FILE=<path to ault_password file>"
}
: "${ANSIBLE_VAULT_PASSWORD_FILE?$(avp_usage)}" 

readonly KEY="$1"
readonly SECRETSFILE="$2"
readonly AV=$(cat $SECRETSFILE | cfn-flip | jq ".${KEY} | to_entries[] | \
  .value" | sed -e s/\"/""/g)
  
readonly AVPREFIX=${AV%%\\n[0-9]*}
readonly ANSIBLESECRET=$(echo $AV | sed -e s/${AVPREFIX}/""/g | \
  sed -e 's/\\n/''/g')

#echo -e "${AVPREFIX}\n${ANSIBLESECRET}" | ansible-vault decrypt /dev/stdin --output=/dev/stderr --vault-password-file="~/.ansible/vault_password" > /dev/null
echo -e "${AVPREFIX}\n${ANSIBLESECRET}" | ansible-vault decrypt /dev/stdin --output=/dev/stderr 2>&1 > /dev/null 
