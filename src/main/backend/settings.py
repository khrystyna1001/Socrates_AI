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
    'django_minio_backend.apps.DjangoMinioBackendConfig',
    
    # Third Party
    'rest_framework',
    'corsheaders',
    'storages',
    'pgvector',
    'django_celery_results',
    
    # Local
    'bart',
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
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]

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

ROOT_URLCONF = 'backend.urls'

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

RAW_ENDPOINT = os.getenv("S3_ENDPOINT", "play.min.io").replace("http://", "").replace("https://", "")

MINIO_COMMON_OPTIONS = {
    "MINIO_ENDPOINT": RAW_ENDPOINT,
    "MINIO_ACCESS_KEY": os.getenv("MINIO_ROOT_USER"),
    "MINIO_SECRET_KEY": os.getenv("MINIO_ROOT_PASSWORD"),
    "MINIO_USE_HTTPS": True,
    "MINIO_REGION": "us-east-1",
    "MINIO_URL_EXPIRY_HOURS": timedelta(days=1),
    "MINIO_CONSISTENCY_CHECK_ON_START": True,
}

STORAGES = {
    "default": {
        "BACKEND": "django_minio_backend.models.MinioBackend",
        "OPTIONS": {
            **MINIO_COMMON_OPTIONS,

            "MINIO_DEFAULT_BUCKET": os.getenv("MINIO_BUCKET_NAME", "docs"), 
            "MINIO_PRIVATE_BUCKETS": ["django-backend-dev-private"],
            "MINIO_PUBLIC_BUCKETS": [os.getenv("MINIO_BUCKET_NAME", "docs")],
        },
    },
    "staticfiles": {
        "BACKEND": "django_minio_backend.models.MinioBackendStatic",
        "OPTIONS": {
            **MINIO_COMMON_OPTIONS,
            "MINIO_STATIC_FILES_BUCKET": "static",
        },
    },
}

# URLs for media and static
MEDIA_URL = f'{MINIO_ENDPOINT}/{MINIO_BUCKET}/'
STATIC_URL = '/static/'

# --- CELERY ---
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672//')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = "Australia/Tasmania"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_TASK_ROUTES = {
    'bart.tasks.manager_find_missing_book': {'queue': 'manager_queue'},
    'bart.tasks.install_single_book': {'queue': 'installer_queue'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'