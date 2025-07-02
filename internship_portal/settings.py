from pathlib import Path
from django.contrib.messages import constants as messages
import os

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key (replace in production)
SECRET_KEY = 'django-insecure-REPLACE_THIS_WITH_A_SECURE_KEY'

# ⚠️ DEBUG OFF for production
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']  # Add domain/IP in production

# Installed apps
INSTALLED_APPS = [
    'import_export',
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'internship',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 👈 Add this here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'internship_portal.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Optional global templates
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

WSGI_APPLICATION = 'internship_portal.wsgi.application'

# Database (SQLite for dev)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validators
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

# Timezone and language
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ✅ Static files settings
# Where collected static files will live
STATIC_ROOT = BASE_DIR / "staticfiles"

# Folder with your development static assets
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = '/static/'

# Enable WhiteNoise static file compression and caching (recommended)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
  # This is where collectstatic will store static files

# Collect your static files before deploying with:
# python manage.py collectstatic

# ✅ Message tags
MESSAGE_TAGS = {
    messages.ERROR: 'alert-danger',
    messages.SUCCESS: 'alert-success',
    messages.INFO: 'alert-info',
    messages.WARNING: 'alert-warning',
}

# ✅ Logging (recommended to debug 500 errors in production)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# Primary key config
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESSAGE_TAGS = {
    messages.ERROR: 'error',
    messages.SUCCESS: 'success',
    messages.INFO: 'info',
    messages.WARNING: 'warning',
}
