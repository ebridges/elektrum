from os import environ
from os.path import isfile
from sys import path, stdout, stderr
from glob import glob
from pathlib import Path

from dotenv import load_dotenv
from doit import create_after
from doit.action import CmdAction

from elektrum.doit.task_actions import (
    action_config,
    envfile,
    action_build_processor,
    set_credentials,
    environment,
    processor_archive,
    processor_version,
    application_version,
    ThumbnailServiceInfo,
)


if not isfile(envfile()):
    actions = action_config()
    for action in actions:
        action.execute(out=stdout, err=stderr)

load_dotenv(envfile())
set_credentials('AWS_ACCESS_KEY_ID', 'aws_access_key')
set_credentials('AWS_SECRET_ACCESS_KEY', 'aws_secret_key')


def task_config():
    """Compile network, generate configuration"""
    env = envfile()
    file_deps = [f for f in glob('network/**', recursive=True) if isfile(f)]
    action = action_config()
    return {'targets': [env], 'file_dep': file_deps, 'actions': action, 'verbosity': 2}


@create_after(executed='config')
def task_build_processor_service():
    """Builds zip artifact for processor"""
    archive = processor_archive()
    targets = f'functions/processor/build/archives/{archive}'
    file_deps = [f for f in glob('functions/processor/src/main/**', recursive=True) if isfile(f)]
    file_deps.append('functions/processor/version.txt')
    action = action_build_processor()
    return {
        'targets': [targets],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': 2,
        'task_dep': ['config'],
    }


@create_after(executed='build_processor_service')
def task_deploy_processor_service():
    """Deploys processor as an AWS lambda function"""

    archive = processor_archive()

    args = {
        'PATH': environ['PATH'],
        'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_LAMBDA_NAME': environ['MEDIA_PROCESSOR_LAMBDA_NAME'],
        'AWS_LAMBDA_DESCRIPTION': environ['MEDIA_PROCESSOR_DESCRIPTION'],
        'AWS_LAMBDA_HANDLER': environ['MEDIA_PROCESSOR_LAMBDA_HANDLER'],
        'AWS_LAMBDA_ARCHIVE_BUCKET': environ['MEDIA_PROCESSOR_ARTIFACT_BUCKET_NAME'],
        'AWS_LAMBDA_ARCHIVE_KEY': archive,
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
        'file_dep': [f'functions/processor/build/archives/{archive}', envfile()],
        'actions': [CmdAction('lgw lambda-deploy --verbose', env=args)],
        'verbosity': 2,
        'task_dep': ['build_processor_service'],
    }


def task_config_processor_service():
    """Update lambda configuration"""
    file_deps = [f for f in glob('network/roles/lam/**', recursive=True) if isfile(f)]
    action = action_config('lam')
    return {
        'task_dep': ['deploy_processor_service'],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': 2,
    }


@create_after(executed='config')
def task_build_application_service():
    env = envfile()
    application_dir = 'functions/application'
    versionfile = f'{application_dir}/version.txt'
    requirements = f'{application_dir}/requirements.txt'
    targets = ['build/lambda-bundle.zip']
    args = {
        'PATH': environ['PATH'],
        'AWS_LAMBDA_ARCHIVE_CONTEXT_DIR': '.',  # needs to be cwd so that etc/env is availabe in docker context
        'AWS_LAMBDA_ARCHIVE_ADDL_FILES': f'{env},$wkdir/.env;{versionfile},$wkdir;{requirements},$wkdir;{application_dir}/,$wkdir',
        'AWS_LAMBDA_ARCHIVE_ADDL_PACKAGES': 'postgresql,postgresql-devel',
    }
    return {
        'targets': targets,
        'actions': [
            f'etc/bin/poetry2pip.py --file poetry.lock --output {requirements}',
            CmdAction('lgw lambda-archive --verbose', env=args),
        ],
        'verbosity': 2,
    }


@create_after(executed='build_application_service')
def task_deploy_application_service():
    service = environ['SERVICE_NAME']
    env = environment()
    version = application_version()
    archive_key = f'{service}-{env}-{version}.zip'
    args = {
        'PATH': environ['PATH'],
        'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_LAMBDA_NAME': environ['APPLICATION_SERVICE_LAMBDA_NAME'],
        'AWS_LAMBDA_DESCRIPTION': environ['APPLICATION_SERVICE_DESCRIPTION'],
        'AWS_LAMBDA_HANDLER': environ['APPLICATION_SERVICE_LAMBDA_HANDLER'],
        'AWS_LAMBDA_ARCHIVE_BUCKET': environ['APPLICATION_SERVICE_ARTIFACT_BUCKET_NAME'],
        'AWS_LAMBDA_ARCHIVE_KEY': archive_key,
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
    }
    return {
        'file_dep': ['build/lambda-bundle.zip', envfile()],
        'actions': [
            CmdAction(
                'lgw lambda-deploy --verbose --lambda-file=build/lambda-bundle.zip', env=args
            ),
            CmdAction('lgw gw-deploy --verbose', env=args),
            CmdAction('lgw domain-add --verbose', env=args),
        ],
        'verbosity': 2,
        'task_dep': ['build_application_service'],
    }


@create_after(executed='config')
def task_build_thumbnail_service():
    i = ThumbnailServiceInfo()
    file_deps = [f for f in glob('functions/thumbnails/**', recursive=True) if isfile(f)]
    file_deps.append(envfile())
    requirements = f'{i.appdir}/requirements.txt'
    args = {
        'PATH': environ['PATH'],
        'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': i.builddir,
        'AWS_LAMBDA_ARCHIVE_BUNDLE_NAME': i.archive,
        'AWS_LAMBDA_ARCHIVE_CONTEXT_DIR': f'{i.appdir}/',  # trailing slash significant for populating docker image
        'AWS_LAMBDA_ARCHIVE_ADDL_FILES': 'src/,$wkdir;requirements.txt,$wkdir;version.txt,$wkdir',
    }
    return {
        'file_dep': file_deps,
        'targets': [i.target],
        'actions': [
            f'etc/bin/poetry2pip.py --file "{i.appdir}/poetry.lock" --output {requirements}',
            CmdAction('lgw lambda-archive --verbose', env=args),
        ],
        'verbosity': 2,
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
        'file_dep': [i.target, envfile()],
        'actions': [
            CmdAction(f'lgw lambda-deploy --verbose --lambda-file={i.target}', env=args),
            CmdAction('lgw gw-deploy --verbose', env=args),
            CmdAction('lgw domain-add --verbose', env=args),
        ],
        'verbosity': 2,
        'task_dep': ['build_thumbnail_service'],
    }
