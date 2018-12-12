#!/bin/sh

if [ -z "${ELEKTRON_ENV}" ];
then
  . etc/config.env
fi

cd project
echo 'Collecting static files.'
python manage.py collectstatic --noinput
echo 'Making migrations.'
python manage.py makemigrations
echo 'Running migrations.'
python manage.py migrate
echo "Executing CMD: $@"
exec "$@"
