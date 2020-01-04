# How to Install Elektrum on AWS

## Local Setup

1. Ensure you have a version of Python 3.7 available.
1. Install Poetry

        $ curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

1. Invoke poetry shell:

        source  "$(dirname $(poetry run which python))/activate

1. Install project dependencies

        poetry install

1. Editor/IDE Setup
    * [VSCode](https://gist.github.com/ebridges/9e2e5a840c91c7a034c80e3e43dd3a9b0)
    * [PyCharm setup for test coverage](https://gist.github.com/ebridges/d1ebe05e9fd87e409f6e5c978e44bde1)
    * To run vscode from root of project and still have project setup work correctly, change the `python.envFile` setting in VSCode settings (CMD-,) to `${workspaceFolder}/vscode.env`

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

1. Edit `network/group_vars/${env}.yml` to provide values for `https_domain_name` and `APPLICATION_DOMAIN_NAME`.
    * These values will typically be the same.  The only time they wouldn't be is if the application domain name is a subdomain (e.g. `staging.example.com`), as the HTTPS certificate will still be connected to `example.com`.
1. Generate encrypted versions of all secrets listed in the file.  The utility `tools/encrypt-var.sh` can assist with that.  Be sure to record the unencrypted secrets in a secure location.

#### B.2 Create the System & Generate Application Config

1. Change directory to the `network` subdirectory and run the below command.  It will take 20-30 minutes to complete running.

        $ ./run.sh ${env}

1. When the command has finished running, if there have been no errors then there will be an application configuration file located at: `etc/env/${env}.env`.


> ❗**Note** for Known Issues see [ISSUES.md](./ISSUES.md)

### C. Deploy the Application

1. Change directory to the root level of the project (where this file is located).

1. Deploy the application:

        $ ./elektrum-deploy ${env}

    - Builds a VM that mimics the lambda env, and deploys the application to that.
    - Configures API gateway to point to the application's lambda.
    - Links the application's domain name with this gateway.
    - Publishes static assets to S3.

1. [Optional] Generate necessary migrations:

        $ ./elektrum-deploy migrate ${env}

1. Visit the site at `https://${APPLICATION_DOMAIN_NAME}`

### D. Configure Django

#### D.1 Run Migrations

        $ ./elektrum-deploy ${env} migrate

#### D.2 Create the Django Admin User

        $ ./elektrum-deploy ${env} admin-user

    - Credentials are pulled from `network/group_vars/${env}.yml`

#### D.3 Setup Google OAuth

1. Visit site's admin panel at `https://${APPLICATION_DOMAIN_NAME}/admin`
1. Log in using the credentials for the admin user.
1. Update the "Site" entity to use `${application_domain_name}`.
1. Configure Google Auth credentials via Google's Developer Console.
1. Add a Social Application for Google authentication, and configure with Google Auth credentials.

* More info: https://wsvincent.com/django-allauth-tutorial-custom-user-model/#google-credentials

### Miscellaneous

#### Running Locally

```
$ cd project
$ python manage.py runsslserver 127.0.0.1:8000
$ open https://127.0.0.1:8000
```

<!-- #### Accessing Remote DB

This involves configuring a NAT server as a Bastion host, to proxy the DB connection to the RDS instance (which isn't publicly available by default).

_*Warning*: This requires the private key to be installed on the NAT._

1. Security Group: enable inbound access via NAT instance to port `5432` from local IP (e.g. home) in security groups:
    * `elektrum-${env}-vpc-nat-sg`
    * `elektrum-${env}-vpc-public-sg`
1. NAT Instance: edit `/etc/ssh/sshd_config` to ensure that the value of `GatewayPorts` is `yes`, running `sudo service sshd restart` if necessary.
1. NAT Instance: ensure the `elektrum-${env}.pem` is available on the NAT instance.
1. NAT Instance: run the command `ssh -N -R 0.0.0.0:5432:${DB_HOSTNAME}:5432 -i [/path/to/elektrum-${env}.pem] ec2-user@127.0.0.1`
1. Test: `psql -h [nat instance subdomain].compute-1.amazonaws.com -U ${DB_USERNAME} -W`

### Running server locally on VM

1. Configure remote access to the database (see "Accessing Remote DB" above).
1. Local: Open a shell in the VM `./elektrum-deploy shell`
1. Local: update `~/project/.env` to use hostname of NAT instance as value of `DB_HOSTNAME`
1. Local: run `python manage.py runsslserver 0.0.0.0:8000` from `~/project`.
1. Local: `curl https://127.0.0.1:8000/`. -->

## Common Errors

* See [ISSUES.md](./ISSUES.md)
