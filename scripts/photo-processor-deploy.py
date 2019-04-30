from logging import Logger, basicConfig, INFO, DEBUG, CRITICAL, debug, info, getLogger
from os import getenv, path
from sys import argv
from dotenv import load_dotenv
import boto3
from boto3.s3.transfer import S3Transfer

# Presumed to be run from the root of the project

APP_NAME='elektron-processor'
ROOT_FOLDER='elektron-processor-artifacts'

def deploy(archive):
  debug('Deploying lambda function for [%s]' % APP_NAME)
  load_env()

  archive_bucket = getenv('media_processor_artifact_bucket_name')
  artifact_name = '%s/%s' % (ROOT_FOLDER, path.basename(archive))

  upload_archive(archive_bucket, artifact_name, archive)
  add_function(archive_bucket, artifact_name, APP_NAME)

  info('Function created [%s]' % APP_NAME)


def load_env():
  env = getenv('ELEKTRON_ENV', 'development')
  env_file = "etc/env/%s.env" % env
  debug('Loading environment from [%s]' % env_file)
  load_dotenv(dotenv_path=env_file, verbose=True)


def upload_archive(archive_bucket, artifact_name, archive):
  s3 = boto3.client('s3')
  client = S3Transfer(client=s3)
  debug('Uploading function to [%s] as [%s].' % (archive_bucket, artifact_name))
  client.upload_file(archive, archive_bucket, artifact_name)
  info('Function archive uploaded [%s]' % APP_NAME)


def add_function(bucket, artifact_name, function_name):
  client = boto3.client('lambda')

  response = client.list_functions()
  for f in response['Functions']:
    if f['FunctionName'] == function_name:
      debug('Found existing function [%s].' % f['FunctionName'])
      client.delete_function(FunctionName=function_name)
      debug('Existing function [%s] deleted.' % f['FunctionName'])
      break

  db_jdbc_url = 'jdbc:postgresql://%s:%s/%s' % (getenv('db_hostname'), getenv("db_port_num"), getenv('db_name'))

  debug('Creating function for artifact [%s]' % artifact_name)
  client.create_function(
    FunctionName=function_name,
    Runtime='java8',
    Role=getenv('photo_processor_role_arn'),
    Handler='cc.roja.photo.ProcessorRequestHandler',
    Code={
      "S3Bucket": bucket,
      "S3Key": artifact_name
    },
    Description='Processes media.',
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
          'BUCKET_NAME': getenv('media_upload_bucket_name')
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
