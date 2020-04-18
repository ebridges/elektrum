from logging import info

from base.views.errors import exceptions_to_web_response, BadRequestException
from sharing.models import Share
from sharing.views.common import do_delete_share


@exceptions_to_web_response
def share_log_delete(request, id=None):
    info(f'share_log_delete({id})')
    if not id:
        raise BadRequestException('Share not identified.')
    share = Share.objects.get(pk=id)
    return do_delete_share(share)
