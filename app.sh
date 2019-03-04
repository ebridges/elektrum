#!/usr/local/bin/bash

CMD=$1
ARG=$2

if [ -z "${CMD}" ];
then
    echo "Usage: ${0}: [deploy-release|create-environment] [-f]"
    exit 0
fi

if [ -z "${ELEKTRON_ENV}" ];
then
    # default environment
    ELEKTRON_ENV=staging
fi

if [ ! -f "./etc/env/${ELEKTRON_ENV}.env" ];
then
    echo "Generating configuration for ${ELEKTRON_ENV}"
    pushd network
    ./run.sh --tags=common,cfg
    popd
else
    echo "Configuration already exists for ${ELEKTRON_ENV}"
fi

source "./etc/env/${ELEKTRON_ENV}.env" || (echo "Error: config for ${ELEKTRON_ENV} not found" && exit 1)

ENV_NAME="${service_name}-${ELEKTRON_ENV}"

if [ 'deploy-release' == "${CMD}" ];
then
    echo "Running deploy for ${ENV_NAME}"

    current_branch=$(git branch | grep \* | cut -d ' ' -f2)
    if [ "${current_branch}" != 'master' ];
    then
        if [ "${ARG}" != '-f' ];
        then
            echo "Current branch is not master: [${current_branch}]."
            exit 1
        fi
    fi
    
    echo "Running unit tests in development env."
    pushd project
    ELEKTRON_ENV=development python manage.py test
    result=$?
    popd
    if [ "${result}" != "0" ];
    then
        echo "Error running unit tests."
        exit ${result}
    fi

    echo "Running integration test in dev environment."
    docker build --file Dockerfile-Proxy --tag roja/elektron_proxy:latest .
    docker build --file Dockerfile-App --build-arg="ELEKTRON_ENV=development" --tag roja/elektron_app:latest .
    ELEKTRON_ENV=development ./integration_test.py
    result=$?
    if [ "${result}" != "0" ];
    then
        echo "Error running integration test."
        exit ${result}
    fi

    read -n1 -rsp $'Press any key to continue with tagging release or Ctrl+C to exit...\n' key
    
    declare version
    if [ "$key" = '' ]; then
        version=$(cat ./version.txt | sed 's/\.dev0//')
        fullrelease --verbose --no-input
        result=$?
        if [ ! ${result} ];
        then
            echo "Error bundling release."
            exit ${result}
        fi
    else
        echo 'Deploy cancelled.'
        exit 0
    fi

    if [ -z "${version}" ];
    then
        echo "Version not set."
        exit 1
    else
        echo "${version} ready for deploy."
    fi

    read -n1 -rsp $'Press any key to continue with deploy or Ctrl+C to exit...\n' key

    if [ "$key" = '' ]; then
        # key pressed, do something
        # echo [$key] is pressed # uncomment to trace
        echo "Release tagging successful, deploying application version ${version}"
        git checkout ${version}

        $(aws ecr get-login --no-include-email --region us-east-1)

        echo "Building a fresh image of Dockerfile-Proxy for ${ELEKTRON_ENV} at version ${version}"
        docker build --file Dockerfile-Proxy --tag roja/elektron_proxy:${version} .
        docker tag roja/elektron_proxy:${version} ${ecr_host}/roja/elektron_proxy:${version}
        docker push ${ecr_host}/roja/elektron_proxy:${version}
        tmp=$(mktemp)
        cat Dockerrun.aws.json | sed "s/roja\/elektron_proxy:latest/${ecr_host}\/roja\/elektron_proxy:${version}/" > "$tmp" && mv "$tmp" Dockerrun.aws.json

        echo "Building a fresh image of Dockerfile-App for ${ELEKTRON_ENV} at version ${version}"
        docker build --file Dockerfile-App --build-arg="ELEKTRON_ENV=${ELEKTRON_ENV}" --tag roja/elektron_app:${version} .
        docker tag roja/elektron_app:${version} ${ecr_host}/roja/elektron_app:${version}
        docker push ${ecr_host}/roja/elektron_app:${version}
        tmp=$(mktemp)
        cat Dockerrun.aws.json | sed "s/roja\/elektron_app:latest/${ecr_host}\/roja\/elektron_app:${version}/" > "$tmp" && mv "$tmp" Dockerrun.aws.json

        eb deploy "${ENV_NAME}"

        git checkout -- Dockerrun.aws.json
        git checkout master
        exit $?
    else
        # Anything else pressed, do whatever else.
        # echo [$key] not empty
        echo 'Deploy cancelled.'
        exit 0
    fi
fi
   
if [ 'create-environment' == "${CMD}" ];
then
    ## TODO: raise error if environment already exists
    
    ## create environment
    echo "Creating new environment: ${ENV_NAME}"
    eb create --verbose \
       --tags "Service=${service_name}" \
       --platform "multi-container-docker-18.06.1-ce-(generic)" \
       --cname "${ENV_NAME}" \
       --vpc \
       --vpc.id "${vpc_id}" \
       --vpc.elbpublic \
       --vpc.publicip \
       --vpc.ec2subnets "${vpc_public_subnet_ids}" \
       --vpc.elbsubnets "${vpc_public_subnet_ids}" \
       --vpc.securitygroups "${vpc_security_group_ids}" \
       --elb-type application \
       --envvars "ELEKTRON_ENV=${ELEKTRON_ENV}" \
       "${ENV_NAME}"

    exit $?
fi
