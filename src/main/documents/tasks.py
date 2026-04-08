import logging
import re
from uuid import uuid4

from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.conf import settings
from django.utils.module_loading import import_string

from .models import Document, DocumentChunk, DocumentPages, DocumentText, DocumentTextChunk
from bart.models import EmbeddingModel, LLMModel, TextSplitter

_BUCKET_RE = re.compile(r"[^a-z0-9-]")

logger = get_task_logger(__name__)


def _get_doc_or_error(doc_id):
    try:
        return get_object_or_404(Document, pk=doc_id)
    except ObjectDoesNotExist as odne:
        logging.warning(odne)


def _get_storage(bucket_name: str):
    try:
        storage_class = import_string(settings.PRIVATE_STORAGE_CLASS)
        storage = storage_class()
        storage.bucket_name = bucket_name
        return storage
    except Exception as err:
        logging.warning(err)


def build_user_bucket_name(user_id: int) -> str:
    try:
        prefix = getattr(settings, "MINIO_USER_BUCKET_PREFIX", "user-files")
        raw = f"{prefix}-{user_id}".lower()
        bucket = _BUCKET_RE.sub("-", raw).strip("-")
        return bucket[:63] or f"user-{user_id}"
    except Exception as err:
        logging.warning(err)


def ensure_bucket_exists(bucket_name: str) -> None:
    try:
        storage = _get_storage(bucket_name)
        client = storage.connection.meta.client
        try:
            client.head_bucket(Bucket=bucket_name)
        except Exception:
            client.create_bucket(Bucket=bucket_name)
    except Exception as err:
        logging.warning(err)

def upload_user_file(uploaded_file, bucket_name: str) -> str:
    try:
        ensure_bucket_exists(bucket_name)

        safe_name = uploaded_file.name.replace("/", "_")
        object_key = f"docs/{uuid4().hex}_{safe_name}"
        storage = _get_storage(bucket_name)
        uploaded_file.seek(0)
        storage.save(object_key, uploaded_file)

        return object_key
    except Exception as err:
        logging.warning(err)


def get_file_stream(bucket_name: str, object_key: str):
    try:
        storage = _get_storage(bucket_name)
        return storage.open(object_key, mode="rb")
    except Exception as err:
        logging.warning(err)


def file_exists(bucket_name: str, object_key: str) -> bool:
    try:
        storage = _get_storage(bucket_name)
        return storage.exists(object_key)
    except Exception as err:
        logging.warning(err)

@shared_task()
def upload_pdf_document(doc_id):
    try:
        doc = _get_doc_or_error(doc_id)
    except ObjectDoesNotExist as odne:
        logging.warning(odne)


@shared_task()
def extract_pdf_text(payload):
    try:
        doc_id = payload["doc_id"]
        doc = _get_doc_or_error(doc_id)

        bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
        stream = get_file_stream(bucket_name, doc.file.name)

        pages = DocumentPages(stream).get_pages()
        text = DocumentText(stream).get_raw_text(pages)
        return text
    except Exception as err:
        logging.warning(err)

@shared_task()
def split_pdf_into_chunks(payload):
    try:
        text = payload.get("text", "")
        chunks = TextSplitter().text_splitter.split_text(text) if text else []
        return chunks
    except Exception as err:
        logging.warning(err)

@shared_task
def split_text_into_chunks(payload):
    try:
        text = payload.get("text", "")
        chunk_size = payload.get("chunk_size", 1000)
        
        text_chunk = DocumentTextChunk()
        text_chunk.chunks = []
        payload["chunks"] = text_chunk.split_raw_text_into_chunks(text, chunk_size) if text else []

        return payload
    except Exception as err:
        logging.warning(err)

@shared_task()
def embed_chunks(payload):
    try:
        chunks = payload.get("chunks", [])
        embedding_model = EmbeddingModel().get_embedding_model()
        vectors = embedding_model.embed_documents(chunks) if chunks else []
        return vectors
    except Exception as err:
        logging.warning(err)

@shared_task()
def save_to_postgres(payload):
    try:
        doc_id = payload["doc_id"]

        doc = _get_doc_or_error(doc_id)

        chunks = payload.get("chunks", [])
        vectors = payload.get("vectors", [])

        with transaction.atomic():
            DocumentChunk.objects.filter(document=doc).delete()
            DocumentChunk.objects.bulk_create(
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

@shared_task()
def save_to_minio(payload):
    try:
        doc_id = payload["doc_id"]
        doc = _get_doc_or_error(doc_id)

        bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
        is_present = file_exists(bucket_name, doc.file.name)
        if not is_present:
            return JsonResponse({"status": "error", "doc_id": doc_id, "message": "File not found in MinIO"})
        
    except Exception as err:
        logging.warning(err)