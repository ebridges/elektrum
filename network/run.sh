#!/bin/sh

ansible-playbook -i hosts.ini site.yml --vault-password-file ./vault-password.txt $@
