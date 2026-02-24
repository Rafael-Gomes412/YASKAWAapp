"""
Django settings for config project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

# ======================
# SECURITY
# ======================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-very-dangerous')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Autorise toutes les connexions pour le développement Docker/VM
ALLOWED_HOSTS = ['*']


# ======================
# APPLICATIONS
# ======================

INSTALLED_APPS = [
    'jazzmin', # Doit rester avant django.contrib.admin

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'Yaskawa_app_bckend',
]

# ======================
# MIDDLEWARE
# ======================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ======================
# JAZZMIN
# ======================

JAZZMIN_SETTINGS = {
    "site_title": "YASKAWA Sales & Support Admin",
    "site_header": "YASKAWA Sales & Support",
    "site_brand": "YASKAWA",
    "welcome_sign": "Bienvenue sur l'administration YASKAWA",
    "copyright": "YASKAWA © 2026",
}

# ======================
# URLS / TEMPLATES
# ======================

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Yaskawa_app_bckend' / 'templates'], # Chemin corrigé pour tes templates
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

WSGI_APPLICATION = 'config.wsgi.application'

# ======================
# DATABASE (PostgreSQL)
# ======================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ======================
# PASSWORD VALIDATION
# ======================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ======================
# INTERNATIONALIZATION
# ======================

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ======================
# STATIC FILES (CSS, JS, Images)
# ======================

STATIC_URL = '/static/'

# INDISPENSABLE : Dossier où Docker rassemble les fichiers pour Jazzmin
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Dossier de tes fichiers statiques personnalisés
STATICFILES_DIRS = [BASE_DIR / 'Yaskawa_app_bckend' / 'static']

# ======================
# MEDIA FILES (Uploads)
# ======================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ======================
# DEFAULT PK
# ======================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================
# AUTHENTICATION URLS
# ======================

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'