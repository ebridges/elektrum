from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Creates the initial database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating database [%s]' % settings.DATABASES['default']['NAME']))

        os.environ['PGCONNECT_TIMEOUT'] = '5'

        dbname = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']

        connection = None
        try:
          connection = connect(dbname='postgres', user=user, host=host, password=password)
          cursor = connection.cursor()
          if (cursor.execute("select not exists(SELECT datname FROM pg_catalog.pg_database WHERE datname = '%s')" % dbname)):
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor.execute("CREATE DATABASE '%s'" % dbname)
            self.stdout.write(self.style.SUCCESS('Successfully created database [%s]' % dbname))
          else:
            self.stdout.write(self.style.SUCCESS('Database [%s] already exists.' % dbname))
        finally:
          if (connection and connection.closed == 0):
            cursor.close()
            connection.close()
