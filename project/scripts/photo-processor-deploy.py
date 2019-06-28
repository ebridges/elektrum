from logging import Logger, basicConfig, INFO, DEBUG, CRITICAL, debug, info, error, getLogger
from os import getenv, path
from sys import argv, exit, exc_info
import dotenv
import boto3
from boto3.s3.transfer import S3Transfer
import argparse
from traceback import format_exc
from elektron.env_util import locate_env_file

# Presumed to be run from the root of the project

APP_NAME = 'elektron-processor'
ROOT_FOLDER = 'elektron-processor-artifacts'


def deploy(archive):
    debug('Deploying lambda function for [%s]' % APP_NAME)
    load_env()

    archive_bucket = getenv('media_processor_artifact_bucket_name')
    artifact_name = '%s/%s' % (ROOT_FOLDER, path.basename(archive))

    upload_archive(archive_bucket, artifact_name, archive)
    add_function(archive_bucket, artifact_name, APP_NAME)


def load_env():
    env_file = locate_env_file()
    dotenv.read_dotenv(env_file)
    info('Loaded environment from [%s]' % env_file)


def upload_archive(archive_bucket, artifact_name, archive):
    debug('Uploading artifact [%s] to bucket [%s] using archive [%s]' % (artifact_name, archive_bucket, archive))
    s3 = boto3.client('s3')
    client = S3Transfer(client=s3)
    client.upload_file(archive, archive_bucket, artifact_name)
    info('Function archive [%s] uploaded to bucket [%s]' % (artifact_name, archive_bucket))


def add_function(bucket, artifact_name, function_name):
    debug('adding function [%s] from artifact [%s]' % (function_name, artifact_name))
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
    info('Function [%s] created from artifact [%s]' % (function_name, artifact_name))


def configure_logging(threshold=INFO):
    print('level: %s' % threshold)
    basicConfig(
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=threshold)
    getLogger('botocore').setLevel(CRITICAL)
    getLogger('urllib3').setLevel(CRITICAL)
    getLogger('s3transfer').setLevel(CRITICAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy Elektron Photo Processor')
    parser.add_argument('--verbose', action="store_true", dest="verbose", default=False)
    parser.add_argument('--archive', action="store", dest="archive", required=True)
    args = parser.parse_args()

    try:
        level = DEBUG if args.verbose else INFO
        configure_logging(level)
        deploy(args.archive)
    except:
        error('%s: %s' % (exc_info()[0].__name__, exc_info()[1]))
        debug(format_exc())
        exit(1)
    else:
        exit(0)
