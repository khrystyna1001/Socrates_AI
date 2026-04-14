from celery import shared_task

from services.models import PGVectorDB, MinioStorage

@shared_task()
def save_to_pgvector(payload):
    pgvector = PGVectorDB()
    embeddings = payload.get("vectors", [])
    pgvector.save(embeddings)

@shared_task()
def store_document_in_minio(document, uploaded_file=None, **kwargs):
    if uploaded_file is None:
        raise ValueError("uploaded_file is required for upload_document transition")

    storage = MinioStorage()
    bucket_name = document.minio_bucket
    object_key = storage.upload_user_file(uploaded_file, bucket_name)

    document.minio_bucket = bucket_name
    document.file = object_key
    document.save(update_fields=["minio_bucket", "file"])