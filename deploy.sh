#!/usr/local/bin/bash

source deploy/config.env

cmd=$1

if [ -z "${cmd}" ];
then
    echo "$0 [build|run|deploy]"
    exit 0
fi

if [ "${cmd}" == 'build' ];
then
    pipenv lock -r > deploy/temp-requirements.txt
    docker build --file deploy/Dockerfile --tag ${APP_NAME} .
fi

if [ "${cmd}" == 'run' ];
then
    docker-compose --file=deploy/docker-compose.yml up
fi

if [ "${cmd}" == 'deploy' ];
then
    pipenv lock -r > deploy/temp-requirements.txt
    docker build --file deploy/Dockerfile --tag ${APP_NAME} .
    $(aws ecr get-login --no-include-email --region us-east-1)
    docker tag ${APP_NAME}:latest ${DOCKER_REPO}/${APP_NAME}:latest
    docker push ${DOCKER_REPO}/${APP_NAME}:latest
fi
