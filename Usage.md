# Usage

## Setup VSCode

* To run vscode from root of project and still have project setup work correctly, change `python.envFile` in VSCode settings (CMD-,) to `${workspaceFolder}/vscode.env`

## Setup Project

1. Install Poetry
  `curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python`
1. Invoke poetry shell:
  `source  "$(dirname $(poetry run which python))/activate`
1. Install project dependencies
  `poetry install`

## Running Locally with Remote DB

_*Warning*: This requires the private key to be installed on the NAT._

1. Security Group: enable inbound access via NAT instance to port `5432` from local IP (e.g. home).
1. NAT Instance: edit `/etc/ssh/sshd_config` to ensure that the value of `GatewayPorts` is `yes`, running `sudo service ssh restart` if necessary.
1. NAT Instance: ensure the `roja-llc.pem` is available on the NAT instance.
1. NAT Instance: run the command `ssh -N -R 0.0.0.0:5432:elektron-db.cf3jqjy0lfne.us-east-1.rds.amazonaws.com:5432 -i [/path/to/roja-llc.pem] ec2-user@127.0.0.1`
1. Test: `psql -h [nat instance subdomain].compute-1.amazonaws.com -U elektronusr -W`
1. Local: Open a shell in the VM `./elektron-deploy shell`
1. Local: update `~/project/.env` to use hostname of NAT instance as value of `db_hostname`
1. Local: run `python manage.py migrate` if necessary.
1. Local: run `python manage.py runserver 0.0.0.0:8000` from `~/project`.
