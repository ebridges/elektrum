from io import StringIO

from django.http import HttpResponse
from django.views import View

from elektrum.management.commands import create_initial_db
from elektrum.log import getLogger


class DBCreate(View):
    def get(self, request=None):
        # output = StringIO()
        # command = create_initial_db.Command(stdout=output, stderr=output)
        # command.handle(None, None)
        # result = output.getvalue()
        # logger = getLogger(__name__)
        # logger.info(result)
        result = 'Not implemented.'
        response = HttpResponse(result)
        response['Content-Type'] = 'text/plain'
        return response
