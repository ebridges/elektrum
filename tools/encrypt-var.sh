#!/bin/sh

env=development
var_name=$1
if [ -z "${var_name}" ];
then
    echo "Usage: $0 [varname]"
    exit 1
fi

pbpaste | ansible-vault encrypt_string --vault-password-file=network/environments/${env}-vault-password.txt --stdin-name ${var_name} | pbcopy
