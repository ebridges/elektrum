#!/usr/local/bin/bash

WORKING_DIR=$(dirname "${BASH_SOURCE[0]}")  # get the script's directory name
WORKING_DIR=$(realpath "${WORKING_DIR}/..") # resolve its full path up one dir

cd ${WORKING_DIR}

source etc/config.env

TAG="${org_name}/${app_name}"

cmd=$1

if [ -z "${cmd}" ];
then
    echo "$0 [build|run|deploy]"
    exit 0
fi

if [ "${cmd}" == 'build' ];
then
    docker build --tag ${TAG} .
fi

if [ "${cmd}" == 'run' ];
then
    docker run ${TAG}
fi

if [ "${cmd}" == 'deploy' ];
then
    docker build  --tag ${TAG} .
    $(aws ecr get-login --no-include-email --region us-east-1)
    docker tag ${TAG}:latest ${container_repository_uri}:latest
    docker push ${container_repository_uri}:latest
fi
