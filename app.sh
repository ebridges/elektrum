#!/usr/local/bin/bash

CMD=$1
ENV=$2
if [ -z "${ENV}" ];
then
    # default environment
    ENV=staging
fi

source "etc/${ENV}.env"

ENV_NAME="${service_name}-${ENV}"

if [ -z "${CMD}" ];
then
    echo "Usage: ${0}: [deploy-release|create-environment]"
    exit 0
fi

if [ 'deploy-release' == "${CMD}" ];
then
    current_branch=$(git branch | grep \* | cut -d ' ' -f2)
    if [ "${current_branch}" != 'master' ];
    then
        echo "Current branch is not master: [${current_branch}]."
        exit 1
    fi
    
    echo "Running unit tests."
    pushd project
    python manage.py test
    popd
    result=$?
    echo "result: ${result}"
    if [ ! ${result} ];
    then
        echo "Error running unit tests."
        exit ${result}
    fi

    echo "Running integration test."
    ./integration_test.py
    result=$?
    echo "result: ${result}"
    if [ ! ${result} ];
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
        docker build -t roja/elektron:${version} .
        eb deploy --label "${version}" "${ENV_NAME}"
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
    eb create --verbose \
       --tags "Service=${service_name}" \
       --cname "${ENV_NAME}" \
       --vpc \
       --vpc.id "${vpc_id}" \
       --vpc.elbpublic \
       --vpc.publicip \
       --vpc.ec2subnets "${vpc_public_subnet_ids}" \
       --vpc.elbsubnets "${vpc_public_subnet_ids}" \
       --vpc.securitygroups "${vpc_security_group_ids}" \
       --elb-type application \
       "${ENV_NAME}"

    exit $?
fi
