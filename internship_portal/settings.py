from pathlib import Path
from django.contrib.messages import constants as messages
import os
from decouple import config, Csv
import dj_database_url
from dotenv import load_dotenv

load_dotenv()


# Environment
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")

# Security Settings
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')  # ✅ Load the .env file here


# Secret key (replace in production)
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default-key')

# ⚠️ DEBUG OFF for production
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')
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

JAZZMIN_SETTINGS = {
    "site_title": "Internship Portal Admin",
    "site_header": "VelTech Internship Portal",
    "site_brand": "VelTech",
    "site_logo": "images/LOGO.png",  # Path to your logo in /static/images/
    "login_logo": "images/VELTECH.png",
    "welcome_sign": "Welcome to VelTech Internship Admin Panel",
    "copyright": "VelTech",

    # Top menu links
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Company List", "model": "internship.company"},
        {"name": "Student List", "model": "internship.student"},
    ],

    # User menu (top right corner)
    "usermenu_links": [
        {"name": "Support", "url": "https://veltech.edu.in/support", "new_window": True},
    ],

    # Side menu (app ordering)
    "order_with_respect_to": ["auth", "internship"],

    # App icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "internship.company": "fas fa-building",
        "internship.student": "fas fa-user-graduate",
    },

    # Theme and layout options
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "changeform_format": "horizontal_tabs",  # or "collapsible", "single"

    # UI tweaks
    "custom_css": "css/admin_custom.css",  # Optional
    "custom_js": "js/admin_custom.js",     # Optional
    "use_google_fonts_cdn": True,
    "changeform_format_overrides": {
        "auth.user": "collapsible",
    },

    "language_chooser": False,
    "hide_models": [
        "auth.User",
        "auth.Group",
    ]
}



# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 👈 Add this here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'internship.middleware.MaintenanceModeMiddleware',
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
        'default': dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=not DEBUG  # Disable SSL in local dev only
        )
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
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Source static files during development
STATIC_ROOT = BASE_DIR / "staticfiles"  # Collected static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # Enable caching and compression

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


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')


GOOGLE_CONFIG = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
}

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")  # put in .env
# GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, "google_service.json")



INSTALLED_APPS += ["django_crontab"]
CRONJOBS = [
    ('*/1 * * * *', 'internship.utils.google_sheets.sync_sheets_to_db')  # every 5 min
]
