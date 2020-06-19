from os import environ
from os.path import isfile
from sys import stdout, stderr
from glob import glob

from dotenv import load_dotenv
from doit.action import CmdAction

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
    return {
        'file_dep': i.deploy_deps(),
        'actions': [CmdAction('lgw lambda-deploy --verbose', env=i.deploy_args)],
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
        'actions': [CmdAction('make static', cwd='functions/application')],
        'file_dep': i.static_deps(),
        'verbosity': 2,
    }


def task_deploy_application_apply_migrations():
    return {
        'actions': [CmdAction('python manage.py migrate_remote', cwd='functions/application')],
        'verbosity': 2,
        'task_dep': ['deploy_application_service'],
    }


def task_build_thumbnail_service():
    i = ThumbnailServiceInfo()
    return {
        'file_dep': i.build_deps(),
        'targets': [i.target],
        'actions': [
            f'etc/bin/poetry2pip.py --file "{i.appdir}/poetry.lock" --output {i.requirements}',
            CmdAction('lgw lambda-archive --verbose', env=i.build_args),
        ],
        'verbosity': VERBOSITY,
    }


def task_deploy_thumbnail_service():
    i = ThumbnailServiceInfo()
    return {
        'file_dep': i.deploy_deps(),
        'actions': [
            CmdAction(f'lgw lambda-deploy --verbose --lambda-file={i.target}', env=i.deploy_args),
            CmdAction('lgw gw-deploy --verbose', env=i.deploy_args),
            CmdAction('lgw domain-add --verbose', env=i.deploy_args),
        ],
        'verbosity': VERBOSITY,
        'task_dep': ['build_thumbnail_service'],
    }
