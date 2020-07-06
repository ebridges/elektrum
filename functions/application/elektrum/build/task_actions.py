from os import environ, makedirs
from os.path import exists
from glob import glob
from os.path import isfile
from doit.action import CmdAction
from requests.api import get

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


def download_github_release(token, project, version, dest):
    if not exists(dest):
        h = {'Accept': 'application/vnd.github.v3+json', 'Authorization': f'token  {token}'}
        download_url = f'https://api.github.com/repos/ebridges/{project}/releases/tags/v{version}'
        r = get(download_url, headers=h)
        content = r.json()
        asset_url = content['assets'][0]['url']

        h['Accept'] = 'application/octet-stream'
        print(f'Downloading from {asset_url}')
        r = get(asset_url, headers=h, allow_redirects=True, stream=True)
        chunk_size = 256
        with open(dest, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        print(f'Release archive successfully downloaded to {dest}')
    else:
        print(f'Release archive already downloaded locally.  Remove {dest} to redownload.')
    return True


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


class ProcessorServiceInfo:
    def __init__(self):
        self.version = '1.0.5'
        self.name = f'{service()}-processor'
        self.downloaddir = f'./build-tmp/{self.name}'
        self.archive = f'{self.name}-{self.version}.zip'
        self.target = f'{self.downloaddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_OAUTH_TOKEN']
        self.install_args = {
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

        if not exists(self.downloaddir):
            makedirs(self.downloaddir)

    def install_deps(self):
        return [envfile()]

    def install_action(self):
        bucket = self.install_args['AWS_LAMBDA_ARCHIVE_BUCKET']

        return [
            (
                download_github_release,
                [self.github_auth_token, self.name, self.version, self.target],
                {},
            ),
            CmdAction(
                f'aws s3 sync {self.downloaddir} s3://{bucket}/ --exclude "*" --include {self.archive}'
            ),
            CmdAction(
                f'lgw lambda-deploy --verbose --lambda-file={self.target}', env=self.install_args
            ),
        ]

    def install_target(self):
        return [self.target]

    def config_deps(self):
        return [f for f in glob('network/roles/lam/**', recursive=True) if isfile(f)]

    def config_action(self):
        return config_action('lam')


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
