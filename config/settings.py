from datetime import timedelta
from pathlib import Path

import firebase_admin
from decouple import config
from firebase_admin import credentials

from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

cred = credentials.Certificate(BASE_DIR / "credentials.json")
firebase_admin.initialize_app(cred)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

# ALLOWED_HOSTS = config(
#     "ALLOWED_HOSTS",
#     cast=lambda hosts: [host.strip() for host in hosts.split(",")],
# )
ALLOWED_HOSTS='*'

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.gis",
    "mptt",
    'django_celery_beat',
    'django_celery_results',

]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_filters",
    "rest_framework",
    "djoser",
    "django_rest_resetpassword",
    "django_extensions",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "dj_rest_auth.registration",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.facebook",
    "rolepermissions",
    "versatileimagefield",
    "fcm_django",
    'oauth2_provider',
    "rest_framework_api_key",



]

CREATED_APPS = [
    "user",
    "core",
    "utils",
    "product",
    "meta",
    "buyer_app",
    "notification",
    "geouser"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CREATED_APPS

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "geouser.middleware.CustomMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    cast=lambda hosts: [host.strip() for host in hosts.split(",")],
)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "frontend",
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": config("POSTGRES_DB"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
    }
}

print(DATABASES)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# AUTHENTICATION_BACKENDS = ['user.middleware.RemoteUserBackend']


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # "DEFAULT_PAGINATION_CLASS": "utils.pagination.CustomPageNumberPagination",
    "EXCEPTION_HANDLER": "utils.exceptions.custom_exception_handler",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
        "rest_framework_api_key.permissions.HasAPIKey",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.BasicAuthentication",

        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',  # django-oauth-toolkit >= 1.0.0

    ),
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",  # Any other renders
    ],
    "DEFAULT_PARSER_CLASSES": (
        # If you use MultiPartFormParser or FormParser, we also have a camel case version
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "utils.parsers.NestedCamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        # Any other parsers
    ),
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

if DEBUG:
    # Show browsable api only on debug mode
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer"
    )
    CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)


SOCIALACCOUNT_ADAPTER = "core.adapter.SocialAccountAdapter"
SOCIALACCOUNT_EMAIL_VERIFICATION = False
SOCIALACCOUNT_EMAIL_REQUIRED = False

REST_SESSION_LOGIN = False
REST_USE_JWT = True
JWT_AUTH_REFRESH_COOKIE = "refresh"

UI_URL = config("UI_URL", default="https://www.samuhikbazar.com/")

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "user.serializers.AuthUserSerializer",
    "JWT_SERIALIZER": "core.serializers.JWTCustomSerializer",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = "Asia/Kathmandu"
# CELERY_TIMEZONE = "UTC"


CELERY_BEAT_SCHEDULE = {
	'beattask': {
		'task': 'geouser.tasks.beattask',
		'schedule': crontab(hour=18, minute=17) #timedelta(seconds=5)  # execute every minute
	}
}

DJOSER = {
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_URL": "en/auth/reset/confirm/{uid}/{token}",
    "LOGOUT_ON_PASSWORD_CHANGE": True,
    "ACTIVATION_URL": "en/activate/{uid}/{token}",
    "BUYER_ACTIVATION_URL": "en/buyer/activate/{uid}/{token}",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Nursery API",
    "DESCRIPTION": "Documentation for API of Nursery",
    "VERSION": "1.0.0",
    # OTHER SETTINGS
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields"
    ],
    "COMPONENT_SPLIT_REQUEST": True,
}


VERSATILEIMAGEFIELD_SETTINGS = {
    "cache_length": 2592000,  ## 30 days
    "cache_name": "versatileimagefield_cache",
    "jpeg_resize_quality": 70,
    "sized_directory_name": "__sized__",
    "filtered_directory_name": "__filtered__",
    "placeholder_directory_name": "__placeholder__",
    "create_images_on_demand": True,
    "image_key_post_processor": None,
    "progressive_jpeg": False,
}

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "headshot": [
        ("full_size", "url"),
        ("thumbnail", "thumbnail__100x100"),
        ("medium_crop", "crop__250x250"),
        ("small_crop", "crop__50x50"),
    ]
}

PASSWORD_RESET_TIMEDELTA = timedelta(minutes=5)

# Time in hour
DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = (
    PASSWORD_RESET_TIMEDELTA.days * 24 + PASSWORD_RESET_TIMEDELTA.seconds / 3600
)

DJANGO_REST_RESETPASSWORD_TOKEN_CONFIG = {
    "CLASS": "django_rest_resetpassword.tokens.RandomNumberTokenGenerator",
    "OPTIONS": {"min_length": 4, "max_length": 4},
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "handlers": ["console"],
        "level": config("LOG_LEVEL"),
    },
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": config("LOG_LEVEL"),
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": config("LOG_LEVEL"),
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "verbose",
            "filename": BASE_DIR / "log/debug.log",
            "when": "D",  # specifies the interval (everyday)
            "interval": 1,  # defaults to 1
            "backupCount": 10,  # stores for 10 days then deletes and stores new
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": config("LOG_LEVEL"),
            "propagate": True,
        },
        "utils.logger": {
            "handlers": ["console"],
            "level": config("LOG_LEVEL"),
            "propagate": True,
        },
    },
}

ROLEPERMISSIONS_MODULE = "utils.roles"


DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="Samuhik Bazar <no-reply@sqcc.gov.np>", cast=str
)

EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = config("EMAIL_PORT")
GEOKRISHI_URL = config("GEOKRISHI_URL", default="http://geokrishi.farm/o/token/")
GEOKRISHI_BASE = config("GEOKRISHI_BASE", default="http://geokrishi.farm")


EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

FCM_DJANGO_SETTINGS = {"FCM_SERVER_KEY": config("FCM_SERVER_KEY")}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kathmandu"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "frontend" / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


ENVIRONMENT = config("ENVIRONMENT", default="development")
# if ENVIRONMENT == "production":
# CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE")
# SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE")

# API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"


TESTING = False

if DEBUG and not TESTING:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]
    INSTALLED_APPS += [
        "debug_toolbar",

    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
