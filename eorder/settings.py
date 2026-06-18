from pathlib import Path
import dj_database_url
import os
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    # ✅ Perbaiki format URL postgres
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace(
            'postgres://', 'postgresql://', 1
        )

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            # ✅ Hapus ssl_require=True (penyebab error)
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME'  : BASE_DIR / 'db.sqlite3',
        }
    }

SECRET_KEY = config('SECRET_KEY')
DEBUG      = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=Csv()
)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',    # ✅ tambah ini SEBELUM staticfiles
    'cloudinary',
    'django.contrib.staticfiles',
    'menu',
    'pelanggan',
    'kasir',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← tambah ini
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pelanggan.middleware.SessionPelangganMiddleware',
    
]

ROOT_URLCONF = 'eorder.urls'

WSGI_APPLICATION = 'eorder.wsgi.application'

CSRF_TRUSTED_ORIGINS = [
    "https://e-order.up.railway.app",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pelanggan.context_processors.session_pelanggan',
                'kasir.context_processors.setting_kasir',
            ],
        },
    },
]




SESSION_ENGINE            = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE        = 600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

# ==============================
# CLOUDINARY — Media Storage
# ==============================
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY'   : config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Gunakan Cloudinary hanya di production
if config('USE_CLOUDINARY', default=False, cast=bool):
    DEFAULT_FILE_STORAGE = (
        'cloudinary_storage.storage.MediaCloudinaryStorage'
    )
    MEDIA_URL = '/media/'
else:
    # Development — tetap pakai local storage
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=Csv()
)

LANGUAGE_CODE = 'id'
TIME_ZONE     = 'Asia/Jakarta'
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
WHATSAPP_TOKEN    = config('WHATSAPP_TOKEN', default='')
WHATSAPP_AKTIF    = config('WHATSAPP_AKTIF', default=False, cast=bool)
BASE_URL          = config('BASE_URL', default='http://127.0.0.1:8000')
VAPID_PUBLIC_KEY  = config('VAPID_PUBLIC_KEY', default='')
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_CLAIMS      = {'sub': 'mailto:admin@eorder.com'}