#!/bin/bash

# Exit on error
set -e

source .env

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating default site..."
python manage.py shell <<EOF
from django.contrib.sites.models import Site
import os
site_id = os.environ.get('SITE_ID')
Site.objects.get_or_create(id=site_id, defaults={'domain': 'localhost:8080', 'name': 'localhost'})
EOF

echo "Setting up social authentication providers..."
python manage.py shell <<EOF
import os
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Get the default site
site_id = os.environ.get('SITE_ID')
site = Site.objects.get(id=site_id)

# Google provider
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

echo "Starting application..."
# Execute the main command (Gunicorn)
exec "$@"
