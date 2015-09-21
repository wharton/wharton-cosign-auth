from django.core.exceptions import PermissionDenied

from functools import wraps

from penn_auth.utilities import call_wisp_api

def wharton_permission(permission):
  def wharton(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
      if request.META.get('REMOTE_USER') is not None:
        url = 'https://apps.wharton.upenn.edu/wisp/api/v1/adgroups/%s' % request.META.get('REMOTE_USER')
        response = call_wisp_api(url)
        if str(permission) in response.get('groups'):
          return func(request, *args, **kwargs)
        else:
          raise PermissionDenied
      else:
        raise PermissionDenied
    return wrapper
  return wharton

class WhartonPermission(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(WhartonPermission, cls).as_view(**initkwargs)
        return wharton_permission(view)
