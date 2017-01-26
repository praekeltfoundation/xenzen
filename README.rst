XenZen
======

.. image:: https://travis-ci.org/praekeltfoundation/xenzen.svg?branch=develop
    :target: https://travis-ci.org/praekeltfoundation/xenzen
.. image:: https://codecov.io/gh/praekeltfoundation/xenzen/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/praekeltfoundation/xenzen

A Django UI for managing `XenServer <http://xenserver.org/>`_ in the simplest possible way.

Getting started
---------------
To install XenZen run: ::

    $ git clone https://github.com/praekeltfoundation/xenzen.git
    $ cd xenzen/
    $ virtualenv ve
    $ . ./ve/bin/activate
    $ pip install -e .

To start a development server listening on ``127.0.0.1:8000``, with a SQLite database, run: ::

    $ export DJANGO_SETTINGS_MODULE=xenserver.settings
    $ django-admin syncdb
    $ django-admin collectstatic
    $ django-admin runserver

To configure XenZen further, create the file ``local_settings.py`` containing extra Django settings. For example, to configure a PostgreSQL database: ::

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
