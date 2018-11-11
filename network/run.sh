#!/bin/sh

ansible-playbook -i hosts.inventory tasks/vpc.yml --vault-password-file ./vault-password.txt $@

