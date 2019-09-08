function_name := TestLambda

## private-01, private-02 subnets
vpc_private_subnet_ids := subnet-0c80b35d50028313e,subnet-0bc1c1490b0963464

## staging-elektrum-vpc-public-sg
vpc_security_group_ids := sg-08499b1d7284cb6ac

role_arn := arn:aws:iam::169122179348:role/elektrum-staging-ZappaLambdaExecutionRole

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
