import os

DEFAULT_ENV='development'

def locate_env_file(start_dir):
  #print('start_dir: %s' % start_dir)

  # check in current directory for `.env`
  location = os.path.join(start_dir, '.env')
  #print('Looking for env file in %s' % location)
  if os.path.isfile(location):
    print('[INFO] Located env file in %s' % location)
    return location

  # check in parent, parent directory for `.env`
  location = os.path.join(os.path.dirname(start_dir), '.env')
  #print('Looking for env file in %s' % location)
  if os.path.isfile(location):
    print('[INFO] Located env file in %s' % location)
    return location
  
  # check in parent, parent etc/env directory for `$ELEKTRON_ENV.env`
  location = os.path.join(os.path.dirname(start_dir), 'etc/env/%s.env' % os.getenv('ELEKTRON_ENV', DEFAULT_ENV))
  #print('Looking for env file in %s' % location)
  if os.path.isfile(location):
    print('[INFO] Located env file in %s' % location)
    return location
  
  raise FileNotFoundError('Unable to locate env configuration file.')
