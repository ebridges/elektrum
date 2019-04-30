from logging import Logger, basicConfig, INFO, DEBUG, CRITICAL, debug, info, getLogger
from json import dumps
from os import getenv
from sys import argv
from dotenv import load_dotenv
import boto3

# Presumed to be run from the root of the project

APP_NAME='elektron-processor'

def deploy(archive):
  debug('Deploying lambda function for [%s]' % APP_NAME)
  client = boto3.client('lambda')
  response = client.list_functions()
  for f in response['Functions']:
    if f['FunctionName'] == APP_NAME:
      debug('Found existing function [%s].' % f['FunctionName'])
      client.delete_function(FunctionName=APP_NAME)
      debug('Existing function [%s] deleted.' % f['FunctionName'])
      break
  create_function(client, archive)
  info('Function created [%s]' % APP_NAME)


def create_function(client, archive):
  env = getenv('ELEKTRON_ENV', 'development')
  env_file = "etc/env/%s.env" % env
  debug('Loading environment from [%s]' % env_file)
  load_dotenv(dotenv_path=env_file, verbose=True)

  db_jdbc_url = 'jdbc:postgresql://%s:%s/%s' % (getenv('db_hostname'), getenv("db_port_num"), getenv('db_name'))

  debug('Uploading archive [%s]' % archive)
  with open(archive, "rb") as binaryfile :
    zipfile = bytearray(binaryfile.read())
    client.create_function(
      FunctionName=APP_NAME, 
      Runtime='java8', 
      Role=getenv('photo_processor_role_arn'),
      Handler='cc.roja.photo.ProcessorRequestHandler',
      Code={ 'ZipFile': zipfile },
      Description='Processes photos.',
      Timeout=int(getenv('connection_timeout')),
      MemorySize=int(getenv('memory_size')),
      Publish=True,
      VpcConfig={
          'SubnetIds': getenv('vpc_public_subnet_ids').split(','),
          'SecurityGroupIds': getenv('vpc_security_group_ids').split(',')
      },
      Environment={
        'Variables': {
            'DB_JDBC_URL': db_jdbc_url,
            'DB_USERNAME': getenv('db_username'),
            'DB_PASSWORD': getenv('db_password'),
            'BUCKET_NAME': getenv('bucket_name')
        }
      }
    )


def configure_logging(threshold=INFO):
  basicConfig(
      format='[%(asctime)s][%(levelname)s] [%(name)s] %(message)s',
      datefmt='%Y/%m/%d %H:%M:%S',
      level=threshold)
  getLogger('botocore.credentials').setLevel(CRITICAL)


if __name__ == "__main__":
  if len(argv) > 2:
    configure_logging(DEBUG)
  else:
    configure_logging()
  deploy(argv[1])
