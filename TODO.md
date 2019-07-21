
-[ ] Configure postgres as database.
-[ ] Research designs for site.
-[ ] Research using s3 for storage backend.
-[ ] Create longterm google account for gmail auth.
-[ ] Expose an authenticated API for service
    -[ ] Django REST API
        - https://wsvincent.com/django-rest-framework-user-authentication-tutorial/
    -[ ] Configure behind AWS API Gateway
-[x] Set up production network
    -[x] configure pub/private subnets
    -[x] create database
    -[x] create load balancer
    -[x] configure container cluster
    -[x] configure service container
-[ ] set up bastion host
-[ ] [configure application deployment](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-basics.html)
    -[ ] configure/build docker container for app
    -[ ] push docker container to ecr
-[ ] Change sort media to write metadata to db
-[ ] scope storage of media in S3 to a user account
-[ ] design website


Sharing concepts
* my photos: show all photos by me
* my groups: show all photos shared with me
    * my family: show all photos shared by this group with me


## Zappa To-Do

* Only install non-dev deps in docker venv
* GDAL
    - Squash migrations to eliminate `django.contrib.gis` dep
    - Attempt to get it to compile successfully and bundle in docker image
* deployment script:
    - exec zappa deploy/update appropriately
* generate `zappa_settings.json` from `cfg` role in ansible playbook
* create IAM roles per env in ansible playbook






```
[ERROR] ImproperlyConfigured: Could not find the GDAL library (tried "gdal", "GDAL", "gdal2.3.0", "gdal2.2.0", "gdal2.1.0", "gdal2.0.0", "gdal1.11.0"). Is GDAL in    % '", "'.join(lib_names)/contrib/gis/gdal/libgdal.py", line 43, in <module>
```
https://github.com/django/django/blob/master/django/contrib/gis/gdal/libgdal.py#L39
https://github.com/joshtkehoe/lambda-python-gdal



Create role:
  - `elektron-development-ZappaLambdaExecutionRole`
```
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AttachNetworkInterface",
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DetachNetworkInterface",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ec2:ResetNetworkInterfaceAttribute"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:*"
            ],
            "Resource": "arn:aws:kinesis:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:*"
            ],
            "Resource": "arn:aws:sns:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:*"
            ],
            "Resource": "arn:aws:sqs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:*"
            ],
            "Resource": "arn:aws:dynamodb:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "route53:*"
            ],
            "Resource": "*"
        }
    ]
}
```

