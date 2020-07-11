include ../../../etc/env/development.env
export

function_name := TestLambda

## private-01, private-02 subnets
vpc_private_subnet_ids := "${MEDIA_PROCESSOR_SUBNET_IDS}"

## staging-elektrum-vpc-public-sg
vpc_security_group_ids := "${MEDIA_PROCESSOR_SECURITY_GROUPS}"

role_arn := ${MEDIA_PROCESSOR_EXECUTION_ROLE_ARN}

output := /dev/null

build:
	@zip app.zip lambda.py

create:
	@aws lambda create-function \
		--function-name $(function_name) \
		--runtime python3.7 \
		--zip-file fileb://app.zip \
		--handler lambda.handler  \
		--role $(role_arn) \
		--vpc-config "SubnetIds=$(vpc_private_subnet_ids),SecurityGroupIds=$(vpc_security_group_ids)"

delete:
	@aws lambda delete-function \
		--function-name $(function_name)

invoke:
	@aws --output json lambda invoke \
		--function-name $(function_name) \
		--log-type Tail \
		$(output) | jq --raw-output .LogResult | base64 --input=- --decode
