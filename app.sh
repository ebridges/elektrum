#!/usr/local/bin/bash

CMD=$1

if [ -z "${CMD}" ];
then
    echo "Usage: ${0}: [deploy-release|create-environment]"
    exit 0
fi

if [ 'deploy-release' == "${CMD}" ];
then
    current_branch=$(git branch | grep \* | cut -d ' ' -f2)
    if [ "${current_branch}" == 'master' ];
    then
	fullrelease
	if [ ! $? ];
	then
	    echo "Error bundling release."
	    exit $?
	fi
	eb deploy
	exit $?
    else
	echo "Current branch is not master: [${current_branch}]."
	exit 1
    fi
fi
   
if [ 'create-environment' == "${CMD}" ];
then
    ENV=$2
    if [ -z "${ENV}" ];
    then
	ENV=staging
    fi

    source etc/config.env

    ## TODO: raise error if environment already exists
    
    ## create environment
    eb create --verbose \
       --tags "Service=${service_name}" \
       --cname "${service_name}-${ENV}" \
       --vpc \
       --vpc.id "${vpc_id}" \
       --vpc.elbpublic \
       --vpc.publicip \
       --vpc.ec2subnets "${vpc_public_subnet_ids}" \
       --vpc.elbsubnets "${vpc_public_subnet_ids}" \
       --vpc.securitygroups "${vpc_security_group_ids}" \
       --elb-type applications \
       "${service_name}-${ENV}"

    exit $?
fi
