from django.views.generic import TemplateView
from django.shortcuts import render

from allauth.account.views import SignupView
from allauth.account.forms import LoginForm

from base.views.errors import exceptions_to_http_status
from base.views.utils import media_url
from date_dimension.models import DateDimension
from media_items.models import MediaItem


class HomePageView(SignupView):
    template_name = 'home.html'

    # here we add some context to the already existing context
    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['login_form'] = LoginForm()  # add form to context
        return context


@exceptions_to_http_status
def app_home_page_view(request, template_name='app-home.html'):
    media_items = MediaItem.objects.raw('''select distinct on (d.year) m.* 
                                    from media_item m, date_dim d 
                                    where m.create_day_id = d.yyyymmdd 
                                    order by d.year, random()''')
    data = []
    for mi in media_items:
        data.append({'year': str(mi.create_day_id)[:4], 'url': media_url(mi.file_path)})

    return render(request, template_name, {'objects': data})
