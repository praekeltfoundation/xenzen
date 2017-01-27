import datetime
import os

import djcelery

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def abspath(*args):
    """convert relative paths to absolute paths relative to BASE_DIR"""
    return os.path.join(BASE_DIR, *args)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'xenserver',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'xenserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'xenserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = abspath('static')


# Raven (Sentry)
INSTALLED_APPS += ('raven.contrib.django.raven_compat',)


# Celery configuration options
djcelery.setup_loader()
INSTALLED_APPS += ('djcelery', 'djcelery_email',)

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_IGNORE_RESULT = True

# Uncomment if you're running in DEBUG mode and you want to skip the broker
# and execute tasks immediate instead of deferring them to the queue / workers.
# CELERY_ALWAYS_EAGER = DEBUG

# Tell Celery where to find the tasks
CELERY_IMPORTS = (
    'xenserver.tasks',
)

CELERYBEAT_SCHEDULE = {
    'update-servers': {
        'task': 'xenserver.tasks.updateVms',
        'schedule': datetime.timedelta(seconds=60)
    }
}

# Defer email sending to Celery, except if we're in debug mode,
# then just print the emails to stdout for debugging.
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Authentication + Social Auth
INSTALLED_APPS += ('social_auth',)
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/accounts/profile/'


# Crispy Forms
INSTALLED_APPS += ('crispy_forms',)
CRISPY_TEMPLATE_PACK = 'bootstrap3'


# If set to True, no task actions are completed
PRETEND_MODE = False

try:
    from local_settings import *  # noqa: F401, F403
except ImportError:
    pass
