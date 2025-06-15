from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# For local development, set ENVIRONMENT=development.
# For production, set ENVIRONMENT=production.

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
if ENVIRONMENT == 'production':
    from .settings_prod import *
else:
    from .settings_dev import *

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'maintenance_mode',
    'home',
    'cvv',
    'orders',
    'users',
    'crypto_configs',
    'billing',
    'category',
    'django_filters',
    'widget_tweaks',
    'captcha',
    'dbbackup',
    'ticket',
    'bininfo',
    'import_export',
    'celery_progress',
    'sellers',
    'cart',
    'core_services',
]

MIDDLEWARE = [
    'livecc.rate_limit_middleware.AdvancedRateLimitMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'livecc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_count',
                'cvv.context_processors.card_count',
                'ticket.context_processors.pending_ticket_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'livecc.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": config('SQL_ENGINE'),
        "NAME": config('SQL_DATABASE'),
        "USER": config('SQL_USER'),
        "PASSWORD": config('SQL_PASSWORD'),
        "HOST": config('SQL_HOST'),
        "PORT": config('SQL_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
   os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====maintenance_mode====
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_STAFF = True
# ====maintenance_mode====

#====================Content Security Policy==================
CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = (
    "'self'",
    "data:",  # Allow data: URIs for images
    "https://cdn.jsdelivr.net",  # Allow images from CDN
)
CSP_STYLE_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",  # Add this line
    "'unsafe-inline'",
)

CSP_SCRIPT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://code.jquery.com",  # Add this line
    "'unsafe-inline'",
)

CSP_FONT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",  # Existing source
    "https://cdnjs.cloudflare.com",  # Add this line to include Font Awesome CDN
)

#====================Celery Settings==================

REDIS_PASSWORD = "HelloMark2024"

# Correctly configured CACHES dictionary with Redis password from environment variable
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

# Celery configuration using the same Redis password
CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@localhost:6379/0'
CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# CELERY_BEAT_SCHEDULE for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'clear_expired_cart_items_every_minute': {
        'task': 'cart.tasks.clear_expired_cart_items',
        'schedule': 300.0,  # Run every 5 minutes
    },
}
#====================Celery Settings==================

