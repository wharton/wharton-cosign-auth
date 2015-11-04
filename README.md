Django Wharton CoSign Login and Permissions
===========================================

Installing CoSign and setting up Apache
---------------------------------------
See [ISC's Apache Cosign instructions](http://www.upenn.edu/computing/weblogin/docs/apache_installation.html)
for step-by-step instructions. An example Apache httpd conf file is located in examples/.

Installing the Django app
-------------------------
Add this line to the requirements.txt of your Django project:

`git+https://github.com/wharton/wharton-cosign-auth.git`

An example requirements.txt is located in examples/. You can also install via pip:

`pip install git+https://github.com/wharton/wharton-cosign-auth.git`

Middleware and authentication backends in settings.py
--------------------------------------
In order to integrate CoSign with the Django auth system, 
we have to tell Django to use the `REMOTE_USER` server variable. 
You can use `RemoteUserMiddleware` that ships with Django, or
the custom `PennRemoteUserBackend` from this module, which subclasses 
`RemoteUserMiddleware` to remove password handling, since Cosign handles passwords during authentication.

Here is an example of this configuration:

```
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'wharton_cosign_auth.remote_user.WhartonRemoteUserBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

INSTALLED_APPS = (
    'bootstrap3',
    'wharton_cosign_auth',
)
```
Logging out
-----------
To add a logout function to your urls.py, do the following:

```
from django.conf.urls import patterns, include, url
from django.contrib import admin

from wharton_cosign_auth.views import penn_logout


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/', penn_logout, name='penn-logout'),
)
```

Using Built-in Permissions to Decorate Views
--------------------------------------------
wharton_cosign_auth gives you the ability to use view decorators using Wharton permissions.
Simply decorate a view by doing something similar to the following:

```
from django.http import HttpResponse

from wharton_cosign_auth.permissions import wharton_permission


@wharton_permission(['STAFF', 'WCIT'])
def my_view(request):
    return HttpResponse("Hello, World!")
```

The decorator checks https://apps.wharton.upenn.edu/api/v1/adgroups endpoint to see if the
user is in the supplied group(s).  If not, a 403 Forbidden will be returned.

Just make sure you pass a list (i.e. ['MKTG-STAFF']) even if you are only checking against one group.

Feel free to contact me with questions: sturoscy@wharton.upenn.edu

Running Test Suite
------------------
To run the tests for wharton cosign-auth first make sure you have the correct dependencies installed. Then execute tests.py by navigating into wharton_cosign_auth

```
pip install requirements.txt
cd wharton_cosign_auth
python tests.py
```


CONTRIBUTORS:
-------------
* Stephen Turoscy
* Timothy Allen
