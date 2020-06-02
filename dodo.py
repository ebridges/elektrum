from os import environ
from os.path import isfile
from glob import glob

from etc.build.task_actions import action_config, action_env, get_envfile

DOIT_CONFIG = {'default_tasks': ['env']}


def task_env():
    """Populates environment"""
    envfile = get_envfile()
    return {'file_dep': [envfile], 'actions': [action_env], 'uptodate': [False]}


def task_config():
    """Compile network, generate configuration"""
    envfile = get_envfile()
    file_deps = [f for f in glob('network/**', recursive=True) if isfile(f)]
    action = action_config()
    return {'targets': [envfile], 'file_dep': file_deps, 'actions': action, 'verbosity': 2}
