Django Penn CoSign Login and Permissions
========================================

Installing CoSign and setting up Apache
---------------------------------------
See [ISC's Apache Cosign instructions](http://www.upenn.edu/computing/weblogin/docs/apache_installation.html)
for step-by-step instructions. An example Apache httpd conf file is located in examples/.

Installing the Django app
-------------------------
Add this line to the requirements.txt of your Django project:

`git+https://github.com/wharton/django-penn-auth.git`

An example requirements.txt is located in examples/. You can also install via pip:

`pip install git+https://github.com/wharton/django-penn-auth.git`

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
    'penn_auth.remote_user.PennRemoteUserBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

INSTALLED_APPS = (
    'bootstrap3',
    'penn_auth',
)
```

Feel free to contact me with questions: sturoscy@wharton.upenn.edu

CONTRIBUTORS:
-------------
* Stephen Turoscy
