from django.http import HttpResponse
from django.views import View

class Ok(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Ok</h2>')
