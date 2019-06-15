#!/usr/bin/env bash

CMD=$1
ARG=$2

if [ -z "${CMD}" ];
then
    echo "Usage: ${0}: deploy-release [-f]"
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

    echo "Running smoke test in dev environment."
    docker build --file Dockerfile-Proxy --tag roja/elektron_proxy:latest .
    docker build --file Dockerfile-App --build-arg="ELEKTRON_ENV=development" --tag roja/elektron_app:latest .
    ELEKTRON_ENV=development ./scripts/tests/smoke_test.py
    result=$?
    if [ "${result}" != "0" ];
    then
        echo "Error running smoke test."
        exit ${result}
    fi

    read -n1 -rsp $'Press any key to continue with tagging release or Ctrl+C to exit...\n' key
    
    declare version
    if [ "$key" = '' ]; then
        version=$(cat ./version.txt | sed 's/\.dev0//')
        fullrelease --verbose --no-input
        result=$?
        if [ "${result}" -ne "0" ];
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

        make all VERSION=${version}
        processor_archive=`find processor -name 'elektron-processor*.zip'`
        echo "Deploying new version of image processor at version ${version} from ${processor_archive}"
        ELEKTRON_ENV=${ELEKTRON_ENV} python3 scripts/photo-processor-deploy.py --archive=${processor_archive}
        result=$?
        if [ "${result}" -ne "0" ];
        then
            echo "ERROR: building/deploying photo processor archive was unsuccessful."
            exit ${result}
        fi

        IFS=', ' read -r -a subnets <<< ${vpc_private_subnet_ids}
        subnet_list=''
        for element in "${subnets[@]}"
        do
            if [ -z "${subnet_list}" ];
            then
                subnet_list="\"${element}\""
            else
                subnet_list="${subnet_list}, \"${element}\""
            fi
        done

        IFS=', ' read -r -a secgroups <<< ${vpc_nat_security_group_ids}
        secgrp_list=''
        for element in "${secgroups[@]}"
        do
            if [ -z "${secgrp_list}" ];
            then
                secgrp_list="\"${element}\""
            else
                secgrp_list="${secgrp_list}, \"${element}\""
            fi
        done

	    echo "Deploying ${version} to ${ELEKTRON_ENV} using the following settings:"
        cat <<- EOF > project/zappa_settings.json
		{
			"${ELEKTRON_ENV}": {
				"aws_region": "${aws_region}",
				"django_settings": "${service_name}.settings",
				"project_name": "${service_name}",
				"runtime": "python3.6",
				"s3_bucket": "${media_processor_artifact_bucket_name}",
				"slim_handler": true,
				"environment_variables": {
					"ELEKTRON_ENV": "${ELEKTRON_ENV}",
					"APP_VERSION": "${version}"
				},
				"vpc_config": {
					"SubnetIds": [ ${subnet_list} ],
					"SecurityGroupIds": [ ${secgrp_list} ]
				},
			}
		}
		EOF

        cat project/zappa_settings.json

        echo "Building a fresh image of elektron_zappa for ${ELEKTRON_ENV} at version ${version}"
        docker build \
            --build-arg="ELEKTRON_ENV=${ELEKTRON_ENV}"  \
            --tag roja/elektron_zappa:${version} .


        `aws --output text lambda list-functions | grep ${service_name}-${ELEKTRON_ENV} > /dev/null 2>&1`

        if [ $? == 0 ];
        then
            echo "Running 'zappa update ${ELEKTRON_ENV}' for v${version}'"
            docker run \
                --env AWS_SECRET_ACCESS_KEY \
                --env AWS_ACCESS_KEY_ID \
                --env ELEKTRON_ENV=${ELEKTRON_ENV} \
                roja/elektron_zappa:${version} \
                bash --login -c "cd project && zappa update ${ELEKTRON_ENV}"
        else
            echo "Running 'zappa deploy ${ELEKTRON_ENV}' for v${version}'"
            docker run \
                --env AWS_SECRET_ACCESS_KEY \
                --env AWS_ACCESS_KEY_ID \
                --env ELEKTRON_ENV=${ELEKTRON_ENV} \
                roja/elektron_zappa:${version} \
                bash --login -c "cd project && zappa deploy ${ELEKTRON_ENV}"
        fi

        rm project/zappa_settings.json

        git checkout master
        exit $?
    else
        # Anything else pressed, do whatever else.
        # echo [$key] not empty
        echo 'Deploy cancelled.'
        exit 0
    fi
fi
