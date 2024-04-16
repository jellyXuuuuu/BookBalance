
from functools import wraps
from django.http import HttpRequest, HttpResponse, JsonResponse
from . import stateCode
from django.utils.translation import gettext as _, get_language


def login_required(func):
    @wraps(func)
    def _wrapped_func(request, *args, **kwargs):
        if(request.user.is_authenticated):
            return func(request, *args, **kwargs)
        else:
            return JsonResponse({'state': stateCode.NOTLOGGIN, 'info': _('user does not login')})

    return _wrapped_func
