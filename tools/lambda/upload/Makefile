include ../../../etc/env/development.env
export

function_name := TestUploadLambda

upload_file := 2020-02-01T10.16.41.jpg


output := /dev/null

comma:= ,
list := $(subst $(comma), ,$(AWS_LAMBDA_VPC_SUBNETS))
subnets = $(word $(words $(list)), $(list))

vpc_config := '{ "SubnetIds": ["$(call subnets,$*,1)", "$(call subnets,$*,2)"], "SecurityGroupIds": ["$(AWS_LAMBDA_VPC_SECURITY_GROUPS)"] }'

build:
	@zip app.zip lambda.py upload_photo.py

create:
	@aws lambda create-function \
		--function-name $(function_name) \
		--runtime python3.7 \
		--zip-file fileb://app.zip \
		--handler lambda.handler  \
		--role $(AWS_LAMBDA_EXECUTION_ROLE_ARN) \
		--vpc-config $(vpc_config)

delete:
	@aws lambda delete-function \
		--function-name $(function_name)

invoke:
	@aws --output json lambda invoke \
		--function-name $(function_name) \
		--payload '{"bucket": "$(MEDIA_UPLOAD_BUCKET_NAME)", "filename": "$(upload_file)"}' \
		--log-type Tail \
		$(output) | jq --raw-output .LogResult | base64 --input=- --decode
