from os import environ, makedirs
from glob import glob
from os.path import isfile, exists
from doit.action import CmdAction

from elektrum.build.version_info import read_from_file
from elektrum.build_util import download_github_release, slurp, get_encrypted_field, decrypt_value

ELEKTRUM_PROCESSOR_VERSION = {'development': '1.1.2', 'staging': '1.1.2', 'production': '1.1.2'}
ELEKTRUM_THUMBNAIL_VERSION = {'development': '1.2.3', 'staging': '1.2.3', 'production': '1.2.3'}


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
        CmdAction(f'printf "[\e[31;1m§\e[0m] Updating configuration for targets [{tags}]\n" 1>&2'),
        CmdAction(
            f'ansible-playbook --tags {tags} --inventory environments/{env} --vault-password-file environments/{env}-vault-password.txt site.yml',
            cwd='network',
        ),
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
        self.appdir = 'application'
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
        included_dirs = [
            'base',
            'date_dimension',
            'elektrum',
            'emailer',
            'js',
            'media_items',
            'pages',
            'sharing',
            'status',
            'users',
        ]
        deps = []
        for d in included_dirs:
            deps.extend(
                [
                    f
                    for f in glob(f'{self.appdir}/{d}/**', recursive=True)
                    if isfile(f) and not f.endswith('.pyc')
                ]
            )
        deps.append(envfile())
        deps.append(self.versionfile)
        return deps

    def static_deps(self):
        deps = [f for f in glob(f'{self.appdir}/static/**', recursive=True) if isfile(f)]
        return deps


class ProcessorServiceInfo:
    def __init__(self):
        self.name = f'{service()}-processor'
        self.downloaddir = f'./build-tmp/{self.name}'
        self.archive = f'{self.name}-{self.version()}.zip'
        self.target = f'{self.downloaddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_OAUTH_TOKEN']
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

        if not exists(self.downloaddir):
            makedirs(self.downloaddir)

    def version(self):
        return ELEKTRUM_PROCESSOR_VERSION[environment()]

    def deploy_deps(self):
        return [envfile()]

    def deploy_actions(self):
        return [
            f'printf "[\e[31;1m§\e[0m] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.name, self.version(), self.target],
                {},
            ),
            f'printf "[\e[31;1m§\e[0m] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
        ]

    def config_deps(self):
        return [f for f in glob('network/roles/lam/**', recursive=True) if isfile(f)]

    def config_action(self):
        return config_action('lam')


class ThumbnailServiceInfo:
    def __init__(self):
        self.name = 'thumbnailer'
        self.builddir = f'./build-tmp/{self.name}'
        self.archive = f'{service()}-thumbnails-{self.version()}.zip'
        self.target = f'{self.builddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_OAUTH_TOKEN']
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

    def version(self):
        return ELEKTRUM_THUMBNAIL_VERSION[environment()]

    def deploy_deps(self):
        return [envfile()]

    def deploy_actions(self):
        gw_name = self.deploy_args['AWS_API_NAME']
        dns_name = self.deploy_args['AWS_API_DOMAIN_NAME']
        return [
            f'printf "[\e[31;1m§\e[0m] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.name, self.version(), self.target],
                {},
            ),
            f'printf "[\e[31;1m§\e[0m] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] Deploying gateway [{gw_name}]\n" 1>&2',
            CmdAction('lgw gw-deploy', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] Adding domain name [{dns_name}]\n" 1>&2',
            CmdAction('lgw domain-add', env=self.deploy_args),
        ]
