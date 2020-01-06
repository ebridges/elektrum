## General Info

| **User Account** | **Description**                                         |
|------------------|---------------------------------------------------------|
| `elektrondba`    | Super-user account, created at the time db is created.  |
| `elektronusr`    | Non-privileged account, used by the application.        |


## Staging

### Install & Configure DB Objects

1. Run Ansible setup scripts to set up an RDS instance.
2. Review `etc/staging.env` to get DB connect info. Values are referenced here as variables below.
3. Log into one of the EC2 instances marked as "jump" boxes (db is not accessible outside VPC).
4. Confirm connectivity to RDS instance from jump box: `psql -h ${db_hostname} -U elektrondba -W ${db_name}` [password in vault]
5. As `elektrondba` create non-privileged user: `CREATE ROLE elektronusr NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;`
6. Set password for non-privileged user: `ALTER USER elektronusr WITH PASSWORD '${db_password}';` [password in vault]
7. Configure privileges for `elektronusr` and `elektrondba`:
```bash
psql --username=elektrondba --host ${db_hostname} --dbname=${db_name} --password << EOF
  GRANT ALL PRIVILEGES ON DATABASE ${db_name} TO elektronusr;
  ALTER ROLE elektronusr SET client_encoding TO 'utf8';
  ALTER ROLE elektronusr SET default_transaction_isolation TO 'read committed';
  ALTER ROLE elektronusr SET timezone TO 'UTC';

  ALTER ROLE elektrondba SET client_encoding TO 'utf8';
  ALTER ROLE elektrondba SET default_transaction_isolation TO 'read committed';
  ALTER ROLE elektrondba SET timezone TO 'UTC';
EOF
```

### Test Connectivity

1. Log into the container running the Django app.
2. Execute `apt-get update && apt-get install postgresql-client`
3. Run the following command: `psql -h <IP of Host Machine> -U elektronusr -W ${db_name}`
