from django.views.generic import TemplateView

from allauth.account.views import SignupView
from allauth.account.forms import LoginForm


class HomePageView(SignupView):
    template_name = 'home.html'

    # here we add some context to the already existing context
    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['login_form'] = LoginForm()  # add form to context
        return context


class AppHomePageView(TemplateView):
    template_name = 'app-home.html'
