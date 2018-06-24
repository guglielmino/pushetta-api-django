# coding=utf-8

###
# Django settings for pushetta project.
###


import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENVIRONMENT = os.environ['DJANGO_ENV'] # Env variable "dev" or "prod"
BASE_URL="http://www.pushetta.com"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Secret key in environment variable
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', ]

SITE_ID = 1


# Application definition

INSTALLED_APPS = (
    # The Django sites framework is required
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'haystack',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'taggit',
    'api',
    'core',
    'www',
    'drip',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    # Required by allauth template tags
    "django.core.context_processors.request",
    # allauth specific context processors
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",

)

ROOT_URLCONF = 'pushetta.urls'
WSGI_APPLICATION = 'pushetta.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DATABASE_NAME',
        'TEST_NAME' : 'TEST_DATABASE_NAME',
        'USER': 'DATABASE_USER',
        'PASSWORD': 'DATABASE_PASSWORD',
        'HOST': '',
        'PORT': '',
    }
}

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, '..', 'templates'),
    os.path.join(BASE_DIR, '..', 'templates/www'),
)

# Credenziali per il push su Mosquitto
MOSQ_HOST="localhost"
MOSQ_PORT=1884
MOSQ_USERNAME="USER"
MOSQ_PASSWORD="PASSWORD"
# Configurazione per il brocker di backend di Celery
BROKER_URL = 'amqp://USER:PASSWORD@localhost:5672/pushetta'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_TIMEZONE = 'Europe/Rome'

CELERY_ALWAYS_EAGER = True                  
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

LOGIN_REDIRECT_URL = '/'

# django-allauth settings
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USERNAME_MIN_LENGTH = 4

# Configurazione per l'invio delle email
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = ''

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'PAGINATE_BY': 100
}

# Settings del sistema di autenticazione token based
JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': False,  # Token con valitidà infinita
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300)
}

# Con questo signal processo l'aggiunta di un mode indicizzato è aggiornata nel search engine immediatamente
# Nota: è pesante da gestire su motori diversi da Solr e ElasticSearch
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL' : u"http://localhost:8081/solr",
    },
}
HAYSTACK_IDENTIFIER_METHOD = 'core.utils.custom_get_identifier'

SWAGGER_SETTINGS = {
    "exclude_namespaces": ["feedback-api", "messages-api", "publisher-api", "subscribers-api", "subscriptions-api", "android-api"],  # List URL namespaces to ignore
    "api_version": '1.0',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
                          'get',
                          'post',
                          'put',
                          'patch',
                          'delete'
    ],
    "api_key": '',  # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}



# Configurazione per l'utilizzo di Redis
REDIS_DB = 0
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY_PREFIX = "ptta_dev"

# Google cloud messaging
GCM_KEY = ""

# Apple APNS
APNS_CERT_FILE = os.path.join(BASE_DIR, '..', "certs/", "cert-dev.pem")
APNS_KEY_FILE = os.path.join(BASE_DIR, '..', "certs/", "cert-dev.pem")
APNS_IS_SANDBOX = True

# Push notifications on Safari browser
APNS_SAFARI_CERT_FILE=os.path.join(BASE_DIR, '..', "certs/", "cert-safari-dev.pem")
APNS_SAFARI_KEY_FILE = os.path.join(BASE_DIR, '..', "certs/", "cert-safari-dev.pem")
APNS_SAFARI_IS_SANDBOX = True

# Durata dei token OTT (un mese)
OTT_DURATION_SECONDS = 259200

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

#STATIC_ROOT = os.path.join(BASE_DIR, '..', 'dev_static/')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', '..', 'static/collect/')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '..', "dev_static/"),
)

# Settings for django-bootstrap3
BOOTSTRAP3 = {
    'include_jquery': False,
    'jquery_url': '/static/site/js/jquery-1.7.2.min.js',
    'base_url': '/static/site/',
    'css_url': '/static/site/css/bootstrap.min.css',
    'javascript_url': '/static/site/js/bootstrap.js',
}

# Media (file uploads)
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'uploads/')
MEDIA_URL = '/uploads/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s [%(name)s: %(lineno)s] -- %(message)s',
            'datefmt': '%m-%d-%Y %H:%M:%S'
        },
    },
    'handlers': {
        'logfile': {
            'level': 'INFO',
            'filters': None,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', '..', 'log/pushetta-{0}.log'.format(ENVIRONMENT)),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 3,
            'formatter': 'standard'
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', '..', 'log/debug-{0}.log'.format(ENVIRONMENT)),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard'
        },
        'default_logger': {
            'level': 'WARNING',
            'filters': None,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', '..', 'log/default-{0}.log'.format(ENVIRONMENT)),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard'
        },
        'celery_logger': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', '..', 'log/celery-{0}.log'.format(ENVIRONMENT)),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard'
        },
        'celery_task_logger': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', '..', 'log/celery-tasks-{0}.log'.format(ENVIRONMENT)),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default_logger'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'feedmanager': {
            'handlers': ['logfile', 'debug_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'recipemanager': {
            'handlers': ['logfile', 'debug_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'menumanager': {
            'handlers': ['logfile', 'debug_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'core.tasks': {
            'handlers': ['celery_task_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['celery_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}



