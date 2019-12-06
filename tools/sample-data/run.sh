#!/bin/sh

env=$1
source ../../etc/env/${env}.env
cat sample-data.csv | ./publish.pl | psql "postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOSTNAME}:${DB_PORT_NUM}/${DB_NAME}"
