from celery import shared_task

from services.models import MinioStorage, PGVectorDB

def create_document_with_upload(serializer, user, uploaded_file):
    user_bucket = MinioStorage().build_user_bucket_name(user.id)
    instance = serializer.save(
        owner=user,
        minio_bucket=user_bucket,
        file="",
    )
    instance.document_logic.upload_document(
        uploaded_file=uploaded_file,
        user=user,
    )
    return instance


@shared_task
def extract_raw_text_from_pdf(document_id):
    from .models import Document, DocumentPages, DocumentText
    document = Document.objects.get(pk=document_id)
    document.document_logic.extract_pdf_text()

    pages = document.get_pages()
    DocumentPages.objects.update_or_create(
        document=document,
        pages=document.get_pages,
    )
    document_text, _ = DocumentText.objects.update_or_create(
        document=document,
        text=document.get_raw_text,
    )
    return document_text


@shared_task
def split_raw_text_into_chunks(document_id, document_text_id):
    from .models import Document, DocumentText, DocumentTextChunk
    document = Document.objects.get(pk=document_id)
    document_text = DocumentText.objects.get(pk=document_text_id)
    document.document_logic.split_text_into_chunks()

    from bart.models import TextSplitter
    text_splitter = TextSplitter().get_text_splitter()
    chunks = text_splitter.split_text(document_text.text)

    document_text.chunks.all().delete()

    for index, chunk_text in enumerate(chunks):
        DocumentTextChunk.objects.update_or_create(
            document=document_text,
            chunk_index=index,
            content=chunk_text,
        )


def embed_document_chunks(document, chunks):

    document.document_logic.embed_chunks()

    if not chunks:
        document.chunks.all().delete()
        return []

    from bart.models import EmbeddingModel
    embedding_model = EmbeddingModel().get_embedding_model()
    vectors = embedding_model.embed_documents(chunks)

    document.chunks.all().delete()

    from .models import DocumentChunkEmbedding
    for index, vector in enumerate(vectors):
        DocumentChunkEmbedding.objects.update_or_create(
            document=document,
            chunk_index=index,
            embedding=vector,
        )
    return vectors

@shared_task
def save_to_pgvector(document_id):
    from .models import Document, DocumentChunkEmbedding
    document = Document.objects.get(pk=document_id)
    document.document_logic.save_to_pgvector()
    
    pgvector = PGVectorDB()
    embeddings = DocumentChunkEmbedding.objects.filter(document=document)
    pgvector.save(embeddings)


@shared_task
def store_document_in_minio(document_id, uploaded_file=None, **kwargs):
    from .models import Document
    document = Document.objects.get(pk=document_id)
    
    if uploaded_file is None:
        raise ValueError("uploaded_file is required for upload_document transition")

    storage = MinioStorage()
    bucket_name = document.minio_bucket
    object_key = storage.upload_user_file(uploaded_file, bucket_name)

    document.minio_bucket = bucket_name
    document.file = object_key
    document.save(update_fields=["minio_bucket", "file"])

@shared_task
def process_document_pipeline(document_id):
    document_text = extract_raw_text_from_pdf(document_id)
    split_raw_text_into_chunks(document_id, document_text.pk)
    embed_document_chunks(document_id)
    save_to_pgvector(document_id)
    
    return document_id