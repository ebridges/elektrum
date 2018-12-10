#!/bin/sh
echo 'Collecting static files.'
python manage.py collectstatic --noinput
echo 'Making migrations.'
python manage.py makemigrations
echo 'Running migrations.'
python manage.py migrate
echo "Executing CMD: $@"
exec "$@"
