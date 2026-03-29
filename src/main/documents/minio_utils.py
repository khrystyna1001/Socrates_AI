import re
from uuid import uuid4

from django.conf import settings
from django.utils.module_loading import import_string


_BUCKET_RE = re.compile(r"[^a-z0-9-]")


def _get_storage(bucket_name: str):
    storage_class = import_string(settings.PRIVATE_STORAGE_CLASS)
    storage = storage_class()
    storage.bucket_name = bucket_name
    return storage


def build_user_bucket_name(user_id: int) -> str:
    prefix = getattr(settings, "MINIO_USER_BUCKET_PREFIX", "user-files")
    raw = f"{prefix}-{user_id}".lower()
    bucket = _BUCKET_RE.sub("-", raw).strip("-")
    return bucket[:63] or f"user-{user_id}"


def ensure_bucket_exists(bucket_name: str) -> None:
    storage = _get_storage(bucket_name)
    client = storage.connection.meta.client
    try:
        client.head_bucket(Bucket=bucket_name)
    except Exception:
        client.create_bucket(Bucket=bucket_name)


def upload_user_file(uploaded_file, bucket_name: str) -> str:
    ensure_bucket_exists(bucket_name)

    safe_name = uploaded_file.name.replace("/", "_")
    object_key = f"docs/{uuid4().hex}_{safe_name}"
    storage = _get_storage(bucket_name)
    uploaded_file.seek(0)
    storage.save(object_key, uploaded_file)

    return object_key


def get_file_stream(bucket_name: str, object_key: str):
    storage = _get_storage(bucket_name)
    return storage.open(object_key, mode="rb")


def file_exists(bucket_name: str, object_key: str) -> bool:
    storage = _get_storage(bucket_name)
    return storage.exists(object_key)
