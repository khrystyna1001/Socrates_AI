import os
from pathlib import Path
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    
    # Third Party
    'rest_framework',
    'corsheaders',
    'storages',
    'pgvector',
    'django_celery_results',
    'rest_framework_simplejwt',
    'django_lifecycle_checks',
    'django_logic',

    
    # Local
    'bart',
    'documents',
    'services'
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- CORS SETTINGS (For Vue) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://0.0.0.0:9000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)

# --- CSRF (For Vue) ---
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173', 
    'http://0.0.0.0:5173', 
    'http://127.0.0.1:5173'
    ]

ROOT_URLCONF = 'backend.urls'

# --- DRF ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# --- TEMPLATES ---
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

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'master'),
        'USER': os.getenv('POSTGRES_USER', 'user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'supersecretpassword'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# --- MINIO / S3 STORAGE ---
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET_NAME", "docs")
MINIO_USER_BUCKET_PREFIX = os.getenv("MINIO_USER_BUCKET_PREFIX", "user-files")

DEFAULT_FILE_STORAGE = "documents.storage.MinioStorage"
PRIVATE_STORAGE_CLASS = "documents.storage.MinioStorage"

# MEDIA_URL = f'{MINIO_ENDPOINT}/{MINIO_BUCKET}/media/'
STATIC_URL = "/static/"

STORAGES = {
    "default": {
        "BACKEND": "documents.storage.MinioStorage",
    },
    "private": {
        "BACKEND": "documents.storage.MinioStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# --- CELERY ---
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672//')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = "Australia/Tasmania"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Simple JWT ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
}
