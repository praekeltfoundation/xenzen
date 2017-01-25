XenZen
======

.. image:: https://travis-ci.org/praekeltfoundation/xenzen.svg?branch=develop
  :target: https://travis-ci.org/praekeltfoundation/xenzen
.. image:: https://codecov.io/gh/praekeltfoundation/xenzen/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/praekeltfoundation/xenzen

A Django UI for managing XenServer in the simplest possible way.

Installing
----------
::

    $ git clone https://github.com/praekeltfoundation/xenzen.git
    $ cd xenzen/
    $ virtualenv ve
    $ . ./ve/bin/activate
    $ pip install -r requirements-dev.txt

Create skeleton/local_settings.py ::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'xenzen',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }


Add files in config to the right place, and make sure the paths are correct, and configure a non-root user. run manage.py syncdb, manage.py migrate and manage.py collectstatic
