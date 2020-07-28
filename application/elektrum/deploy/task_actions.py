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

ELEKTRUM_APPLICATION_VERSION = {'development': '0.6.0', 'staging': '0.6.0', 'production': '0.6.0'}
ELEKTRUM_PROCESSOR_VERSION = {'development': '1.2.0', 'staging': '1.2.0', 'production': '1.2.0'}
ELEKTRUM_THUMBNAIL_VERSION = {'development': '1.3.0', 'staging': '1.3.0', 'production': '1.3.0'}


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


class PublishMonitoringRelease:
    def publish_monitoring_release_action(self):
        sentry_auth_token = environ['SENTRY_AUTH_TOKEN']
        release_tag = f'v{self.version()}'
        release_commit = get_tag_commit(self.github_auth_token, self.repo_name, release_tag)
        release_name = f'Release {release_tag}'
        release_ref = f'{self.repo_name}@{release_commit}'
        release_url = f'https://github.com/{self.repo_name}/releases/tag/{release_tag}'
        return (
            (
                publish_sentry_release,
                [
                    self.sentry_auth_token,
                    service(),
                    environment(),
                    self.name,
                    release_tag,
                    release_name,
                    release_commit,
                    release_ref,
                    release_url,
                ],
            ),
        )


class ApplicationServiceInfo(PublishMonitoringRelease):
    def __init__(self):
        self.name = f'{service()}-application'
        self.repo_name = f'ebridges/{service()}'
        self.downloaddir = f'./deploy-tmp/{self.name}'
        self.archive = f'{self.name}-{environment()}-{self.version()}.zip'
        self.target = f'{self.downloaddir}/{self.archive}'
        self.github_auth_token = environ['GITHUB_OAUTH_TOKEN']
        self.sentry_auth_token = environ['SENTRY_AUTH_TOKEN']
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
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.repo_name, self.version(), self.target],
                {},
            ),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Link archive with environment [{environment()}]\n" 1>&2',
            (self.update_archive, [], {}),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying gateway [{gw_name}]\n" 1>&2',
            CmdAction('lgw gw-deploy', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Adding domain name [{dns_name}]\n" 1>&2',
            CmdAction('lgw domain-add', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Configuring monitoring for this release\n" 1>&2',
            monitoring_deploy_action,
        ]

    def update_archive(self):
        with ZipFile(self.target, 'a') as zip:
            if not '.env' in zip.namelist():
                stderr.write(
                    '[%s] [INFO] Adding [%s] to [%s] as [.env]\n'
                    % (datetime.now(), envfile(), self.target)
                )
                zip.write(envfile(), '.env')
            else:
                stderr.write('[%s] [WARN] .env exists in [%s]\n' % (datetime.now(), self.target))

    def deploy_deps(self):
        return [envfile()]

    def static_actions(self):
        return [CmdAction('make static', cwd='application')]

    def static_deps(self):
        deps = [f for f in glob(f'application/js/**', recursive=True) if isfile(f)]
        return deps

    def static_publish_actions(self):
        return [
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Collecting & publishing static assets\n" 1>&2',
            CmdAction(
                'python ./manage.py collectstatic --noinput --pythonpath=. --settings=elektrum.settings',
                cwd='application',
            ),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Adding to git any files that have changed.\n" 1>&2',
            CmdAction(
                'git add ./css/app* ./js/app* ./js/manifest* ./js/vendor* ./js/load-image*',
                cwd='application/static',
            ),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Committing any changed assets.\n" 1>&2',
            CmdAction('git commit --gpg-sign --message "chore: static assets generated."'),
        ]

    def static_publish_deps(self):
        deps = [f for f in glob(f'application/static/**', recursive=True) if isfile(f)]
        return deps

    def migration_actions(self):
        return [
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Running django migrations.\n" 1>&2',
            CmdAction('python manage.py migrate_remote', cwd='application'),
        ]


class ProcessorServiceInfo(PublishMonitoringRelease):
    def __init__(self):
        self.name = f'{service()}-processor'
        self.repo_name = f'ebridges/{self.name}'
        self.downloaddir = f'./deploy-tmp/{self.name}'
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
        monitoring_deploy_action = self.publish_monitoring_release_action()
        return [
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.repo_name, self.version(), self.target],
                {},
            ),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Configuring monitoring for this release\n" 1>&2',
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
            'AWS_LAMBDA_ARCHIVE_BUNDLE_DIR': self.downloaddir,
            'AWS_API_DESCRIPTION': environ['THUMBNAIL_SERVICE_API_DESCRIPTION'],
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
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Downloading version [{self.version()}]\n" 1>&2',
            (
                download_github_release,
                [self.github_auth_token, self.repo_name, self.version(), self.target],
                {},
            ),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying lambda from [{self.target}]\n" 1>&2',
            CmdAction(f'lgw lambda-deploy --lambda-file={self.target}', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Deploying gateway [{gw_name}]\n" 1>&2',
            CmdAction('lgw gw-deploy', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Adding domain name [{dns_name}]\n" 1>&2',
            CmdAction('lgw domain-add', env=self.deploy_args),
            f'printf "[\e[31;1m§\e[0m] [{self.name}] Configuring monitoring for this release\n" 1>&2',
            monitoring_deploy_action,
        ]
