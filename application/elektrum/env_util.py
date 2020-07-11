import os
import logging
from pathlib import Path

DEBUG_ENVIRONMENT_LOADING_VAR = 'ELEKTRUM_DEBUG_ENV_LOADING'

debug_logging = 'DEBUG' if os.getenv(DEBUG_ENVIRONMENT_LOADING_VAR) else 'INFO'

logging.basicConfig(
    level=debug_logging, format='[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_ENV = 'local'


def locate_env_file(start_dir=os.getcwd()):
    logger.debug('Begin looking for environment in: %s' % start_dir)

    # check in current directory for `.env`
    location = os.path.join(start_dir, '.env')
    logger.debug('Looking for env file in %s' % location)
    if os.path.isfile(location):
        logger.info('Located env file in %s' % location)
        return location

    # check in parent, parent etc/env directory for `$OPERATING_ENV.env`
    grandparent = Path(start_dir).parents[0]
    location = os.path.join(grandparent, 'etc/env/%s.env' % os.getenv('OPERATING_ENV', DEFAULT_ENV))
    logger.debug('Looking for env file in %s' % location)
    if os.path.isfile(location):
        logger.info('Located env file in %s' % location)
        return location

    raise FileNotFoundError('Unable to locate env configuration file.')


def resolve_version(start_dir=os.getcwd()):
    logger.debug('Begin looking for version file in: %s' % start_dir)

    location = os.path.join(start_dir, 'version.txt')
    logger.debug('Looking for version file in %s' % location)
    if os.path.isfile(location):
        logger.info('Located version file in %s' % location)
        return location

    grandparent = Path(start_dir).parents[1]
    location = os.path.join(grandparent, 'version.txt')
    logger.debug('Looking for version file in %s' % location)
    if os.path.isfile(location):
        logger.info('Located version file in %s' % location)
        return location

    raise FileNotFoundError('Unable to locate version file.')
