from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from .models import Document, DocumentChunk

logger = get_task_logger(__name__)
_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    return _embedding_model


def extract_pdf_text(file_field) -> str:
    with file_field.open("rb") as f:
        reader = PdfReader(f)
        pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages).strip()


@shared_task(bind=True)
def process_document_task(self, doc_id, chunk_size=1000, chunk_overlap=200):
    try:
        doc = Document.objects.get(pk=doc_id)
    except Document.DoesNotExist:
        return {"status": "error", "doc_id": doc_id, "message": "Document not found"}

    try:
        doc.mark_processing()

        text = extract_pdf_text(doc.file)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = splitter.split_text(text)

        embedding_model = get_embedding_model()
        vectors = embedding_model.embed_documents(chunks) if chunks else []

        with transaction.atomic():
            DocumentChunk.objects.filter(document=doc).delete()
            DocumentChunk.objects.bulk_create(
                [
                    DocumentChunk(
                        document=doc,
                        chunk_index=i,
                        content=chunk,
                        embedding=vectors[i],
                    )
                    for i, chunk in enumerate(chunks)
                ]
            )

        doc.mark_ready()
        logger.info("Processed doc_id=%s, chunks=%s", doc_id, len(chunks))
        return {"status": "ok", "doc_id": doc_id, "chunks": len(chunks)}

    except Exception as exc:
        doc.mark_failed()
        logger.exception("Failed doc_id=%s", doc_id)
        return {"status": "error", "doc_id": doc_id, "message": str(exc)}
