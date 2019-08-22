#!/bin/sh

env=$1
source ../../etc/env/${env}.env
cat sample-data.csv | ./publish.pl | psql "postgresql://${db_username}:${db_password}@${db_hostname}:${db_port_num}/${db_name}"
