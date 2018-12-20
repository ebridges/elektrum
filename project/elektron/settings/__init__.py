import os

env = os.getenv('ELEKTRON_ENV', 'production')

if env == 'staging':
    from .staging import *

if env == 'development':
    from .development import *

if not env or env == 'production':
    from .production import *
