import os

from configurations import Configuration

import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseConfiguration(Configuration):
    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

    # Django environ
    # FIXME: we must have oportunity upload settings from env file
    # DOTENV = os.path.join(BASE_DIR, '.env')

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = '3@a)-cbt514^!a%qiotx$su4%29p@dxfrd-qb(oouzbp^@!+gr'

    # FIXME: we must setup that list
    ALLOWED_HOSTS = ['*']

    # Database
    # https://docs.djangoproject.com/en/1.11/ref/settings/#databases

    DATABASES = {
        'default': dj_database_url.config(
            default='postgres://journal:journal@journal_postgres/journal'
        )
    }

    TROOD_AUTH_SERVICE_URL =  os.environ.get(
        'TROOD_AUTH_SERVICE_URL', 'http://authorization.trood:8000/'
        )

    SERVICE_DOMAIN = os.environ.get('SERVICE_DOMAIN')
    SERVICE_AUTH_SECRET = os.environ.get('SERVICE_AUTH_SECRET')

    # Application definition

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'raven.contrib.django.raven_compat',
        'rest_framework',
        'django_filters',
        'journal.api',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'journal.urls'

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

    WSGI_APPLICATION = 'journal.wsgi.application'


    # Internationalization
    # https://docs.djangoproject.com/en/1.11/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'trood_auth_client.authentication.TroodTokenAuthentication',
        ),
        'PAGINATE_BY': 10,
    }

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'WARNING',  # To capture more than ERROR, change to WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

    ENABLE_RAVEN = os.environ.get('ENABLE_RAVEN', "False")

    if ENABLE_RAVEN == "True":
        RAVEN_CONFIG = {
            'dsn': os.environ.get('RAVEN_CONFIG_DSN'),
            'release': os.environ.get('RAVEN_CONFIG_RELEASE')
        }

    STATIC_URL = '/static/'


class Development(BaseConfiguration):
    DEBUG = True


class Production(BaseConfiguration):
    DEBUG = False

