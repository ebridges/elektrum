#!/bin/sh

var_name=$1
env=${2:-development}
if [ -z "${var_name}" ];
then
    echo "Usage: $0 [varname] (env)"
    exit 1
fi

echo "Decrypting var $var for env: $env"
yq read network/group_vars/${env}.yml ${var_name} | ansible-vault decrypt --vault-password-file=network/environments/${env}-vault-password.txt
