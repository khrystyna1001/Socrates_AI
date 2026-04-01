from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MinioStorage(S3Boto3Storage):
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    bucket_name = settings.MINIO_BUCKET
    endpoint_url = settings.S3_ENDPOINT or settings.MINIO_ENDPOINT
    default_acl = None
    querystring_auth = True
    file_overwrite = True
    custom_domain = False
    addressing_style = "path"
