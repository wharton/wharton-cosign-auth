Django Penn CoSign Custom User Template
=======================================

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
    'pennuser.auth_backends.PennRemoteUserBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

INSTALLED_APPS = (
    'bootstrap3',
    'pennuser',
)
```

Or, for prod.py only (handy, if you want to use Django's auth for local dev):

```
MIDDLEWARE_CLASSES += (
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
)

AUTHENTICATION_BACKENDS += (
    'pennuser.auth_backends.PennRemoteUserBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

INSTALLED_APPS += (
    'penn_auth',
)
```

Then, you can begin to customize the models.py (and auth_backend.py if necessary).

Don't forget to run this to create the necessary pennuser_pennuser table in your Django Project's database after adding the pennuser app to INSTALLED_APPS:

```
python manage.py migrate
```

Feel free to contact me with questions: sturoscy@wharton.upenn.edu

CONTRIBUTORS:
-------------
* Stephen Turoscy
