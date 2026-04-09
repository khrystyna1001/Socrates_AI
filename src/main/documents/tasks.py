import logging

from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from .models import Document, DocumentPages, DocumentText, DocumentTextChunk
from bart.models import EmbeddingModel, TextSplitter

logger = get_task_logger(__name__)

def _get_doc_or_error(doc_id):
    try:
        return get_object_or_404(Document, pk=doc_id)
    except ObjectDoesNotExist as odne:
        logging.warning(odne)

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