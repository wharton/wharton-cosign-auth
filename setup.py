import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='penn_auth',
    version='0.1',
    packages=['penn_auth'],
    include_package_data=True,
    license='BSD License',
    description="A simple Django app to use the University of Pennsylvania's CoSign auth.",
    long_description=README,
    url='https://github.com/wharton/django-penn-auth/',
    author='Stephen Turoscy, The Wharton School',
    author_email='sturoscy@wharton.upenn.edu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
