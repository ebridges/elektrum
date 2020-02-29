from django.shortcuts import render
from base.views.errors import exceptions_to_web_response


@exceptions_to_web_response
def share_media(request, template_name='sharing/share_items_view.html'):
    if request.method == 'POST':
        data = request.POST.getlist('items-to-share')
        yyyymmdd = request.POST.get('yyyymmdd')
        year = request.POST.get('year')

        response_data = {'objects': data, 'yyyymmdd': yyyymmdd, 'year': int(year)}

        # save items to share, then
        # redirect as a GET to display it.

        # else if request.method == 'GET':
        # query items to share, and render page with data

        return render(request, template_name, response_data)
