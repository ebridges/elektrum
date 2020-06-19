from os import environ
from glob import glob
from os.path import isfile
from doit.action import CmdAction

from elektrum.build.version_info import read_from_file
from elektrum.management.commands._util import slurp, get_encrypted_field, decrypt_value


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
        self.build_args = {
            'PATH': environ['PATH'],
            'AWS_LAMBDA_ARCHIVE_CONTEXT_DIR': '.',  # needs to be cwd so that etc/env is availabe in docker context
            'AWS_LAMBDA_ARCHIVE_ADDL_FILES': f'{envfile()},$wkdir/.env;{self.versionfile},$wkdir;{self.requirements},$wkdir;{self.appdir}/,$wkdir',
            'AWS_LAMBDA_ARCHIVE_ADDL_PACKAGES': 'postgresql,postgresql-devel',
            'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': self.builddir,
            'AWS_LAMBDA_ARCHIVE_BUNDLE_NAME': self.archive,
        }
        self.deploy_args = {
            'PATH': environ['PATH'],
            'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
            'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
            'AWS_LAMBDA_NAME': environ['APPLICATION_SERVICE_LAMBDA_NAME'],
            'AWS_LAMBDA_DESCRIPTION': environ['APPLICATION_SERVICE_DESCRIPTION'],
            'AWS_LAMBDA_HANDLER': environ['APPLICATION_SERVICE_LAMBDA_HANDLER'],
            'AWS_LAMBDA_ARCHIVE_BUCKET': environ['APPLICATION_SERVICE_ARTIFACT_BUCKET_NAME'],
            'AWS_LAMBDA_ARCHIVE_KEY': self.archive,
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
            'AWS_API_DESCRIPTION': environ['APPLICATION_SERVICE_API_DESCRIPTION'],
        }

    def build_deps(self):
        included_dirs = (
            '{base,date_dimension,elektrum,emailer,js,media_items,pages,sharing,status,users}'
        )
        deps = [f for f in glob(f'{self.appdir}/{included_dirs}/**', recursive=True) if isfile(f)]
        deps.append(envfile())
        deps.append(self.versionfile)
        return deps

    def static_deps(self):
        deps = [f for f in glob(f'{self.appdir}/static/**', recursive=True) if isfile(f)]
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
        self.deploy_args = {
            'PATH': environ['PATH'],
            'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
            'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
            'AWS_LAMBDA_NAME': environ['MEDIA_PROCESSOR_LAMBDA_NAME'],
            'AWS_LAMBDA_DESCRIPTION': environ['MEDIA_PROCESSOR_DESCRIPTION'],
            'AWS_LAMBDA_HANDLER': environ['MEDIA_PROCESSOR_LAMBDA_HANDLER'],
            'AWS_LAMBDA_ARCHIVE_BUCKET': environ['MEDIA_PROCESSOR_ARTIFACT_BUCKET_NAME'],
            'AWS_LAMBDA_ARCHIVE_KEY': self.archive,
            'AWS_LAMBDA_VPC_SUBNETS': environ['MEDIA_PROCESSOR_SUBNET_IDS'],
            'AWS_LAMBDA_VPC_SECURITY_GROUPS': environ['MEDIA_PROCESSOR_SECURITY_GROUPS'],
            'AWS_LAMBDA_TAGS': environ['MEDIA_PROCESSOR_TAGS'],
            'AWS_LAMBDA_ENVIRONMENT': environ['MEDIA_PROCESSOR_ENVIRONMENT'],
            'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['MEDIA_PROCESSOR_EXECUTION_ROLE_ARN'],
            'AWS_LAMBDA_MEMORY_SIZE': environ['MEDIA_PROCESSOR_MEMORY_SIZE'],
            'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['MEDIA_PROCESSOR_TIMEOUT'],
            'AWS_LAMBDA_RUNTIME': environ['MEDIA_PROCESSOR_RUNTIME'],
        }

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
        self.build_args = {
            'PATH': environ['PATH'],
            'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': self.builddir,
            'AWS_LAMBDA_ARCHIVE_BUNDLE_NAME': self.archive,
            'AWS_LAMBDA_ARCHIVE_CONTEXT_DIR': f'{self.appdir}/',  # trailing slash significant for populating docker image
            'AWS_LAMBDA_ARCHIVE_ADDL_FILES': 'src/,$wkdir;requirements.txt,$wkdir;version.txt,$wkdir',
        }
        self.deploy_args = {
            'PATH': environ['PATH'],
            'AWS_REGION': environ['AWS_REGION'],
            'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
            'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
            'AWS_LAMBDA_NAME': environ['THUMBNAIL_SERVICE_LAMBDA_NAME'],
            'AWS_LAMBDA_DESCRIPTION': environ['THUMBNAIL_SERVICE_DESCRIPTION'],
            'AWS_LAMBDA_HANDLER': environ['THUMBNAIL_SERVICE_LAMBDA_HANDLER'],
            'AWS_LAMBDA_ARCHIVE_BUCKET': environ['THUMBNAIL_SERVICE_ARTIFACT_BUCKET_NAME'],
            'AWS_LAMBDA_ARCHIVE_KEY': self.archive,
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
            'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': self.builddir,
            'AWS_API_DESCRIPTION': environ['THUMBNAIL_SERVICE_API_DESCRIPTION'],
        }

    def build_deps(self):
        deps = [f for f in glob(f'{self.appdir}/**', recursive=True) if isfile(f)]
        deps.append(envfile())
        deps.append(self.versionfile)
        return deps

    def deploy_deps(self):
        return [self.target, envfile()]
