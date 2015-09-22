from django.contrib.auth import logout
from django.shortcuts import redirect


def penn_logout(request):
    logout(request)
    response = redirect('https://weblogin.pennkey.upenn.edu/logout')
    response.delete_cookie(request.META.get('COSIGN_SERVICE'))
    return response
