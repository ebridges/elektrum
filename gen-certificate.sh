#!/bin/sh

DOMAIN_NAME='elektrum.dev'
SUBJ_ALTNAME='*.elektrum.dev'

aws --profile elektrum-development acm request-certificate \
    --domain-name ${DOMAIN_NAME} \
    --subject-alternative-names ${SUBJ_ALTNAME} \
    --validation-method DNS \
    --tags '[{"Key": "Name", "Value": "elektrum-certificate"},{"Key": "Service", "Value": "elektrum"}]'
