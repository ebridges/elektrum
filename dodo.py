from os import environ
from os.path import isfile
from sys import path
from glob import glob
from pathlib import Path

from dotenv import load_dotenv
from doit import run

from elektrum.doit.task_actions import (
    action_config,
    get_envfile,
    action_build_processor,
    action_set_credentials,
    environment,
)
from elektrum.doit.version_info import read_from_file


load_dotenv(get_envfile())


def task_set_credentials():
    cred_vars = [
        ('AWS_ACCESS_KEY_ID', 'aws_access_key'),
        ('AWS_SECRET_ACCESS_KEY', 'aws_secret_key'),
    ]
    for var, key in cred_vars:
        yield {
            'name': var.lower(),
            'actions': [(action_set_credentials, [], {'var': var, 'key': key})],
            'uptodate': [key in environ and environ[key] is not None],
            'verbosity': 2,
        }


def task_config():
    """Compile network, generate configuration"""
    envfile = get_envfile()
    file_deps = [f for f in glob('network/**', recursive=True) if isfile(f)]
    action = action_config()
    return {
        'targets': [envfile],
        'task_dep': ['set_credentials'],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': 2,
    }


def task_build_processor():
    """Builds zip artifact for processor"""
    env = environment()
    version = read_from_file('functions/processor/version.txt', dev=True)
    targets = f'functions/processor/build/archives/elektrum-{env}-processor-{version}.zip'
    file_deps = [f for f in glob('functions/processor/src/main/**', recursive=True) if isfile(f)]
    file_deps.append('functions/processor/version.txt')
    action = action_build_processor(version)
    return {
        'targets': [targets],
        'file_dep': file_deps,
        'actions': action,
        'verbosity': 2,
        'task_dep': ['config'],
    }
