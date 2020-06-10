from os import environ
from os.path import isfile
from sys import stdout, stderr
from glob import glob

from dotenv import load_dotenv
from doit import create_after
from doit.action import CmdAction

from elektrum.doit.task_actions import (
    envfile,
    environment,
    config_action,
    set_credentials,
    ThumbnailServiceInfo,
    ProcessorServiceInfo,
    ApplicationServiceInfo,
)

VERBOSITY = 1


# Hack
if not isfile(envfile()):
    actions = config_action()
    for action in actions:
        action.execute(out=stdout, err=stderr)


load_dotenv(envfile())
set_credentials('AWS_ACCESS_KEY_ID', 'aws_access_key')
set_credentials('AWS_SECRET_ACCESS_KEY', 'aws_secret_key')


def task_config():
    """Compile network, generate configuration"""
    file_deps = [f for f in glob('network/**', recursive=True) if isfile(f)]
    action = config_action()
    return {
        'targets': [envfile()],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': VERBOSITY,
    }


def task_build_processor_service():
    """Builds zip artifact for processor"""
    i = ProcessorServiceInfo()
    return {
        'targets': [i.target],
        'file_dep': i.build_deps(),
        'actions': i.build_action(),
        'verbosity': VERBOSITY,
        'task_dep': ['config'],
    }


def task_deploy_processor_service():
    """Deploys processor as an AWS lambda function"""
    i = ProcessorServiceInfo()
    args = {
        'PATH': environ['PATH'],
        'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_LAMBDA_NAME': environ['MEDIA_PROCESSOR_LAMBDA_NAME'],
        'AWS_LAMBDA_DESCRIPTION': environ['MEDIA_PROCESSOR_DESCRIPTION'],
        'AWS_LAMBDA_HANDLER': environ['MEDIA_PROCESSOR_LAMBDA_HANDLER'],
        'AWS_LAMBDA_ARCHIVE_BUCKET': environ['MEDIA_PROCESSOR_ARTIFACT_BUCKET_NAME'],
        'AWS_LAMBDA_ARCHIVE_KEY': i.archive,
        'AWS_LAMBDA_VPC_SUBNETS': environ['MEDIA_PROCESSOR_SUBNET_IDS'],
        'AWS_LAMBDA_VPC_SECURITY_GROUPS': environ['MEDIA_PROCESSOR_SECURITY_GROUPS'],
        'AWS_LAMBDA_TAGS': environ['MEDIA_PROCESSOR_TAGS'],
        'AWS_LAMBDA_ENVIRONMENT': environ['MEDIA_PROCESSOR_ENVIRONMENT'],
        'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['MEDIA_PROCESSOR_EXECUTION_ROLE_ARN'],
        'AWS_LAMBDA_MEMORY_SIZE': environ['MEDIA_PROCESSOR_MEMORY_SIZE'],
        'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['MEDIA_PROCESSOR_TIMEOUT'],
        'AWS_LAMBDA_RUNTIME': environ['MEDIA_PROCESSOR_RUNTIME'],
    }
    return {
        'file_dep': i.deploy_deps(),
        'actions': [CmdAction('lgw lambda-deploy --verbose', env=args)],
        'verbosity': VERBOSITY,
        'task_dep': ['build_processor_service'],
    }


def task_config_processor_service():
    """Update lambda configuration"""
    i = ProcessorServiceInfo()
    action = config_action('lam')
    return {
        'task_dep': ['deploy_processor_service'],
        'file_dep': i.config_deps(),
        'actions': action,
        'verbosity': VERBOSITY,
    }


@create_after(executed='config')
def task_build_application_service():
    i = ApplicationServiceInfo()

    args = {
        'PATH': environ['PATH'],
        'AWS_LAMBDA_ARCHIVE_CONTEXT_DIR': '.',  # needs to be cwd so that etc/env is availabe in docker context
        'AWS_LAMBDA_ARCHIVE_ADDL_FILES': f'{envfile()},$wkdir/.env;{i.versionfile},$wkdir;{i.requirements},$wkdir;{i.appdir}/,$wkdir',
        'AWS_LAMBDA_ARCHIVE_ADDL_PACKAGES': 'postgresql,postgresql-devel',
    }
    return {
        'file_dep': i.file_deps(),
        'targets': [i.target],
        'actions': [
            f'etc/bin/poetry2pip.py --file poetry.lock --output {i.requirements}',
            CmdAction('lgw lambda-archive --verbose', env=args),
        ],
        'verbosity': VERBOSITY,
    }


@create_after(executed='build_application_service')
def task_deploy_application_service():
    i = ApplicationServiceInfo()
    args = {
        'PATH': environ['PATH'],
        'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_LAMBDA_NAME': environ['APPLICATION_SERVICE_LAMBDA_NAME'],
        'AWS_LAMBDA_DESCRIPTION': environ['APPLICATION_SERVICE_DESCRIPTION'],
        'AWS_LAMBDA_HANDLER': environ['APPLICATION_SERVICE_LAMBDA_HANDLER'],
        'AWS_LAMBDA_ARCHIVE_BUCKET': environ['APPLICATION_SERVICE_ARTIFACT_BUCKET_NAME'],
        'AWS_LAMBDA_ARCHIVE_KEY': i.archive,
        'AWS_LAMBDA_VPC_SUBNETS': environ['APPLICATION_SERVICE_SUBNET_IDS'],
        'AWS_LAMBDA_VPC_SECURITY_GROUPS': environ['APPLICATION_SERVICE_SECURITY_GROUPS'],
        'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['APPLICATION_SERVICE_EXECUTION_ROLE_ARN'],
        'AWS_API_LAMBDA_INTEGRATION_ROLE': environ['APPLICATION_SERVICE_INTEGRATION_ROLE_ARN'],
        'AWS_API_NAME': environ['APPLICATION_SERVICE_API_NAME'],
        'AWS_API_DEPLOY_STAGE': environ['APPLICATION_SERVICE_API_DEPLOY_STAGE'],
        'AWS_API_DOMAIN_NAME': environ['APPLICATION_SERVICE_API_DOMAIN_NAME'],
        'AWS_ACM_CERTIFICATE_ARN': environ['APPLICATION_SERVICE_HTTPS_CERT_ARN'],
        'AWS_LAMBDA_TAGS': environ['APPLICATION_SERVICE_TAGS'],
        'AWS_LAMBDA_ENVIRONMENT': environ['APPLICATION_SERVICE_ENVIRONMENT'],
        'AWS_LAMBDA_MEMORY_SIZE': environ['APPLICATION_SERVICE_MEMORY_SIZE'],
        'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['APPLICATION_SERVICE_TIMEOUT'],
        'AWS_LAMBDA_RUNTIME': environ['APPLICATION_SERVICE_RUNTIME'],
        'AWS_API_DESCRIPTION': environ['APPLICATION_SERVICE_API_DESCRIPTION'],
    }
    return {
        'file_dep': [i.target, envfile()],
        'actions': [
            CmdAction(f'lgw lambda-deploy --verbose --lambda-file={i.target}', env=args),
            CmdAction('lgw gw-deploy --verbose', env=args),
            CmdAction('lgw domain-add --verbose', env=args),
        ],
        'verbosity': VERBOSITY,
        'task_dep': ['build_application_service'],
    }


@create_after(executed='config')
def task_build_thumbnail_service():
    i = ThumbnailServiceInfo()
    args = {
        'PATH': environ['PATH'],
        'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': i.builddir,
        'AWS_LAMBDA_ARCHIVE_BUNDLE_NAME': i.archive,
        'AWS_LAMBDA_ARCHIVE_CONTEXT_DIR': f'{i.appdir}/',  # trailing slash significant for populating docker image
        'AWS_LAMBDA_ARCHIVE_ADDL_FILES': 'src/,$wkdir;requirements.txt,$wkdir;version.txt,$wkdir',
    }
    return {
        'file_dep': i.build_deps(),
        'targets': [i.target],
        'actions': [
            f'etc/bin/poetry2pip.py --file "{i.appdir}/poetry.lock" --output {i.requirements}',
            CmdAction('lgw lambda-archive --verbose', env=args),
        ],
        'verbosity': VERBOSITY,
    }


def task_deploy_thumbnail_service():
    i = ThumbnailServiceInfo()
    args = {
        'PATH': environ['PATH'],
        'AWS_REGION': environ['AWS_REGION'],
        'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_LAMBDA_NAME': environ['THUMBNAIL_SERVICE_LAMBDA_NAME'],
        'AWS_LAMBDA_DESCRIPTION': environ['THUMBNAIL_SERVICE_DESCRIPTION'],
        'AWS_LAMBDA_HANDLER': environ['THUMBNAIL_SERVICE_LAMBDA_HANDLER'],
        'AWS_LAMBDA_ARCHIVE_BUCKET': environ['THUMBNAIL_SERVICE_ARTIFACT_BUCKET_NAME'],
        'AWS_LAMBDA_ARCHIVE_KEY': i.archive,
        'AWS_LAMBDA_VPC_SUBNETS': environ['THUMBNAIL_SERVICE_SUBNET_IDS'],
        'AWS_LAMBDA_VPC_SECURITY_GROUPS': environ['THUMBNAIL_SERVICE_SECURITY_GROUPS'],
        'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['THUMBNAIL_SERVICE_EXECUTION_ROLE_ARN'],
        'AWS_API_LAMBDA_INTEGRATION_ROLE': environ['THUMBNAIL_SERVICE_INTEGRATION_ROLE_ARN'],
        'AWS_API_NAME': environ['THUMBNAIL_SERVICE_API_NAME'],
        'AWS_API_DEPLOY_STAGE': environ['THUMBNAIL_SERVICE_API_DEPLOY_STAGE'],
        'AWS_API_DOMAIN_NAME': environ['THUMBNAIL_SERVICE_API_DOMAIN_NAME'],
        'AWS_ACM_CERTIFICATE_ARN': environ['THUMBNAIL_SERVICE_HTTPS_CERT_ARN'],
        'AWS_LAMBDA_TAGS': environ['THUMBNAIL_SERVICE_TAGS'],
        'AWS_LAMBDA_ENVIRONMENT': environ['THUMBNAIL_SERVICE_ENVIRONMENT'],
        'AWS_LAMBDA_MEMORY_SIZE': environ['THUMBNAIL_SERVICE_MEMORY_SIZE'],
        'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['THUMBNAIL_SERVICE_TIMEOUT'],
        'AWS_LAMBDA_RUNTIME': environ['THUMBNAIL_SERVICE_RUNTIME'],
        'AWS_API_BINARY_TYPES': environ['THUMBNAIL_SERVICE_BINARY_TYPES'],
        'AWS_API_RESPONSE_MODELS': environ['THUMBNAIL_SERVICE_RESPONSE_MODELS'],
        'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': i.builddir,
        'AWS_API_DESCRIPTION': environ['THUMBNAIL_SERVICE_API_DESCRIPTION'],
    }
    return {
        'file_dep': i.deploy_deps(),
        'actions': [
            CmdAction(f'lgw lambda-deploy --verbose --lambda-file={i.target}', env=args),
            CmdAction('lgw gw-deploy --verbose', env=args),
            CmdAction('lgw domain-add --verbose', env=args),
        ],
        'verbosity': VERBOSITY,
        'task_dep': ['build_thumbnail_service'],
    }
