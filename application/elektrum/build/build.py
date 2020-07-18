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


def task_install_processor_service():
    """Download, install, & config processor as a lambda"""
    i = ProcessorServiceInfo()
    return {
        'task_dep': ['config'],
        'file_dep': i.install_deps(),
        'actions': i.install_action(),
        'verbosity': 2,
        'targets': i.install_target(),
    }


def task_config_processor_service():
    """Update lambda configuration"""
    i = ProcessorServiceInfo()
    return {
        'task_dep': ['install_processor_service'],
        'file_dep': i.config_deps(),
        'actions': i.config_action(),
        'verbosity': VERBOSITY,
    }


def task_build_application_service():
    i = ApplicationServiceInfo()
    return {
        'file_dep': i.build_deps(),
        'targets': [i.target],
        'actions': [
            f'etc/bin/poetry2pip.py --file poetry.lock --output {i.requirements}',
            CmdAction('lgw lambda-archive --verbose', env=i.build_args),
        ],
        'verbosity': VERBOSITY,
    }


def task_deploy_application_service():
    i = ApplicationServiceInfo()
    return {
        'file_dep': [i.target, envfile()],
        'actions': [
            CmdAction(f'lgw lambda-deploy --lambda-file={i.target}', env=i.deploy_args),
            CmdAction('lgw gw-deploy --verbose', env=i.deploy_args),
            CmdAction('lgw domain-add --verbose', env=i.deploy_args),
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
    i = ThumbnailServiceInfo()
    return {'actions': [environment, i.version], 'verbosity': 1}


def task_deploy_thumbnail_service():
    i = ThumbnailServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': i.deploy_actions(),
        'verbosity': 1,
        'uptodate': [result_dep('thumbnail_service_version')],
    }


def task_processor_service_version():
    i = ProcessorServiceInfo()
    return {'actions': [environment, i.version], 'verbosity': 1}
