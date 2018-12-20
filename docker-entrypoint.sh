#!/bin/sh

if [ -z "${ELEKTRON_ENV}" ];
then
    echo 'ELEKTRON_ENV not found in environment'
    exit 1
fi

cd project
#echo 'Collecting static files.'
python manage.py collectstatic --noinput
#echo 'Making migrations.'
python manage.py makemigrations
#echo 'Running migrations.'
python manage.py migrate
#echo "Executing CMD: $@"
exec gunicorn --chdir elektron --bind :8000 elektron.wsgi:application
