"""
Django settings for totoro project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""


from datetime import timedelta
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Internal
    "accounts",
    "posts.apps.PostsConfig",
    "friends",
    "notifications",
    # External
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # Auth
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.discord",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


if not DEBUG:
    MIDDLEWARE += [
        "totoro.middleware.exceptions.ExceptionMiddleware",
    ]


AUTH_USER_MODEL = "accounts.User"


ROOT_URLCONF = "totoro.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "totoro.wsgi.application"

# CORS
# https://github.com/adamchainz/django-cors-headers

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CSRF_TRUSTED_ORIGINS = [
    "locahost:8000",
    "locahost:3000",
]
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]
CORS_ALLOW_CREDENTIALS = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3"
        # "ENGINE": "django.db.backends.postgresql",
        # "NAME": config("DB_NAME"),
        # "USER": config("DB_USERNAME"),
        # "PASSWORD": config("DB_PASSWORD"),
        # "HOST": config("DB_HOST"),
        # "PORT": config("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_ROOT = "static/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# BUCKET

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

STATIC_URL = "/static/"

MEDIA_ROOT = "media/"
MEDIA_URL = "/media/"
UPLOAD_ROOT = "uploads/"


DOWNLOAD_ROOT = BASE_DIR / "static/media/downloads"

DOWNLOAD_URL = STATIC_URL + "media/downloads"
CALLBACK_URL = "http://localhost:3000"


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ),
    "EXCEPTION_HANDLER": "totoro.middleware.exceptions.handle_exception",
    "DEFAULT_THROTTLE_RATES": {
        "loginAttempts": "6/hr",
        "user": "1000/min",
        "anon": "1000/min",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
}

REST_AUTH_SERIALIZERS = {
    "JWT_TOKEN_CLAIMS_SERIALIZER": "accounts.api.serializers.TotoroTokenObtainPairSerializer",
    # "USER_DETAILS_SERIALIZER": "accounts.api.serializers.TotoroUserModelSerializer",
}


# JWT Settings
SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_LIFETIME": timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "USER_ID_FIELD": "user_id",  # for the totoro user model
    "USER_ID_CLAIM": "user_id",
    "SIGNING_KEY": SECRET_KEY,
}

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "SCOPE": [
            "user",
        ],
    },
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
}

# we are turning off email verification for now
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = False

SITE_ID = 1  # https://dj-rest-auth.readthedocs.io/en/latest/installation.html#registration-optional
REST_USE_JWT = True  # use JSON Web Tokens
JWT_AUTH_COOKIE = "totoro-access-token"
JWT_AUTH_REFRESH_COOKIE = "totoro-refresh-token"
JWT_AUTH_SAMESITE = "Lax"


# CELERY
BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Kathmandu"

# API CACHE
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 60 * 1  # 1 hour

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {"format": "[contactor] %(levelname)s %(asctime)s %(message)s"},
    },
    "handlers": {
        # Send all messages to console
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        # Warning messages are sent to admin emails
        "mail_admins": {
            "level": "WARNING",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "totoro.log",
        },
    },
    "loggers": {
        # This is the "catch all" logger
        "": {
            "handlers": ["console", "mail_admins", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
