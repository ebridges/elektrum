import os

DEFAULT_ENV='development'
elektron_env = os.getenv('ELEKTRON_ENV', DEFAULT_ENV)

if elektron_env == 'staging':
    from .staging import *

if elektron_env == 'development':
    from .development import *

if not elektron_env or elektron_env == 'production':
    from .production import *
