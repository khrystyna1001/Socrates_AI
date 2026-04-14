import logging
import re
from uuid import uuid4

from django.conf import settings
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class PGVectorDB(models.Model):
    def save(self, embeddings):
        try:
            from documents.models import DocumentChunk

            DocumentChunk.save(embeddings)
        except Exception as err:
            logging.warning(err)


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
    location = "docs"
    BUCKET_RE = re.compile(r"[^a-z0-9-]")

    def get_storage(self, bucket_name: str | None = None) -> "MinioStorage":
        storage = self.__class__()
        if bucket_name:
            storage.bucket_name = bucket_name
        return storage

    def build_user_bucket_name(self, user_id: int) -> str:
        prefix = getattr(settings, "MINIO_USER_BUCKET_PREFIX", "user-files")
        raw = f"{prefix}-{user_id}".lower()
        bucket = self.BUCKET_RE.sub("-", raw).strip("-")
        return bucket[:63] or f"user-{user_id}"

    def ensure_bucket_exists(self, bucket_name: str) -> None:
        storage = self.get_storage(bucket_name)
        client = storage.connection.meta.client
        try:
            client.head_bucket(Bucket=storage.bucket_name)
        except client.exceptions.ClientError as err:
            error_code = err.response.get("Error", {}).get("Code")
            if error_code not in {"404", "NoSuchBucket"}:
                raise
            client.create_bucket(Bucket=storage.bucket_name)

    def upload_user_file(self, uploaded_file, bucket_name: str) -> str:
        self.ensure_bucket_exists(bucket_name)

        safe_name = uploaded_file.name.replace("/", "_")
        object_key = f"{uuid4().hex}_{safe_name}"

        storage = self.get_storage(bucket_name)
        uploaded_file.seek(0)
        storage.save(object_key, uploaded_file)
        return object_key

    def get_file_stream(self, bucket_name: str, object_key: str):
        storage = self.get_storage(bucket_name)
        return storage.open(object_key, mode="rb")

    def file_exists(self, bucket_name: str, object_key: str) -> bool:
        storage = self.get_storage(bucket_name)
        return storage.exists(object_key)

    def document_exists(self, payload) -> bool:
        from documents.models import Document

        doc_id = payload["doc_id"]
        doc = Document.objects.get(pk=doc_id)

        bucket_name = doc.minio_bucket
        return self.file_exists(bucket_name, doc.file.name)
