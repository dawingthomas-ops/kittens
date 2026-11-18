"""
Royal Munchkin Cattery — Django settings.

Same configuration approach as the findapomsky project: python-decouple for
env-driven config, WhiteNoise for static files, optional AWS S3 media,
SQLite by default (Postgres via DB_* env vars), DRF with throttling,
security headers, SMTP email, and SEO defaults exposed to every template
through core.context_processors.site_meta.
"""

import sys
from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
TESTING = "test" in sys.argv
BUILDING_OR_MANAGING = any(
    command in sys.argv
    for command in (
        "collectstatic",
        "makemigrations",
        "migrate",
        "check",
        "showmigrations",
    )
)

# ---------------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-insecure-key-change-me")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

if not DEBUG and not TESTING and not BUILDING_OR_MANAGING:
    if SECRET_KEY == "dev-insecure-key-change-me":
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set to a strong secret in production."
        )
ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="royalmunchkincattery.com,www.royalmunchkincattery.com,*.onrender.com,localhost,127.0.0.1,0.0.0.0",
    cast=Csv(),
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://royalmunchkincattery.com,https://www.royalmunchkincattery.com,https://royalmunchkincattery.onrender.com",
    cast=Csv(),
)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in CSRF_TRUSTED_ORIGINS
    if origin.strip().startswith(("http://", "https://"))
]

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0 if DEBUG else 31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
# Render / most PaaS terminate TLS at a proxy. Without this header Django never
# sees the request as secure and SECURE_SSL_REDIRECT becomes an infinite loop.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
# How many reverse proxies sit in front of the app (used by the rate limiter).
TRUSTED_PROXY_COUNT = config("TRUSTED_PROXY_COUNT", default=1, cast=int)

if TESTING:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "config.apps.SuperuserOnlyAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "rest_framework",
    "django_filters",
    "storages",
    "core",
    "kittens",
    "reservations",
    "reviews",
    "dashboard",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RateLimitFormsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database — SQLite by default for development and production. Set the DB_*
# env vars (e.g. DB_ENGINE=django.db.backends.postgresql) to override.
# Django's ORM parameterizes every query; raw SQL is avoided everywhere.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=BASE_DIR / "db.sqlite3"),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default=""),
        "CONN_MAX_AGE": 60,
    }
}

# Local-memory cache by default (fine for a single instance). Point
# CACHE_URL-style config at Redis/Memcached when you scale past one worker
# group so the rate limiter and settings cache are shared.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "royal-munchkin",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="America/Chicago")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_STATIC_BACKEND = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if TESTING
    else "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ---------------------------------------------------------------------------
# Media storage — AWS S3. Kitten photos, gallery images, parent photos and
# review photos all flow through this backend, so views never touch the
# filesystem directly. Set USE_S3=False for local development.
# ---------------------------------------------------------------------------
USE_S3 = config("USE_S3", default=False, cast=bool)
SERVE_LOCAL_MEDIA = config("SERVE_LOCAL_MEDIA", default=DEBUG, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="royalmunchkin-media")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_CUSTOM_DOMAIN = config(
        "AWS_S3_CUSTOM_DOMAIN",
        default=f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com",
    )
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000, public"}
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_ADDRESSING_STYLE = "virtual"

    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3.S3Storage"},
        "staticfiles": {"BACKEND": _STATIC_BACKEND},
    }
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": _STATIC_BACKEND},
    }

# Reject oversized uploads early (review photos, dashboard uploads).
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "60/min", "user": "120/min"},
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# ---------------------------------------------------------------------------
# Email — reservation, contact and waitlist notifications go to the admin inbox.
# ---------------------------------------------------------------------------
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Royal Munchkin Cattery <dawingthomas@gmail.com>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Where every reservation, contact and waitlist notification is delivered.
ADMIN_NOTIFICATION_EMAIL = config("ADMIN_NOTIFICATION_EMAIL", default="dawingthomas@gmail.com")
ADMINS = [("Site Admin", ADMIN_NOTIFICATION_EMAIL)]

# ---------------------------------------------------------------------------
# Business rules
# ---------------------------------------------------------------------------
KITTEN_MIN_PRICE = 800
KITTEN_MAX_PRICE = 1000

# ---------------------------------------------------------------------------
# Site-wide SEO defaults (used by core.context_processors.site_meta)
# ---------------------------------------------------------------------------
SITE_NAME = "Royal Munchkin Cattery"
SITE_SHORT_NAME = "Royal Munchkin"
SITE_DOMAIN = config("SITE_DOMAIN", default="royalmunchkincattery.com")
GOOGLE_SITE_VERIFICATION = config("GOOGLE_SITE_VERIFICATION", default="")
BING_SITE_VERIFICATION = config("BING_SITE_VERIFICATION", default="")
GA_MEASUREMENT_ID = config("GA_MEASUREMENT_ID", default="")  # e.g. G-XXXXXXXXXX or AW-XXXXXXXXX
SITE_PHONE = config("SITE_PHONE", default="+17208196325")  # Google Voice contact number, E.164 format
WHATSAPP_NUMBER = config("WHATSAPP_NUMBER", default="")  # digits only, e.g. 15551234567
TWITTER_HANDLE = config("TWITTER_HANDLE", default="")

SITE_DEFAULT_DESCRIPTION = (
    "Royal Munchkin Cattery raises healthy, home-raised Munchkin kittens for sale at $800 to $1,000. "
    "Vet-checked, vaccinated, microchipped, with a written health guarantee and safe delivery support."
)
SITE_DEFAULT_KEYWORDS = (
    "munchkin kittens for sale, munchkin cat breeder, munchkin kittens near me, short leg cats for sale, "
    "longhair munchkin kittens, shorthair munchkin kittens, affordable munchkin kittens, "
    "calico munchkin kitten, tabby munchkin kitten, munchkin cattery, healthy munchkin kittens"
)
SITE_LOCATION_SUMMARY = "Serving families across the United States"
SITE_SERVICE_AREAS = ["United States"]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:overview"
LOGOUT_REDIRECT_URL = "core:home"

# ---------------------------------------------------------------------------
# Logging — surface email/SMTP failures instead of silently swallowing them.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "[{levelname}] {name}: {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {"royalmunchkin": {"handlers": ["console"], "level": "INFO", "propagate": False}},
}
