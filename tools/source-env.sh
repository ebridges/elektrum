#!/bin/sh

ENV=$1

if [ -z "${ENV}" ];
then
  echo "Usage: ${0} [development|staging|production]"
  exit 1
fi

echo export AWS_ACCESS_KEY_ID=`yq read network/group_vars/${ENV}.yml 'aws_access_key' | ansible-vault decrypt --vault-password-file=network/environments/${ENV}-vault-password.txt`
echo export AWS_SECRET_ACCESS_KEY=`yq read network/group_vars/${ENV}.yml 'aws_secret_key' | ansible-vault decrypt --vault-password-file=network/environments/${ENV}-vault-password.txt`
