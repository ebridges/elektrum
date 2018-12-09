import os

if os.environ['ELEKTRON_ENV'] == 'staging':
    from .staging import *

if os.environ['ELEKTRON_ENV'] == 'development':
    from .development import *

from .production import *

