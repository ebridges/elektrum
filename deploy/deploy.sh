#!/usr/local/bin/bash

source deploy/config.env

cmd=$1

if [ -z "${cmd}" ];
then
    echo "$0 [build|run|deploy|login]"
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
	docker tag ${APP_NAME} ${DOCKER_REPO}/${APP_NAME}:latest
    docker push ${DOCKER_REPO}/${APP_NAME}:latest
fi

if [ "${cmd}" == 'login' ];
then
    aws ecr --profile ${AWS_CLI_PROFILE} --region ${AWS_CLI_REGION} get-login --no-include-email
fi
