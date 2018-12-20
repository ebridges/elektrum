#!/bin/sh

ansible-playbook \
  --inventory hosts.ini \
  --vault-password-file ./vault-password.txt \
  $@ \
  site.yml
