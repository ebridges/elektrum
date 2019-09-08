function_name := TestJavaLambda

## private-01, private-02 subnets
vpc_private_subnet_ids := subnet-00aa21fba3d2dab7e,subnet-0927062525f777534

## staging-elektrum-vpc-public-sg
vpc_security_group_ids := sg-0ec0f0a88e865b635

role_arn := arn:aws:iam::743873495175:role/elektrum-development-ZappaLambdaExecutionRole

output := /dev/null

clean:
	@/bin/rm -rf build

build:
	@gradle buildZip
	@mkdir build/tmp/zipFile
	@unzip build/archives/java.zip -d build/tmp/zipFile
	@rm -rf build/tmp/zipFile/lib
	@wget https://github.com/ebridges/archive/blob/master/lib.tar.gz?raw=true -O - | tar xzf - -C build/tmp/zipFile
	@rm build/archives/java.zip
	@jar cf build/archives/java.zip -C build/tmp/zipFile .

create:
	@aws --profile elektrum-development --region us-east-1 \
		lambda create-function \
		--function-name $(function_name) \
		--runtime java8 \
		--zip-file fileb://build/archives/java.zip \
		--handler lambda.Handler  \
		--role $(role_arn) \
		--vpc-config "SubnetIds=$(vpc_private_subnet_ids),SecurityGroupIds=$(vpc_security_group_ids)"

delete:
	@aws --profile elektrum-development --region us-east-1 \
		lambda delete-function \
		--function-name $(function_name)

invoke:
	@aws --profile elektrum-development --region us-east-1 \
		--output json lambda invoke \
		--function-name $(function_name) \
		--log-type Tail \
		$(output) | jq --raw-output .LogResult | base64 --input=- --decode
