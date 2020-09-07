from os import environ
from os.path import isfile
from sys import stdout, stderr
from glob import glob

from dotenv import load_dotenv
from doit.action import CmdAction
from doit.tools import result_dep

from elektrum.deploy.task_actions import (
    envfile,
    environment,
    config_action,
    set_credentials,
    ThumbnailServiceInfo,
    ProcessorServiceInfo,
    ApplicationServiceInfo,
)

DOIT_CONFIG = {'verbosity': 1}

# HACK: Handles first time case where envfile does not exist,
#       causes config tasks to be run 2x
if not isfile(envfile()):
    actions = config_action()
    for action in actions:
        action.execute(out=stdout, err=stderr)


load_dotenv(envfile())
set_credentials('AWS_ACCESS_KEY_ID', 'aws_access_key')
set_credentials('AWS_SECRET_ACCESS_KEY', 'aws_secret_key')


def task_config():
    """Generate configuration for given environment."""
    file_deps = [
        f for f in glob('network/**', recursive=True) if isfile(f) and 'roles/lam' not in f
    ]
    action = config_action()
    return {
        'targets': [envfile()],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': 2,
    }


def task_application_service_version():
    """Returns version of application for current environment."""
    i = ApplicationServiceInfo()
    return {'actions': [environment, i.version]}


def task_application_service_deploy():
    """Deploys the application service if the version has changed."""
    i = ApplicationServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': i.deploy_actions(),
        'uptodate': [result_dep('application_service_version')],
    }


# TODO Fix this
def task_application_service_migrations():
    """Deploys pending database migrations."""
    i = ApplicationServiceInfo()
    return {
        'actions': i.migration_actions(),
        'verbosity': 2,
    }


def task_thumbnail_service_version():
    """Returns version of thumbnailer for current environment."""
    i = ThumbnailServiceInfo()
    return {'actions': [environment, i.version]}


def task_thumbnail_service_deploy():
    """Deploys the thumbnail service if the version has changed."""
    i = ThumbnailServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': i.deploy_actions(),
        'uptodate': [result_dep('thumbnail_service_version')],
    }


def task_processor_service_version():
    """Returns version of processor for current environment."""
    i = ProcessorServiceInfo()
    return {'actions': [environment, i.version]}


def task_processor_service_deploy():
    """Deploys the processor service if the version has changed."""
    i = ProcessorServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': i.deploy_actions(),
        'uptodate': [result_dep('processor_service_version')],
    }


def task_processor_service_config():
    """Deploys lambda config to grant S3 bucket permission to exec processor."""
    i = ProcessorServiceInfo()
    return {
        'task_dep': ['processor_service_deploy'],
        'file_dep': i.config_deps(),
        'actions': i.config_action(),
    }
