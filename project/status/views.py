from django.http import HttpResponse
from django.views import View
from django.db import connection

from elektron.log import getLogger

class Ok(View):
    # noinspection PyUnusedLocal
    def get(self, request=None):
        time_at = self.db_time()
        response = HttpResponse('<h2>Ok</h2> %s' % time_at[0])
        response['X-Elektron-Now'] = time_at[0]
        logger = getLogger(__name__)
        logger.debug(time_at[0])
        return response

    def db_time(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_timestamp AS now")
            return cursor.fetchone()
