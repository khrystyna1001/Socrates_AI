from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from pypdf import PdfReader
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse



from .models import Document, DocumentChunk, DocumentPages, DocumentText, DocumentTextChunk
from .minio_utils import file_exists, get_file_stream
from bart.models import EmbeddingModel, LLMModel, TextSplitter

logger = get_task_logger(__name__)

def _get_doc_or_error(doc_id):
    try:
        return get_object_or_404(Document, pk=doc_id)
    except ObjectDoesNotExist:
        return None, HttpResponse({"status": "error", "doc_id": doc_id, "message": "Document not found"})


@shared_task()
def upload_pdf_document(doc_id):
    try:
        doc, error = _get_doc_or_error(doc_id)
    except ObjectDoesNotExist:
        raise Http404("Document does not exist")


@shared_task()
def extract_pdf_text(payload):
    doc_id = payload["doc_id"]
    
    try:
        doc, error = _get_doc_or_error(doc_id)
    except ObjectDoesNotExist:
        raise Http404("Document does not exist")

    bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
    stream = get_file_stream(bucket_name, doc.file.name)

    pages = DocumentPages(stream).get_pages()
    text = DocumentText(stream).get_raw_text(pages)
    return text

@shared_task()
def split_pdf_into_chunks(payload):
    text = payload.get("text", "")
    chunks = TextSplitter().text_splitter.split_text(text) if text else []
    return chunks

@shared_task
def split_text_into_chunks(payload):
    text = payload.get("text", "")
    chunk_size = payload.get("chunk_size", 1000)
    
    text_chunk = DocumentTextChunk()
    text_chunk.chunks = []
    payload["chunks"] = text_chunk.split_raw_text_into_chunks(text, chunk_size) if text else []

    return payload

@shared_task()
def embed_chunks(payload):
    chunks = payload.get("chunks", [])
    embedding_model = EmbeddingModel().get_embedding_model()
    vectors = embedding_model.embed_documents(chunks) if chunks else []
    return vectors


@shared_task()
def save_to_postgres(payload):
    doc_id = payload["doc_id"]

    try:
        doc, error = _get_doc_or_error(doc_id)
    except ObjectDoesNotExist:
        raise Http404("Document does not exist")

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

@shared_task(bind=True)
def save_to_minio(payload):
    doc_id = payload["doc_id"]
    
    try:
        doc, error = _get_doc_or_error(doc_id)
    except ObjectDoesNotExist:
        raise Http404("Document does not exist")

    bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
    is_present = file_exists(bucket_name, doc.file.name)
    if not is_present:
        return HttpResponse({"status": "error", "doc_id": doc_id, "message": "File not found in MinIO"})

    logger.info("Document %s processed and stored", doc_id)
