from django_minio_backend.models import MinioBackend

def get_public_storage():
    return MinioBackend(
        bucket_name='django-backend-dev-public',
        storage_name='default',
    )

def get_private_storage():
    return MinioBackend(
        bucket_name='django-backend-dev-private',
        storage_name='default',
    )