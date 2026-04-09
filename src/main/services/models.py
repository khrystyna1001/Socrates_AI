from django.db import models, transaction
from django.conf import settings
from django.utils.module_loading import import_string
from django.http import JsonResponse

from documents.tasks import _get_doc_or_error
from documents.models import DocumentChunk

from uuid import uuid4
import logging
import re

# Create your models here.
class PGVectorDB(models.Model):

    def save(self, payload):
        try:
            doc_id = payload["doc_id"]

            doc = _get_doc_or_error(doc_id)

            chunks = payload.get("chunks", [])
            vectors = payload.get("vectors", [])

            with transaction.atomic():
                DocumentChunk.objects.filter(document=doc).delete()
                DocumentChunk.objects.update_or_create(
                    [
                        DocumentChunk(
                            document=doc,
                            chunk_index=i,
                            content=chunk,
                            embedding=vectors[i] if i < len(vectors) else None,
                        )
                        for i, chunk in enumerate(chunks)
                    ]
                )
        except Exception as err:
            logging.warning(err)

class MinioStorage(models.Model):

    BUCKET_RE = re.compile(r"[^a-z0-9-]")
    storage = import_string(settings.PRIVATE_STORAGE_CLASS)

    def get_storage(self, bucket_name: str):
        self.storage.bucket_name = bucket_name


    def build_user_bucket_name(self, user_id: int) -> str:
        prefix = getattr(settings, "MINIO_USER_BUCKET_PREFIX", "user-files")
        raw = f"{prefix}-{user_id}".lower()
        bucket = self.BUCKET_RE.sub("-", raw).strip("-")
        return bucket[:63] or f"user-{user_id}"


    def ensure_bucket_exists(self) -> None:
        client = self.storage.connection.meta.client
        try:
            client.head_bucket(Bucket=self.storage.bucket_name)
        except Exception:
            client.create_bucket(Bucket=self.storage.bucket_name)

    def upload_user_file(self, uploaded_file, bucket_name: str) -> str:
        self.ensure_bucket_exists(bucket_name)

        safe_name = uploaded_file.name.replace("/", "_")
        object_key = f"docs/{uuid4().hex}_{safe_name}"
        storage = self.get_storage(bucket_name)
        uploaded_file.seek(0)
        storage.save(object_key, uploaded_file)

        return object_key


    def get_file_stream(self, object_key: str):
        return self.storage.open(object_key, mode="rb")

    def file_exists(self, object_key: str) -> bool:
        return self.storage.exists(object_key)

    def save(self, payload) -> bool:
        doc_id = payload["doc_id"]
        doc = _get_doc_or_error(doc_id)

        bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
        is_present = self.file_exists(bucket_name, doc.file.name)
        return is_present