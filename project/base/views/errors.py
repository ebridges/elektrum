from functools import wraps
from django.http import HttpResponseBadRequest, HttpResponseServerError


class BadRequestException(Exception):
    pass


def exceptions_to_http_status(view_func):
    @wraps(view_func)
    def inner(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except BadRequestException as e:
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            return HttpResponseServerError(str(e))
    return inner
