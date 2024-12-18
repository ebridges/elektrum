from os import environ, makedirs
from glob import glob
from os.path import isfile, exists
from sys import stderr
from datetime import datetime
from zipfile import ZipFile

from doit.action import CmdAction

from elektrum.deploy_util import (
    download_github_release,
    slurp,
    get_encrypted_field,
    decrypt_value,
    publish_sentry_release,
    get_tag_commit,
)

ELEKTRUM_APPLICATION_VERSION = {'development': '0.7.2', 'staging': '0.7.2', 'production': '0.7.2'}
ELEKTRUM_PROCESSOR_VERSION = {'development': '1.2.3', 'staging': '1.2.3', 'production': '1.2.3'}
ELEKTRUM_THUMBNAIL_VERSION = {'development': '1.5.0', 'staging': '1.5.0', 'production': '1.5.0'}


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
        CmdAction(rf'printf "[\e[31;1m§\e[0m] Updating configuration for targets [{tags}]\n" 1>&2'),
        CmdAction(
            f'ansible-playbook --tags {tags} --inventory environments/{env} --vault-password-file environments/{env}-vault-password.txt site.yml',
            cwd='network',
        ),
    ]


def abstractmethod(method):
    """
    An @abstractmethod member fn decorator.
    (put this in some library somewhere for reuse).

    """

    def default_abstract_method(*args, **kwargs):
        raise NotImplementedError('call to abstract method ' + repr(method))

    default_abstract_method.__name__ = method.__name__
    return default_abstract_method


class PublishMonitoringRelease:
    '''
    This is an abstract base class that takes care of
    initializing monitoring for all child classes.
    '''

    def __init__(self):
        self.name = ''
        self.repo_name = ''
        self.github_auth_token = ''

    @abstractmethod
    def version(self):
        pass

    def publish_monitoring_release_action(self):
        sentry_auth_token = environ['SENTRY_AUTH_TOKEN']
        release_tag = f'v{self.version()}'
        release_commit = get_tag_commit(self.github_auth_token, self.repo_name, release_tag)
        release_name = f'Release {release_tag}'
        release_ref = f'{self.repo_name}@{release_commit}'
        release_url = f'https://github.com/{self.repo_name}/releases/tag/{release_tag}'
        return (
            publish_sentry_release,
            [
                sentry_auth_token,
                service(),
                environment(),
                self.name,
                release_tag,
                release_name,
                release_commit,
                release_ref,
                release_url,
            ],
        )


class ApplicationServiceInfo(PublishMonitoringRelease):
    def __init__(self):
        self.name = f'{service()}-application'
        self.repo_name = f'ebridges/{service()}'
        self.downloaddir = f'./deploy-tmp/{self.name}'
        self.archive = f'{self.name}-{environment()}-{self.version()}.zip'
        self.target = f'{self.downloaddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_TOKEN']
        if not self.github_auth_token:
            raise ValueError('unable to locate GITHUB_TOKEN in environment')
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

        if not exists(self.downloaddir):
            makedirs(self.downloaddir)

    def version(self):
        return ELEKTRUM_APPLICATION_VERSION[environment()]

    def deploy_actions(self):
        gw_name = self.deploy_args['AWS_API_NAME']
        dns_name = self.deploy_args['AWS_API_DOMAIN_NAME']
        monitoring_deploy_action = self.publish_monitoring_release_action()
        return [
            rf'printf "[\\e[31;1m§\e[0m] [{self.name}] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.repo_name, self.version(), self.target],
                {},
            ),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Link archive with environment [{environment()}]\n" 1>&2',
            (self.update_archive, [], {}),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying gateway [{gw_name}]\n" 1>&2',
            CmdAction('lgw gw-deploy', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Adding domain name [{dns_name}]\n" 1>&2',
            CmdAction('lgw domain-add', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Configuring monitoring for this release\n" 1>&2',
            monitoring_deploy_action,
        ]

    def update_archive(self):
        with ZipFile(self.target, 'a') as zip:
            if '.env' not in zip.namelist():
                stderr.write(
                    '[%s] [INFO] Adding [%s] to [%s] as [.env]\n'
                    % (datetime.now(), envfile(), self.target)
                )
                zip.write(envfile(), '.env')
            else:
                stderr.write('[%s] [WARN] .env exists in [%s]\n' % (datetime.now(), self.target))

    def deploy_deps(self):
        return [envfile()]

    def migration_actions(self):
        return [
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Running django migrations.\n" 1>&2',
            CmdAction('python manage.py migrate_remote', cwd='application'),
        ]


class ProcessorServiceInfo(PublishMonitoringRelease):
    def __init__(self):
        self.name = f'{service()}-processor'
        self.repo_name = f'ebridges/metadata-processor'
        self.downloaddir = f'./deploy-tmp/{self.name}'
        self.archive = f'{self.name}-{self.version()}.zip'
        self.target = f'{self.downloaddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_TOKEN']
        if not self.github_auth_token:
            raise ValueError('unable to locate GITHUB_TOKEN in environment')
        self.deploy_args = {
            'PATH': environ['PATH'],
            'AWS_REGION': environ['AWS_REGION'],
            'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
            'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
            'AWS_ACM_CERTIFICATE_ARN': environ['MEDIA_PROCESSOR_HTTPS_CERT_ARN'],
            'AWS_API_DEPLOY_STAGE': environ['MEDIA_PROCESSOR_API_DEPLOY_STAGE'],
            'AWS_API_DESCRIPTION': environ['MEDIA_PROCESSOR_API_DESCRIPTION'],
            'AWS_API_DOMAIN_NAME': environ['MEDIA_PROCESSOR_API_DOMAIN_NAME'],
            'AWS_API_LAMBDA_INTEGRATION_ROLE': environ['MEDIA_PROCESSOR_INTEGRATION_ROLE_ARN'],
            'AWS_API_NAME': environ['MEDIA_PROCESSOR_API_NAME'],
            'AWS_LAMBDA_ARCHIVE_BUCKET': environ['MEDIA_PROCESSOR_ARTIFACT_BUCKET_NAME'],
            'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': self.downloaddir,
            'AWS_LAMBDA_ARCHIVE_KEY': self.archive,
            'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['MEDIA_PROCESSOR_TIMEOUT'],
            'AWS_LAMBDA_DESCRIPTION': environ['MEDIA_PROCESSOR_DESCRIPTION'],
            'AWS_LAMBDA_ENVIRONMENT': environ['MEDIA_PROCESSOR_ENVIRONMENT'],
            'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['MEDIA_PROCESSOR_EXECUTION_ROLE_ARN'],
            'AWS_LAMBDA_HANDLER': environ['MEDIA_PROCESSOR_LAMBDA_HANDLER'],
            'AWS_LAMBDA_MEMORY_SIZE': environ['MEDIA_PROCESSOR_MEMORY_SIZE'],
            'AWS_LAMBDA_NAME': environ['MEDIA_PROCESSOR_LAMBDA_NAME'],
            'AWS_LAMBDA_RUNTIME': environ['MEDIA_PROCESSOR_RUNTIME'],
            'AWS_LAMBDA_TAGS': environ['MEDIA_PROCESSOR_TAGS'],
            'AWS_LAMBDA_VPC_SECURITY_GROUPS': environ['MEDIA_PROCESSOR_SECURITY_GROUPS'],
            'AWS_LAMBDA_VPC_SUBNETS': environ['MEDIA_PROCESSOR_SUBNET_IDS'],
        }

        if not exists(self.downloaddir):
            makedirs(self.downloaddir)

    def version(self):
        return ELEKTRUM_PROCESSOR_VERSION[environment()]

    def deploy_deps(self):
        return [envfile()]

    def deploy_actions(self):
        gw_name = self.deploy_args['AWS_API_NAME']
        dns_name = self.deploy_args['AWS_API_DOMAIN_NAME']
        monitoring_deploy_action = self.publish_monitoring_release_action()
        return [
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.repo_name, self.version(), self.target],
                {},
            ),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying gateway [{gw_name}]\n" 1>&2',
            CmdAction('lgw gw-deploy', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Adding domain name [{dns_name}]\n" 1>&2',
            CmdAction('lgw domain-add', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Configuring monitoring for this release\n" 1>&2',
            monitoring_deploy_action,
        ]

    def config_deps(self):
        return [f for f in glob('network/roles/lam/**', recursive=True) if isfile(f)]

    def config_action(self):
        return config_action('lam')


class ThumbnailServiceInfo(PublishMonitoringRelease):
    def __init__(self):
        self.name = f'{service()}-thumbnails'
        self.repo_name = 'ebridges/thumbnailer'
        self.downloaddir = f'./deploy-tmp/{self.name}'
        self.archive = f'{self.name}-{self.version()}.zip'
        self.target = f'{self.downloaddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_TOKEN']
        if not self.github_auth_token:
            raise ValueError('unable to locate GITHUB_TOKEN in environment')
        self.deploy_args = {
            'PATH': environ['PATH'],
            'AWS_REGION': environ['AWS_REGION'],
            'AWS_ACCESS_KEY_ID': environ['AWS_ACCESS_KEY_ID'],
            'AWS_SECRET_ACCESS_KEY': environ['AWS_SECRET_ACCESS_KEY'],
            'AWS_ACM_CERTIFICATE_ARN': environ['THUMBNAIL_SERVICE_HTTPS_CERT_ARN'],
            'AWS_API_BINARY_TYPES': environ['THUMBNAIL_SERVICE_BINARY_TYPES'],
            'AWS_API_DEPLOY_STAGE': environ['THUMBNAIL_SERVICE_API_DEPLOY_STAGE'],
            'AWS_API_DESCRIPTION': environ['THUMBNAIL_SERVICE_API_DESCRIPTION'],
            'AWS_API_DOMAIN_NAME': environ['THUMBNAIL_SERVICE_API_DOMAIN_NAME'],
            'AWS_API_LAMBDA_INTEGRATION_ROLE': environ['THUMBNAIL_SERVICE_INTEGRATION_ROLE_ARN'],
            'AWS_API_NAME': environ['THUMBNAIL_SERVICE_API_NAME'],
            'AWS_API_RESPONSE_MODELS': environ['THUMBNAIL_SERVICE_RESPONSE_MODELS'],
            'AWS_LAMBDA_ARCHIVE_BUCKET': environ['THUMBNAIL_SERVICE_ARTIFACT_BUCKET_NAME'],
            'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': self.downloaddir,
            'AWS_LAMBDA_ARCHIVE_KEY': self.archive,
            'AWS_LAMBDA_CONNECTION_TIMEOUT': environ['THUMBNAIL_SERVICE_TIMEOUT'],
            'AWS_LAMBDA_DESCRIPTION': environ['THUMBNAIL_SERVICE_DESCRIPTION'],
            'AWS_LAMBDA_ENVIRONMENT': environ['THUMBNAIL_SERVICE_ENVIRONMENT'],
            'AWS_LAMBDA_EXECUTION_ROLE_ARN': environ['THUMBNAIL_SERVICE_EXECUTION_ROLE_ARN'],
            'AWS_LAMBDA_HANDLER': environ['THUMBNAIL_SERVICE_LAMBDA_HANDLER'],
            'AWS_LAMBDA_MEMORY_SIZE': environ['THUMBNAIL_SERVICE_MEMORY_SIZE'],
            'AWS_LAMBDA_NAME': environ['THUMBNAIL_SERVICE_LAMBDA_NAME'],
            'AWS_LAMBDA_RUNTIME': environ['THUMBNAIL_SERVICE_RUNTIME'],
            'AWS_LAMBDA_TAGS': environ['THUMBNAIL_SERVICE_TAGS'],
            'AWS_LAMBDA_VPC_SECURITY_GROUPS': environ['THUMBNAIL_SERVICE_SECURITY_GROUPS'],
            'AWS_LAMBDA_VPC_SUBNETS': environ['THUMBNAIL_SERVICE_SUBNET_IDS'],
        }

        if not exists(self.downloaddir):
            makedirs(self.downloaddir)

    def version(self):
        return ELEKTRUM_THUMBNAIL_VERSION[environment()]

    def deploy_deps(self):
        return [envfile()]

    def deploy_actions(self):
        gw_name = self.deploy_args['AWS_API_NAME']
        dns_name = self.deploy_args['AWS_API_DOMAIN_NAME']
        monitoring_deploy_action = self.publish_monitoring_release_action()
        return [
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.repo_name, self.version(), self.target],
                {},
            ),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying gateway [{gw_name}]\n" 1>&2',
            CmdAction('lgw gw-deploy', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Adding domain name [{dns_name}]\n" 1>&2',
            CmdAction('lgw domain-add', env=self.deploy_args),
            rf'printf "[\e[31;1m§\e[0m] [{self.name}] Configuring monitoring for this release\n" 1>&2',
            monitoring_deploy_action,
        ]
