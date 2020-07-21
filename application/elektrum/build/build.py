from os import environ
from os.path import isfile
from sys import stdout, stderr
from glob import glob

from dotenv import load_dotenv
from doit.action import CmdAction
from doit.tools import result_dep

from elektrum.build.task_actions import (
    envfile,
    environment,
    config_action,
    set_credentials,
    ThumbnailServiceInfo,
    ProcessorServiceInfo,
    ApplicationServiceInfo,
)

VERBOSITY = 1


# Hack @todo -- still needed?
if not isfile(envfile()):
    actions = config_action()
    for action in actions:
        action.execute(out=stdout, err=stderr)


load_dotenv(envfile())
set_credentials('AWS_ACCESS_KEY_ID', 'aws_access_key')
set_credentials('AWS_SECRET_ACCESS_KEY', 'aws_secret_key')


def task_config():
    """Compile network, generate configuration"""
    file_deps = [
        f for f in glob('network/**', recursive=True) if isfile(f) and 'roles/lam' not in f
    ]
    action = config_action()
    return {
        'targets': [envfile()],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': VERBOSITY,
    }

    i = ApplicationServiceInfo()


def task_deploy_application_service():
    i = ApplicationServiceInfo()
    return {
        'file_dep': [i.target, envfile()],
        'actions': [
            CmdAction(f'lgw lambda-deploy --lambda-file={i.target}', env=i.deploy_args),
            CmdAction('lgw gw-deploy', env=i.deploy_args),
            CmdAction('lgw domain-add', env=i.deploy_args),
        ],
        'verbosity': VERBOSITY,
        'task_dep': ['build_application_service'],
    }


def task_deploy_application_make_static():
    i = ApplicationServiceInfo()
    return {
        'actions': [CmdAction('make static', cwd='application')],
        'file_dep': i.static_deps(),
        'verbosity': 2,
    }


def task_deploy_application_apply_migrations():
    return {
        'actions': [CmdAction('python manage.py migrate_remote', cwd='application')],
        'verbosity': 2,
        'task_dep': ['deploy_application_service'],
    }


def task_thumbnail_service_version():
    """Returns version of thumbnailer for current environment."""
    i = ThumbnailServiceInfo()
    return {'actions': [environment, i.version], 'verbosity': 1}


def task_thumbnail_service_deploy():
    """Deploys the thumbnail service if the version has changed."""
    i = ThumbnailServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': i.deploy_actions(),
        'verbosity': 1,
        'uptodate': [result_dep('thumbnail_service_version')],
    }


def task_processor_service_version():
    """Returns version of processor for current environment."""
    i = ProcessorServiceInfo()
    return {'actions': [environment, i.version], 'verbosity': 1}


def task_processor_service_deploy():
    """Deploys the processor service if the version has changed."""
    i = ProcessorServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': i.deploy_actions(),
        'verbosity': 1,
        'uptodate': [result_dep('processor_service_version')],
    }


def task_processor_service_config():
    """Update lambda config to grant S3 bucket permission to exec processor."""
    i = ProcessorServiceInfo()
    return {
        'task_dep': ['processor_service_deploy'],
        'file_dep': i.config_deps(),
        'actions': i.config_action(),
        'verbosity': VERBOSITY,
    }
