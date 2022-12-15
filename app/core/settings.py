import os
import socket
from pathlib import Path
import redis
import dj_database_url
from decouple import config
from datetime import timedelta
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = int(os.environ.get("DEBUG", 1))

ALLOWED_HOSTS = ["127.0.0.1", "0.0.0.0", "localhost", "api", "ec2-44-193-10-88.compute-1.amazonaws.com"]
INTERNAL_IPS = ["127.0.0.1"]
if DEBUG:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'storages',
    'rest_framework',
    'django_filters',
    'import_export',
    'debug_toolbar',
    'drf_spectacular',
    'core.celery.CeleryConfig',
    'user',
    'workspaces',
    'tms',
    'dukka_connection',
]

AUTH_USER_MODEL = "user.User"

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ValidationErrorMiddleware',
    'core.middleware.CaptureExceptionMiddleware'
]

ROOT_URLCONF = 'core.urls'
IMPORT_EXPORT_USE_TRANSACTIONS = True

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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'
CORS_ALLOW_ALL_ORIGINS = True
LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

# Database

db_name = os.getenv("POSTGRES_DB")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST")
db_user = os.getenv("POSTGRES_USER")

db_uri = f"postgres://{db_user}:{db_password}@{db_host}:5432/{db_name}"
# DATABASES = {"default": dj_database_url.parse(db_uri, conn_max_age=600)}

# DATABASES = {
#     'default': dj_database_url.parse(db_uri, conn_max_age=600),
#     'dukka_db': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get('DUKKA_DB_NAME'),
#         'USER': os.environ.get('DUKKA_DB_USER'),
#         'PASSWORD': os.environ.get('DUKKA_DB_PASSWORD', 'P0llE@sy#999&'),
#         'HOST': os.environ.get('DUKKA_DB_HOST'),
#         'PORT': os.environ.get('DUKKA_DB_PORT'),
#     },
# }
DATABASES = {
    'default': dj_database_url.parse(db_uri, conn_max_age=600),
    'dukka_db': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ebdb',
        'USER': 'dukkauser',
        'PASSWORD': 'dukkadevelopment',
        'HOST': 'awseb-e-uy8fa6nmqm-stack-awsebrdsdatabase-httvc0lgknow.cbooj0bmyvkb.us-east-1.rds.amazonaws.com',
        'PORT': 5432,
    },
}
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.CustomPagination',
    'PAGE_SIZE': 20,
    # 'DATE_INPUT_FORMATS': ["%d/%m/%Y", ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

APP_NAME = os.getenv('APP_NAME')
STATIC_ROOT = os.path.join(BASE_DIR, f'staticfiles/{APP_NAME}')
STATIC_TMP = os.path.join(BASE_DIR, f'static/{APP_NAME}')
os.makedirs(STATIC_TMP, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'core.storage_backends.MediaStorage'
PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'core.storage_backends.PrivateMediaStorage'

USE_S3 = os.environ.get('USE_S3', default=False)

if USE_S3:
    # AWS S3
    S3_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    S3_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{ AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    # Static
    STATIC_LOCATION = 'staticfiles'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'core.storage_backends.S3StaticStorage'

# Media
    MEDIA_LOCATION = 'mediafiles'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'core.storage_backends.S3MediaStorage'

else:
    # SIMONE server
    SIMONE_SERVER_URL = os.environ.get("SIMONE_LOCAL_SERVER_URL")

    # Static
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # Media
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Email Settings
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_FROM = os.environ.get('SENDER_EMAIL')

CLIENT_URL = os.environ.get('CLIENT_URL')

TOKEN_LIFESPAN = 24 * 7  # hours

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"


CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json', 'application/x-python-serialize']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

FLOWER_BASIC_AUTH = os.environ.get('FLOWER_BASIC_AUTH')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": APP_NAME
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 1
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

SPECTACULAR_SETTINGS = {
    'SCHEMA_PATH_PREFIX': r'/api/v1',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.generators.SchemaGenerator',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_SPLIT_REQUEST': True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "displayRequestDuration": True
    },
    'UPLOADED_FILES_USE_URL': True,
    'TITLE': 'Simone Application API',
    'DESCRIPTION': 'Simone API Doc',
    'VERSION': '1.0.0',
    'LICENCE': {'name': 'BSD License'},
    'CONTACT': {'name': 'Folakemi Umar', 'email': 'nimah@dukka.com'},

    # Oauth2 related settings. used for example by django-oauth2-toolkit.
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#oauth-flows-object
    'OAUTH2_FLOWS': [],
    'OAUTH2_AUTHORIZATION_URL': None,
    'OAUTH2_TOKEN_URL': None,
    'OAUTH2_REFRESH_URL': None,
    'OAUTH2_SCOPES': None,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# if DEBUG == 0:
#     sentry_sdk.init(
#         dsn=os.environ.get('SENTRY_DSN', None),
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=1.0,

#         # If you wish to associate users to errors (assuming you are using
#         # django.contrib.auth) you may enable sending PII data.
#         send_default_pii=True
#     )
