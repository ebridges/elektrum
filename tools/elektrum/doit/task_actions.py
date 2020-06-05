from os import environ, rename
from os.path import basename
from unittest import TestCase
from doit.action import CmdAction
from ansible_vault import Vault

from elektrum.doit.version_info import read_from_file
from elektrum.doit.util import slurp, get_encrypted_field, decrypt_value, md5


def environment():
    return environ.get('OPERATING_ENV')


def get_envfile():
    env = environment()
    return f'etc/env/{env}.env'


def action_set_credentials(var, key):
    env = environment()
    passwd = slurp(f'network/environments/{env}-vault-password.txt')
    encrypted_val = get_encrypted_field(f'network/group_vars/{env}.yml', key)  # todo fix this
    decrypted_val = decrypt_value(passwd, encrypted_val)
    environ[var] = decrypted_val


def action_config():
    env = environment()
    return [
        CmdAction(
            f'ansible-playbook --inventory environments/{env} --vault-password-file environments/{env}-vault-password.txt site.yml',
            cwd='network',
        )
    ]


def action_build_processor(version):
    env = environment()
    service = environ.get('SERVICE_NAME')
    bucket = environ.get('MEDIA_PROCESSOR_ARTIFACT_BUCKET_NAME')

    archive_folder = 'functions/processor/build/archives'
    src_archive = f'{service}-processor-{version}.zip'
    archive = f'{service}-{env}-processor-{version}.zip'

    return [
        CmdAction(f'./gradlew -PprojVersion={version} buildZip', cwd='functions/processor'),
        CmdAction(f'mv {archive_folder}/{src_archive} {archive_folder}/{archive}'),
        CmdAction(f'aws s3 sync {archive_folder} s3://{bucket}/ --exclude "*" --include {archive}'),
    ]
