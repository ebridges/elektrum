#!/bin/sh

ansible-playbook -i hosts.inventory tasks/show-facts.yml --vault-password-file ./vault-password.txt $@
