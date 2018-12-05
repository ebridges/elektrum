#!/usr/local/bin/bash

USAGE="Usage: ${0} <path to config.env> [build|run|push|deploy|logs]"

CONFIG=${1}
CMD=$2

if [ -z "${CONFIG}" ];
then
    echo ${USAGE}
    exit 1
fi


if [ -z "${CMD}" ];
then
    echo ${USAGE}
    exit 1
fi

if [ ! -e ./Dockerfile ];
then
    echo 'Dockerfile not found in current directory.'
    exit 1
fi

source ${CONFIG}

IMAGE="${org_name}/${app_name}"


if [ "${CMD}" == 'build' ];
then
    docker build -t ${IMAGE}:latest .
fi

if [ "${CMD}" == 'push' ];
then
    docker build .
    $(aws ecr get-login --no-include-email --region us-east-1)
    docker tag ${IMAGE}:latest ${container_repository_uri}:latest
    docker push ${container_repository_uri}:latest
fi

if [ "${CMD}" == 'run' ];
then
    VERSION="latest" \
      docker-compose up
fi

if [ "${CMD}" == 'deploy' ];
then
    ecs-cli configure \
      --region "${aws_region_name}" \
      --cluster "${ecs_cluster_name}"

    VERSION="$(date +%Y%m%d%H%M)"

    docker tag ${IMAGE}:latest "${container_repository_uri}:$VERSION"

    docker push "${container_repository_uri}:$VERSION"

    VERSION="${VERSION}" \
    REGION="${aws_region_name}" \
      ecs-cli compose \
        --verbose \
        --project-name "${ecs_service}" \
        --ecs-params etc/ecs-params.yml \
      service up \
        --role "${ecs_task_exec_role}" \
        --target-group-arn "${elb_target_group}" \
        --container-name "proxy" \
        --container-port "${http_port_num}" \
        --timeout 0
fi

if [ "${CMD}" == 'logs' ];
then
    ecs-cli logs --since 10 --timestamps --follow
fi
