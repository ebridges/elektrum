from base64 import b64decode
from os import environ
from tempfile import NamedTemporaryFile
from json import dumps

import boto3

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Runs the migrate db command remotely via Lambda'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('migration_name', nargs='?', type=str)

    def handle(self, *args, **options):
        lambda_name = environ['APPLICATION_SERVICE_LAMBDA_NAME']
        client = boto3.client('lambda')

        migration_name = options['migration_name'] if options['migration_name'] else ''
        command = f'migrate {migration_name}'.rstrip()
        payload = {'manage': {'cmd': f'{command}'}}
        payload_enc = dumps(payload).encode('utf-8')

        res = client.invoke(
            FunctionName=lambda_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=payload_enc,
        )

        # format/output response from execution.
        http_sc = res['ResponseMetadata']['HTTPStatusCode']
        m = 'HTTPStatusCode: %s' % http_sc
        if int(http_sc) < 400:
            msg = self.style.SUCCESS(m)
        else:
            msg = self.style.ERROR(m)
        log_output = b64decode(res['LogResult'])
        self.stdout.write(log_output.decode('utf-8'))
        self.stdout.write(f'[{msg}] Execution of [{lambda_name}] completed.')
