from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from pypdf import PdfReader
from django.shortcuts import get_object_or_404


from .models import Document, DocumentChunk
from .minio_utils import file_exists, get_file_stream
from bart.models import EmbeddingModel, LLMModel, TextSplitter

logger = get_task_logger(__name__)

def _get_doc_or_error(doc_id):
    try:
        return get_object_or_404(Document, pk=doc_id)
    except Document.DoesNotExist:
        return None, {"status": "error", "doc_id": doc_id, "message": "Document not found"}


@shared_task()
def upload_pdf_document(doc_id):
    doc, error = _get_doc_or_error(doc_id)
    if error:
        return error
    return {"status": "ok", "doc_id": doc.id}


@shared_task()
def extract_pdf_text(payload):
    doc_id = payload["doc_id"]
    doc, error = _get_doc_or_error(doc_id)
    if error:
        return error

    bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
    stream = get_file_stream(bucket_name, doc.file.name)

    reader = PdfReader(stream)
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(pages).strip()

    return {"status": "ok", "doc_id": doc_id, "text": text}


@shared_task()
def split_pdf_into_chunks(payload):
    text = payload.get("text", "")
    chunks = TextSplitter().text_splitter.split_text(text) if text else []
    return {"status": "ok", "doc_id": payload["doc_id"], "chunks": chunks}


@shared_task()
def embed_chunks(payload):
    chunks = payload.get("chunks", [])
    embedding_model = EmbeddingModel().get_embedding_model()
    vectors = embedding_model.embed_documents(chunks) if chunks else []
    return {"status": "ok", "doc_id": payload["doc_id"], "chunks": chunks, "vectors": vectors}


@shared_task()
def save_to_postgres(payload):
    doc_id = payload["doc_id"]
    doc, error = _get_doc_or_error(doc_id)
    if error:
        return error

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

    return {"status": "ok", "doc_id": doc_id, "chunks": len(chunks)}


@shared_task(bind=True)
def save_to_minio(payload):
    doc_id = payload["doc_id"]
    doc, error = _get_doc_or_error(doc_id)
    if error:
        return error

    bucket_name = doc.minio_bucket or settings.MINIO_BUCKET
    is_present = file_exists(bucket_name, doc.file.name)
    if not is_present:
        return {"status": "error", "doc_id": doc_id, "message": "File not found in MinIO"}

    logger.info("Document %s processed and stored", doc_id)
    return {"status": "ok", "doc_id": doc_id, "file": doc.file.name, "bucket": bucket_name}
