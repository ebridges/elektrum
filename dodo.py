from os import environ
from os.path import isfile
from sys import path
from glob import glob
from pathlib import Path

from dotenv import load_dotenv
from doit import run
from doit.action import CmdAction

from elektrum.doit.task_actions import (
    action_config,
    envfile,
    action_build_processor,
    set_credentials,
    environment,
    processor_archive,
    processor_version,
)


load_dotenv(envfile())
set_credentials('AWS_ACCESS_KEY_ID', 'aws_access_key')
set_credentials('AWS_SECRET_ACCESS_KEY', 'aws_secret_key')


def task_config():
    """Compile network, generate configuration"""
    env = envfile()
    file_deps = [f for f in glob('network/**', recursive=True) if isfile(f)]
    action = action_config()
    return {'targets': [env], 'file_dep': file_deps, 'actions': action, 'verbosity': 2}


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
        'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['MEDIA_PROCESSOR_ROLE_ARN'],
        'AWS_LAMBDA_MEMORY_SIZE': environ['MEDIA_PROCESSOR_MEMORY_SIZE'],
        'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['MEDIA_PROCESSOR_TIMEOUT'],
        'AWS_LAMBDA_RUNTIME': environ['MEDIA_PROCESSOR_RUNTIME'],
    }

    return {
        'file_dep': [f'functions/processor/build/archives/{archive}'],
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
