from os import environ, getcwd
from json import dumps

from django.core.management.base import BaseCommand

from ._util import decrypt_value, get_encrypted_field, slurp, invoke


class Command(BaseCommand):
    help = 'Creates the remote Django admin user using the projects configured account user & pass.'

    @staticmethod
    def decrypt_field(environment, field):
        passphrase = slurp(f'../../network/environments/{environment}-vault-password.txt')
        secrets_file = f'../../network/group_vars/{environment}.yml'
        enc = get_encrypted_field(secrets_file, field)
        return decrypt_value(passphrase, enc)

    def handle(self, *args, **options):
        lambda_name = environ['APPLICATION_SERVICE_LAMBDA_NAME']
        environment = environ['ENVIRONMENT']

        admin_username = Command.decrypt_field(environment, 'django_admin_username')
        admin_password = Command.decrypt_field(environment, 'django_admin_password')
        dummy_email = 'admin@example.com'

        payload = {
            'manage': {
                'cmd': 'create-admin-user',
                'args': {
                    'username': admin_username,
                    'password': admin_password,
                    'email': dummy_email,
                },
            }
        }

        payload_enc = dumps(payload).encode('utf-8')

        res = invoke(lambda_name, payload_enc)

        m = 'HTTPStatusCode: %s' % res[0]
        if res[0] < 400:
            msg = self.style.SUCCESS(m)
        else:
            msg = self.style.ERROR(m)
        self.stdout.write(res[1])
        self.stdout.write(f'[{msg}] Execution of [{lambda_name}] completed.')
