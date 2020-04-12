from base.views.errors import exceptions_to_web_response
from media_items.views.media_views import media_list_view


@exceptions_to_web_response
def list_items(request, year, date):
    owner_id = request.user.id
    return media_list_view(request, owner_id, year, date, 'sharing/list_items.html')
