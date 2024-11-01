#!/bin/bash

# Exit on error
set -e

echo "Current working directory $(pwd)"
source .env

echo "Creating default site and social auth providers if necessary"
python manage.py shell <<EOF
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

import os

site_id = os.environ.get('SITE_ID')
site = Site.objects.get_or_create(id=site_id, defaults={'domain': 'localhost:8080', 'name': 'localhost'})

# Google provider, sourced from env
google_client_id = os.getenv('GOOGLE_CLIENT_ID', 'dummy-id')
google_secret = os.getenv('GOOGLE_CLIENT_SECRET', 'dummy-secret')

google_app, created = SocialApp.objects.get_or_create(
    provider='google',
    name='Google',
    defaults={
        'client_id': google_client_id,
        'secret': google_secret
    }
)
if created:
    google_app.sites.add(site)

# Add more providers as needed
EOF

DB_FILE="/app/application/db.sqlite3"

if [ ! -f "$DB_FILE" ] || [ ! -s "$DB_FILE" ]; then
    echo "Fresh database detected, applying all migrations..."
    python manage.py migrate --noinput
else
    echo "Existing database found, checking for pending migrations..."
    if python manage.py showmigrations | grep -q "\[ \]"; then
        echo "Found unapplied migrations, applying..."
        python manage.py migrate --noinput
    else
        echo "Database is up to date, no migrations needed"
    fi
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
# Execute the main command (Gunicorn)
exec "$@"
