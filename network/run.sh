#!/bin/sh

if [ -z "${ELEKTRON_ENV}" ];
then
  ELEKTRON_ENV=staging
fi

ansible-playbook \
  --inventory hosts.ini \
  --vault-password-file ./vault-password.txt \
  --extra-vars="elektron_env=${ELEKTRON_ENV}" \
  $@ \
  site.yml
