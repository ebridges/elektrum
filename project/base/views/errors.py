from traceback import format_exc
from functools import wraps
from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotAllowed,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.http.response import Http404
from rest_framework.response import Response


class BadRequestException(Exception):
    pass


class MethodNotAllowedException(Exception):
    pass


class ForbiddenException(Exception):
    pass


def format_exc_html():
    return '<pre>%s</pre>' % format_exc()


def exceptions_to_web_response(view_func):
    @wraps(view_func)
    def inner(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ForbiddenException as e:
            return HttpResponseForbidden(format_exc_html())
        except BadRequestException as e:
            return HttpResponseBadRequest(format_exc_html())
        except MethodNotAllowedException as e:
            return HttpResponseNotAllowed(str(e))
        except Http404 as e:
            return HttpResponseNotFound(format_exc_html())
        except Exception as e:
            return HttpResponseServerError(format_exc_html())

    return inner


def exceptions_to_api_response(view_func):
    @wraps(view_func)
    def inner(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ForbiddenException as e:
            return Response(str(e), status=403)
        except BadRequestException as e:
            return Response(str(e), status=400)
        except MethodNotAllowedException as e:
            return Response(str(e), status=405)
        except Exception as e:
            return Response(str(e), status=500)

    return inner
