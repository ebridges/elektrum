from django.shortcuts import render, get_object_or_404

from base.views.utils import assert_owner_id
from base.views.errors import exceptions_to_web_response
from media_items.models import MediaItem


@exceptions_to_web_response
def media_item_view(request, owner_id, image_id, template_name='media_items/media_item_view.html'):
    assert_owner_id(owner_id, request.user.id)
    media_item = get_object_or_404(MediaItem, id=image_id)
    return render(request, template_name, media_item.view())
