from celery import shared_task, chain
from django.db import transaction

from services.models import MinioStorage, PGVectorDB

def create_document_with_upload(serializer, user, uploaded_file):
    storage = MinioStorage()
    user_bucket = storage.build_user_bucket_name(user.id)
    
    object_key = storage.upload_user_file(uploaded_file, user_bucket)
    
    instance = serializer.save(
        owner=user,
        minio_bucket=user_bucket,
        file=object_key,
        process_state="upload_document" 
    )
    
    transaction.on_commit(lambda: process_document_pipeline.delay(instance.id))
    
    return instance

@shared_task
def extract_raw_text_from_pdf(document_id):
    from .models import Document, DocumentPages, DocumentText
    document = Document.objects.get(pk=document_id)
    
    pages = document.get_pages() 
    DocumentPages.objects.update_or_create(
        document=document,
        defaults={'pages': len(pages)},
    )
    
    text_val = document.get_raw_text(pages)
    doc_text, _ = DocumentText.objects.update_or_create(
        document=document,
        defaults={'text': text_val},
    )
    return document_id


@shared_task
def split_raw_text_into_chunks(document_id):
    from .models import Document, DocumentText, DocumentTextChunk
    from bart.models import TextSplitter
    
    if isinstance(document_id, Document):
        document = document_id
    else:
        document = Document.objects.get(pk=document_id)
    
    document_text = DocumentText.objects.get(document=document)

    text_splitter = TextSplitter().get_text_splitter()
    chunks = text_splitter.split_text(document_text.text)

    document_text.text_chunks.all().delete()

    from django.db import transaction
    with transaction.atomic():
        DocumentTextChunk.objects.filter(document=document_text).delete()
        
        objs = [
            DocumentTextChunk(
                document=document_text,
                chunk_index=i,
                content=chunk
            ) for i, chunk in enumerate(chunks)
        ]
        DocumentTextChunk.objects.bulk_create(objs)

    return document_id


@shared_task
def embed_document_chunks(document_or_id):
    from .models import Document, DocumentChunkEmbedding, DocumentText, DocumentTextChunk

    if isinstance(document_or_id, Document):
        document = document_or_id
    else:
        document = Document.objects.get(pk=document_or_id)
    
    
    document_text = DocumentText.objects.get(document=document)
    text_chunks = list(DocumentTextChunk.objects.filter(
        document=document_text
    ).values_list('content', flat=True))

    if not text_chunks:
        document.chunks.all().delete()
        return []

    from bart.models import EmbeddingModel
    embedding_model = EmbeddingModel().get_embedding_model()
    vectors = embedding_model.embed_documents(text_chunks)

    document.chunks.all().delete()

    for index, vector in enumerate(vectors):
        DocumentChunkEmbedding.objects.update_or_create(
            document=document,
            chunk_index=index,
            defaults={'embedding': vector},
        )
    return vectors

@shared_task
def save_to_pgvector(document_or_id):
    from .models import Document, DocumentChunkEmbedding
    
    if isinstance(document_or_id, Document):
        document = document_or_id
    else:
        document = Document.objects.get(pk=document_or_id)
    
    pgvector = PGVectorDB()
    embeddings = DocumentChunkEmbedding.objects.filter(document=document)
    pgvector.save(embeddings)


@shared_task
def store_document_in_minio(document_or_id, uploaded_file=None, **kwargs):
    from .models import Document
    
    if isinstance(document_or_id, Document):
        document = document_or_id
    else:
        document = Document.objects.get(pk=document_or_id)
    
    if uploaded_file is None:
        raise ValueError("uploaded_file is required for upload_document transition")

    storage = MinioStorage()
    bucket_name = document.minio_bucket
    object_key = storage.upload_user_file(uploaded_file, bucket_name)

    document.minio_bucket = bucket_name
    document.file = object_key
    document.save(update_fields=["minio_bucket", "file"])

@shared_task()
def process_document_pipeline(document_id):

    pipeline = chain(
        extract_raw_text_from_pdf.s(document_id),
        split_raw_text_into_chunks.s(),
        embed_document_chunks.si(document_id),
        save_to_pgvector.si(document_id),
    )
    
    pipeline.apply_async()