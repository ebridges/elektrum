## General Info

| **User Account** | **Description**                                         |
|------------------|---------------------------------------------------------|
| `elektrondba`    | Super-user account, created at the time db is created.  |
| `elektronusr`    | Non-privileged account, used by the application.        |


## Development

### Install & Configure DB Objects

1.  `brew [install|upgrade] postgres`
2.  `brew postgresql-upgrade-database` [if upgraded]
3.  `brew services start postgresql`
     * `pg_ctl -D /usr/local/var/postgres -l logfile start`
4.  `createuser --superuser elektrondba -W` [password in vault]
5.  `source etc/development.env` [to get db name]
6.  `createuser --no-superuser elektronusr -W` [password in vault]
7.  `createdb ${db_name}`
8.  `psql --username=elektrondba --dbname=${db_name} -c "ALTER ROLE elektronusr SET client_encoding TO 'utf8';"`
9.  `psql --username=elektrondba --dbname=${db_name} -c "ALTER ROLE elektronusr SET default_transaction_isolation TO 'read committed';"`
10. `psql --username=elektrondba --dbname=${db_name} -c "ALTER ROLE elektronusr SET timezone TO 'UTC';"`
11. `psql --username=elektrondba --dbname=${db_name} -c "GRANT ALL PRIVILEGES ON DATABASE ${db_name} TO elektronusr;"`
12.  `psql --username=elektrondba --dbname=${db_name} -c "ALTER ROLE elektrondba SET client_encoding TO 'utf8';"`
13.  `psql --username=elektrondba --dbname=${db_name} -c "ALTER ROLE elektrondba SET default_transaction_isolation TO 'read committed';"`
14. `psql --username=elektrondba --dbname=${db_name} -c "ALTER ROLE elektrondba SET timezone TO 'UTC';"`

### Configure Connectivity

**A. Configure Postgres to listen on all network interfaces**

1. `sudo vi /usr/local/var/postgres/postgresql.conf`
2. Uncomment line `#listen_addresses = 'localhost'` and change to `listen_addresses = '*'` (listen on all address interfaces).  Note this isn't secure, if this is a concern add IP address(es) of client container.
3. Confirm the address it's listening on using: `sudo lsof -n -i -P | grep -i postgres` (MacOS).  It should say something like: `TCP *:5432 (LISTEN)`.

**B. Configure Postgres to allow network connections for our db**

1. `sudo vi /usr/local/var/postgres/pg_hba.conf`
2. Add these lines to the bottom:
    `host ${db_name}  elektronusr 0.0.0.0/0 md5`
    `host test_${db_name} elektronusr 0.0.0.0/0 md5`
    `host postgres elektronusr 0.0.0.0/0 md5`
    - This grants access for the `elektronusr` account to our database using a hashed password.
    - The second two statements are necessary for running tests.

**C. Test connectivity**

1. Log into the container running the Django app.
2. Execute `apt-get update && apt-get install postgresql-client`
3. Run the following command: `psql -h <IP of Host Machine> -U elektronusr -W ${db_name}`

### References

* https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04
* https://gist.github.com/MauricioMoraes/87d76577babd4e084cba70f63c04b07d
* https://www.ipaddressguide.com/cidr
* https://stackoverflow.com/questions/43762537/connect-docker-compose-to-external-database
* https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html
* https://dba.stackexchange.com/questions/83984/connect-to-postgresql-server-fatal-no-pg-hba-conf-entry-for-host
