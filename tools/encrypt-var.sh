#!/bin/sh

var_name=${1}
env=${2:-development}
if [ -z "${var_name}" ];
then
    echo "Usage: $0 [varname] (env)"
    exit 1
fi

echo "Encrypting var $var_name for env: $env"
pbpaste | ansible-vault encrypt_string --vault-password-file=network/environments/${env}-vault-password.txt --stdin-name ${var_name} | pbcopy
