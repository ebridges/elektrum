from os import environ
from glob import glob
from os.path import isfile
from doit.action import CmdAction

from elektrum.doit.version_info import read_from_file
from elektrum.doit.util import slurp, get_encrypted_field, decrypt_value


def service():
    return environ['SERVICE_NAME']


def environment():
    return environ['OPERATING_ENV']


def envfile():
    env = environment()
    return f'etc/env/{env}.env'


def set_credentials(var, key):
    env = environment()
    passwd = slurp(f'network/environments/{env}-vault-password.txt')
    encrypted_val = get_encrypted_field(f'network/group_vars/{env}.yml', key)  # todo fix this
    decrypted_val = decrypt_value(passwd, encrypted_val)
    environ[var] = decrypted_val


def config_action(tags='iam,vpc,rds,sss,acm,cdn,dns,ses,cfg'):
    env = environment()
    return [
        CmdAction(
            f'ansible-playbook --tags {tags} --inventory environments/{env} --vault-password-file environments/{env}-vault-password.txt site.yml',
            cwd='network',
        )
    ]


class VersionInfo(object):
    def version(self):
        return read_from_file(self.versionfile, self.dev, self.next, self.part)


class ApplicationServiceInfo(VersionInfo):
    def __init__(self, dev=True, next=False, part=1):
        self.dev = dev
        self.next = next
        self.part = part
        self.builddir = './build-tmp'
        self.appdir = 'functions/application'
        self.versionfile = f'{self.appdir}/version.txt'
        self.requirements = f'{self.appdir}/requirements.txt'
        self.archive = f'{service()}-{environment()}-application-{self.version()}.zip'
        self.target = f'{self.builddir}/{self.archive}'

    def file_deps(self):
        deps = [f for f in glob(f'{self.appdir}/**', recursive=True) if isfile(f)]
        deps.append(envfile())
        deps.append(self.versionfile)
        return deps


class ProcessorServiceInfo(VersionInfo):
    def __init__(self, dev=True, next=False, part=1):
        self.dev = dev
        self.next = next
        self.part = part
        self.builddir = './build-tmp'
        self.appdir = 'functions/processor'
        self.versionfile = f'{self.appdir}/version.txt'
        self.archive = f'{service()}-{environment()}-processor-{self.version()}.zip'
        self.target = f'{self.appdir}/build/archives/{self.archive}'

    def build_deps(self):
        deps = [f for f in glob(f'{self.appdir}/src/main/**', recursive=True) if isfile(f)]
        deps.append(envfile())
        deps.append(self.versionfile)
        return deps

    def deploy_deps(self):
        return [f'{self.appdir}/build/archives/{self.archive}', envfile()]

    def config_deps(self):
        return [f for f in glob('network/roles/lam/**', recursive=True) if isfile(f)]

    def build_action(self):
        bucket = environ.get('MEDIA_PROCESSOR_ARTIFACT_BUCKET_NAME')
        archive_folder = f'{self.appdir}/build/archives'
        src_archive = f'{service()}-processor-{self.version()}.zip'

        return [
            CmdAction(f'./gradlew -PprojVersion={self.version()} buildZip', cwd=self.appdir),
            CmdAction(f'mv {archive_folder}/{src_archive} {archive_folder}/{self.archive}'),
            CmdAction(
                f'aws s3 sync {archive_folder} s3://{bucket}/ --exclude "*" --include {self.archive}'
            ),
        ]


class ThumbnailServiceInfo(VersionInfo):
    def __init__(self, dev=True, next=False, part=1):
        self.dev = dev
        self.next = next
        self.part = part
        self.builddir = './build-tmp'
        self.appdir = 'functions/thumbnails'
        self.versionfile = f'{self.appdir}/version.txt'
        self.requirements = f'{self.appdir}/requirements.txt'
        self.archive = f'{service()}-{environment()}-thumbnails-{self.version()}.zip'
        self.target = f'{self.builddir}/{self.archive}'

    def build_deps(self):
        deps = [f for f in glob(f'{self.appdir}/**', recursive=True) if isfile(f)]
        deps.append(envfile())
        deps.append(self.versionfile)
        return deps

    def deploy_deps(self):
        return [self.target, envfile()]
