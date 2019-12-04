#!/bin/bash

function main() {
    log "Generating pip-style requirements.txt."
    etc/bin/poetry2pip.py poetry.lock > requirements.txt

    log "Bundling lambda code into a zip archive."
    lambda_archive=$(lgw lambda-archive ${VERBOSE} --config-file=${CONFIG})

    log "Deploying lambda archive from location: ${lambda_archive}"
    lgw lambda-deploy ${VERBOSE} --config-file=${CONFIG} --lambda-file=${lambda_archive}

    log "Creating an API gateway for this function, if it doesn't already exist."
    lgw gw-deploy ${VERBOSE} --config-file=${CONFIG}

    log "Linking domain name with this gateway."
    api_url=$(lgw domain-add ${VERBOSE} --config-file=${CONFIG})

    log "Application deployed at URL: ${api_url}"
}

function log() {
    msg=$1
    now=$(date +"%Y/%m/%d %H:%M:%S")
    echo "[${now}][BASH] ${msg}"
}

ENV=
VERBOSE=

while true; do
    case "$1" in
    -v|--verbose)
        VERBOSE=--verbose
        shift;
        ;;
    development|staging|production)
        ENV=$1
        shift
        ;;
    *)
        break
        ;;
    esac
done

if [ -z "${ENV}" ];
then
  echo "Usage: $0 [development|staging|production]"
  exit 1
fi

CONFIG="etc/env/${ENV}.env"
VERSION=$(cat version.txt | tr -d '\n')
CWD=$(pwd)

export AWS_ACCESS_KEY_ID=`yq read network/group_vars/${ENV}.yml 'aws_access_key' | ansible-vault decrypt --vault-password-file=network/environments/${ENV}-vault-password.txt`
export AWS_SECRET_ACCESS_KEY=`yq read network/group_vars/${ENV}.yml 'aws_secret_key' | ansible-vault decrypt --vault-password-file=network/environments/${ENV}-vault-password.txt`
export AWS_LAMBDA_ARCHIVE_KEY="elektrum-${VERSION}.zip"

log "Building Elektrum release v${VERSION}."
log "    Environment:   ${ENV}"
log "    Configuration: ${CONFIG}"
log "    Current dir:   ${CWD}"
main "$@"
