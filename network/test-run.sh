#!/bin/sh

if [ -z "${1}" ];
then
  echo "Usage: $0 [production|staging|development]"
  exit 1
fi

ENV=${1}
shift

ansible-playbook \
  --inventory environments/${ENV} \
  --vault-password-file environments/${ENV}-vault-password.txt \
  ${@} \
  test.yml
