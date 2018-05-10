#!/usr/bin/env bash
# yq is available at https://github.com/kislyuk/yq
# and can be installed with `pip install yq`

set -e

usage() {
  echo "Useage: $0 -e | -d <value>"
}

#CMK_ARN=${CMK_AWS_ENCRYPTION_SDK}


# Check that everthing is in place
[[ -z $1 ]] || [[ -z $2 ]] && usage && exit 2
[[ ! -x "$(command -v yq)" ]] && echo "yq is not installed. Exiting..." && exit 3

encrypt() {
  encrypted=$(echo $VALUE | aws-encryption-cli --encrypt -S \
                             --input - --output - --encode \
                             --master-keys key=$CMK_ARN )

  echo $encrypted
}

decrypt () {
  # 
  echo $ENCRYPTED | aws-encryption-cli --decrypt --input - --output - --decode -S
}

case "$1" in
  -e) 
    VALUE=$2
    encrypt
    ;;
  -d) 
    ENCRYPTED=$2
    decrypt
    ;;
esac

