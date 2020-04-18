from django.shortcuts import render

from base.views.errors import exceptions_to_web_response
from base.views.utils import assert_owner_id


@exceptions_to_web_response
def media_item_upload_view(
    request, owner_id, template_name='media_items/media_item_upload_view.html'
):
    assert_owner_id(owner_id, request.user.id)
    return render(request, template_name)
