from django.http import HttpResponse
from django.views import View
from django.db import connection
from io import StringIO

from meta.management.commands import createdb
from elektrum.log import getLogger

class Ok(View):
    # noinspection PyUnusedLocal
    def get(self, request=None):
        time_at = self.db_time()
        response = HttpResponse('<h2>Ok</h2> %s' % time_at[0])
        response['X-Elektrum-Now'] = time_at[0]
        logger = getLogger(__name__)
        logger.debug(time_at[0])
        return response

    def db_time(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_timestamp AS now")
            return cursor.fetchone()


class DBCreate(View):
    def get(self, request=None):
        output = StringIO()
        command = createdb.Command(stdout=output, stderr=output)
        command.handle(None, None);
        result = output.getvalue()
        logger = getLogger(__name__)
        logger.info(result)
        response = HttpResponse(result)
        response['Content-Type'] = 'text/plain'
        return response

