from os import environ
from json import dumps

from django.core.management.base import BaseCommand

from elektrum.deploy_util import invoke


class Command(BaseCommand):
    help = 'Runs the migrate db command remotely via Lambda'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('migration_name', nargs='?', type=str)

    def handle(self, *args, **options):
        lambda_name = environ['APPLICATION_SERVICE_LAMBDA_NAME']

        migration_name = options.get('migration_name', '')
        command = f'migrate {migration_name}'.rstrip()
        payload = {'manage': {'cmd': f'{command}'}}
        payload_enc = dumps(payload).encode('utf-8')

        res = invoke(lambda_name, payload_enc)

        m = 'HTTPStatusCode: %s' % res[0]
        if res[0] < 400:
            msg = self.style.SUCCESS(m)
        else:
            msg = self.style.ERROR(m)
        self.stdout.write(res[1])
        self.stdout.write(f'[{msg}] Execution of [{lambda_name}] completed.')
