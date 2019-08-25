# How to Install Elektrum on AWS

## About

The `elektrum` application is a multi-tier system for hosting images and other media designed to be efficient and scalable.  Generally the steps involved in installing it are as follows:

1. Setup Project
1. Establish basic system prerequisites and configure parameters in a global settings file.
1. Configure permissions, a network, storage, security, and distribution mechanisms on AWS.
1. Generate a configuration file that can be used by the application.
1. Deploy the application.

## Platform Information

* Python 3.7
* Django 2.2
* Zappa 0.48.2
* PostgreSQL 11
* Ansible 2.8.2

## Local Setup

1. Ensure you have a version of Python 3.6 or 3.7 available.
1. Install Poetry

        $ curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

1. Invoke poetry shell:

        source  "$(dirname $(poetry run which python))/activate

1. Install project dependencies

        poetry install

1. Editor/IDE Setup
    * [VSCode](https://gist.github.com/ebridges/9e2e5a840c91c7a034c80e3e43dd3a9b0)
    * [PyCharm setup for test coverage](https://gist.github.com/ebridges/d1ebe05e9fd87e409f6e5c978e44bde1)
    * To run vscode from root of project and still have project setup work correctly, change `python.envFile` in VSCode settings (CMD-,) to `${workspaceFolder}/vscode.env`

## Steps to Install

### A. Prerequisites

#### A.1 Choose an Environment Name

* The environment name is used in many places so should be simple and easy to remember.  Use a single, lower-cased word: e.g. "development", or "testing".
* In this doc, this is referred to as `${env}`.

#### A.2 Region

* The application should be created & deployed to `us-east-1`.

#### A.3 Create a console user account

1. Create an IAM console user named `elektrum-${env}` (e.g. "elektrum-development") that has "Programmatic access".
1. The user should be added to a group that uses the `AdministratorAccess` policy.
1. Record the Access Key ID and the Secret Access Key.
1. You will probably want to create a separate user account as well, so you don't need to log in via the root account.

#### A.4 Generate a Public/Private Key Pair

1. Create a Keypair named `elektrum-${env}` (e.g. "elektrum-development").
1. Store the generated PEM file in a secure location.

#### A.5 Register a Domain Name & HTTPS Certificate

1. Choose a domain name to use with the system, and register it (e.g. `example.com`).
1. In Route53 create a Public Hosted Zone for this domain name.  Switch DNS records for your domain name to be Amazon's, as listed in the NS record for this hosted zone.
1. [Request a public certificate](https://console.aws.amazon.com/acm/home?region=us-east-1#/wizard/) for this domain name.  Add `*.example.com` as an additional domain name.
1. Choose "DNS Validation", and link the appropriate CNAME records to your domain name to do so.
1. Wait for the validation of the HTTPs certificate to complete.

#### A.6 Generate a Vault Password for storing secrets

* Generate a secure password and store it in `network/environments/${env}-vault-password.txt`.

### B. Create the System on AWS

#### B.1 AWS System Configuration

1. Edit `network/group_vars/${env}.yml` to provide values for `https_domain_name` and `application_domain_name`.
    * These values will typically be the same.  The only time they wouldn't be is if the application domain name is a subdomain (e.g. `staging.example.com`), as the HTTPS certificate will still be connected to `example.com`.
1. Generate encrypted versions of all secrets listed in the file.  The utility `tools/encrypt-var.sh` can assist with that.  Be sure to record the unencrypted secrets in a secure location.

#### B.2 Create the System & Generate Application Config

1. Change directory to the `network` subdirectory and run the below command.  It will take 20-30 minutes to complete running.

        $ ./run.sh ${env}

1. When the command has finished running, if there have been no errors then there will be an application configuration file located at: `etc/env/${env}.env`.

### C. Deploy the Application

1. Minimize and bundle up JS assets:

        $ make js-all

1. Bundle up static assets and publish them to S3:

        $ elektrum-deploy collectstatic ${env}

1. Generate necessary migrations:

        $ cd project
        $ python manage.py makemigrations

1. Create a VM that mimics the lambda execution environment:

        $ elektrum-deploy build ${env}

1. Deploy the application from the VM to AWS:

        $ elektrum-deploy deploy ${env}

    * Subsequent updates to the application should use `update` instead of `deploy`

1. Run the migrations created above by following the workaround in `Usage.md`

1. Visit the site at `https://${application_domain_name}`

### D. Running Locally

```
$ cd project
$ python manage.py runsslserver 127.0.0.1:8000
$ open https://127.0.0.1:8000
```

## Further Info

* https://romandc.com/zappa-django-guide

## Common Errors

<dl>
<dt><strong><tt>TypeError: 'NoneType' object is not callable</tt> when deploying to an environment</strong></dt>
<dd>
Causes can vary.
<br>
Check:
<li>Ensure host is in `ALLOWED_HOSTS` in the Django configuration.</li>
</dd>
<dt><strong><tt>
ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the DescribeLogStreams operation: The specified log group does not exist.</tt></strong>
</dt>
<dd>
<li>Ensure that API has permissions to log to Cloudwatch.
<br>
Add <tt>arn:aws:iam::743873495175:role/elektrum-development-ZappaLambdaExecutionRole</tt> to <kbd>API Gateway / Settings / CloudWatch log role ARN</kbd>
<br>
<a href="https://stackoverflow.com/a/50022932/87408">https://stackoverflow.com/a/50022932/87408</a>
</li>
</dd>
<dl>
