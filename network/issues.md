
# Open Issues

-[ ] when creating an ec2 key pair register `key.private_key` as a var and save it to a file.

-[ ] generate and import an https certificate separately
        https://blog.confirm.ch/deploying-ssl-private-keys-with-ansible/
        https://vittegleo.com/post/letsencrypt-lambda-ssl/

-[ ] Installation of psql client on NAT instance

        sudo rpm -ivh --force https://yum.postgresql.org/testing/10/redhat/rhel-6-x86_64/postgresql10-libs-10.9-1PGDG.rhel6.x86_64.rpm
        sudo rpm -ivh --force https://yum.postgresql.org/testing/10/redhat/rhel-6-x86_64/postgresql10-10.9-1PGDG.rhel6.x86_64.rpm

-[ ] Lambda unable to download app archive from S3 bucket:

        [DEBUG]	2019-07-08T09:56:39.191Z	b17e-a8a4-4316-9c7a-7db6e4377469	Checking for DNS compatible bucket for: https://s3.amazonaws.com/archive.elektron.photos/staging_elektron_current_project.tar.gz
        [DEBUG]	2019-07-08T09:56:39.191Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	Not changing URI, bucket is not DNS compatible: archive.elektron.photos
        [DEBUG]	2019-07-08T09:56:39.191Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	CanonicalRequest:
        GET
        /archive.elektron.photos/staging_elektron_current_project.tar.gz

        host:s3.amazonaws.com
        x-amz-content-sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        x-amz-date:20190708T095639Z
        x-amz-security-token:AgoJb3JpZ2luX2VjEAIaCXVzLWVhc3QtMSJHMEUCIQD0p79JfuFxKuqdcoGfNGzUK08MGeXynyfnytJt4TLXaQIgRdC3Toby0Q4T74GODIBtq3F8eaiEX8BsUnqAiSLJyPIqjAIIWhAAGgwxNjkxMjIxNzkzNDgiDCQXDV16Wchh9LW3oSrpAfA441lpPzNp8X1oBnorXDjJZhWAkBBDhzwt3HAbdv3VMmmrzV3cX5296bQdSfxn50rtdg9HBikJKTZUR/e5VkK/Qa8uS0hkOTxKcOQrPEvsyrWZPYowlDkxNi1Mc6fLY/ssTxTrZqvie4e7S1EciSAgp0/r2dxz4J0WzIwrqwXUfnzyGL4T0rK3dHqT5Y/fpVMbdAtrqq+bYRcxB9iEShraDjAbw11yOZ+C6KTOqfBMSqNt4kdFVOP7gmOWw646gTN9r5LR6QayaH3Wpje0W5yGJMd1kr4ES31Fuw2uGhUewnRa9Dz4NtKiMJ+TjOkFOrQBCkiLXcfmNUhf3RJ4pctg9Tak6/rt4IyKmdzm8yywnSdAh8lHxkQ/TrwS+HrreMxZGB7Gl7D3whK+U0Vw+ug+zI/bbRMNZUWsgAXAZG9CS2VhJKxZ36imMa+J1A+1U8KgzPYOr6ccBKpt7QANgN8PKuOhYKoDYCbYwHrPwoienXarVH8MsD9LfB3npnJxxQdZe6vgSGEdxDfv/J2M1Jyyv2btN3kQHXxTZSNI88XSFPvjujHx

        host;x-amz-content-sha256;x-amz-date;x-amz-security-token
        e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        [DEBUG]	2019-07-08T09:56:39.191Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	StringToSign:
        AWS4-HMAC-SHA256
        20190708T095639Z
        20190708/us-east-1/s3/aws4_request
        e55fb8f76f744de15f99ee23ee34fbc8f5e7bed1f75706a5232b29535a659b65
        [DEBUG]	2019-07-08T09:56:39.192Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	Signature:
        d131598befe05db91a487d5808571163545c2a21d5aabe9564e43dfae248d7bf
        [DEBUG]	2019-07-08T09:56:39.192Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	Sending http request: <AWSPreparedRequest stream_output=True, method=GET, url=https://s3.amazonaws.com/archive.elektron.photos/staging_elektron_current_project.tar.gz, headers={'User-Agent': b'Boto3/1.9.164 Python/3.6.8 Linux/4.14.123-86.109.amzn1.x86_64 exec-env/AWS_Lambda_python3.6 Botocore/1.12.164 Resource', 'X-Amz-Date': b'20190708T095639Z', 'X-Amz-Security-Token': b'AgoJb3JpZ2luX2VjEAIaCXVzLWVhc3QtMSJHMEUCIQD0p79JfuFxKuqdcoGfNGzUK08MGeXynyfnytJt4TLXaQIgRdC3Toby0Q4T74GODIBtq3F8eaiEX8BsUnqAiSLJyPIqjAIIWhAAGgwxNjkxMjIxNzkzNDgiDCQXDV16Wchh9LW3oSrpAfA441lpPzNp8X1oBnorXDjJZhWAkBBDhzwt3HAbdv3VMmmrzV3cX5296bQdSfxn50rtdg9HBikJKTZUR/e5VkK/Qa8uS0hkOTxKcOQrPEvsyrWZPYowlDkxNi1Mc6fLY/ssTxTrZqvie4e7S1EciSAgp0/r2dxz4J0WzIwrqwXUfnzyGL4T0rK3dHqT5Y/fpVMbdAtrqq+bYRcxB9iEShraDjAbw11yOZ+C6KTOqfBMSqNt4kdFVOP7gmOWw646gTN9r5LR6QayaH3Wpje0W5yGJMd1kr4ES31Fuw2uGhUewnRa9Dz4NtKiMJ+TjOkFOrQBCkiLXcfmNUhf3RJ4pctg9Tak6/rt4IyKmdzm8yywnSdAh8lHxkQ/TrwS+HrreMxZGB7Gl7D3whK+U0Vw+ug+zI/bbRMNZUWsgAXAZG9CS2VhJKxZ36imMa+J1A+1U8KgzPYOr6ccBKpt7QANgN8PKuOhYKoDYCbYwHrPwoienXarVH8MsD9LfB3npnJxxQdZe6vgSGEdxDfv/J2M1Jyyv2btN3kQHXxTZSNI88XSFPvjujHx', 'X-Amz-Content-SHA256': b'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Authorization': b'AWS4-HMAC-SHA256 Credential=ASIASOYDXVEKKDYHF27Q/20190708/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date;x-amz-security-token, Signature=d131598befe05db91a487d5808571163545c2a21d5aabe9564e43dfae248d7bf'}>
        [DEBUG]	2019-07-08T09:56:39.193Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	Converted retries value: False -> Retry(total=False, connect=None, read=None, redirect=0, status=None)
        [DEBUG]	2019-07-08T09:56:39.193Z	9c44b17e-a8a4-4316-9c7a-7db6e4377469	Starting new HTTPS connection (1): s3.amazonaws.com:443
        END RequestId: 9c44b17e-a8a4-4316-9c7a-7db6e4377469
        REPORT RequestId: 9c44b17e-a8a4-4316-9c7a-7db6e4377469	Duration: 30031.11 ms	Billed Duration: 30000 ms 	Memory Size: 512 MB	Max Memory Used: 47 MB	
        2019-07-08T09:57:08.839Z 9c44b17e-a8a4-4316-9c7a-7db6e4377469 Task timed out after 30.03 seconds


      WGET doesn't work either
        ```
        $ wget --verbose https://s3.amazonaws.com/archive.elektron.photos/sting_elektron_current_project.tar.gz
        --2019-07-08 05:57:34--  https://s3.amazonaws.com/archive.elektron.photos/staging_elektron_current_project.tar.gz
        Resolving s3.amazonaws.com (s3.amazonaws.com)... 52.216.176.253
        Connecting to s3.amazonaws.com (s3.amazonaws.com)|52.216.176.253|:443... connected.
        HTTP request sent, awaiting response... 403 Forbidden
        2019-07-08 05:57:34 ERROR 403: Forbidden.
        ```

      Tried this policy:
        {
            "Version": "2012-10-17",
            "Id": "Policy1562579648891",
            "Statement": [
                {
                    "Sid": "Stmt1562579642455",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::169122179348:role/elektron-staging-ZappaLambdaExecutionRole"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::archive.elektron.photos/*",
                        "arn:aws:s3:::archive.elektron.photos"
                    ]
                }
            ]
        }

# Closed Issues

-[x] ensure nat instance names are unique across envs
-[x] hardcoded names `public-0x` and `private-0x` when creating security groups
-[x] issue creating rds instance

        TASK [rds : establish the RDS instance] *******************************************************************************************
        [WARNING]: The value False (type bool) in a string field was converted to 'False' (type string). If this does not look like what
        you expect, quote the entire value to ensure it does not change.

-[x] issue creating rds instance

        fatal: [localhost]: FAILED! => {"changed": false, "msg": "Failed to create instance: Invalid master user name"}

-[x] cannot create db user because instance is not reachable

-[x] AMI is not amzn-ami-vpc-nat
      - missing /etc/sysctl.d/10-nat-settings per https://docs.aws.amazon.com/vpc/latest/userguide/VPC_NAT_Instance.html#basics

-[x] split staging-elektron-vpc-public routing table into two: one per public subnet

-[x] split staging-elektron-vpc-nat-private routing table into two: one per private subnet

-[x] nat instances are not getting created in different availability zones
