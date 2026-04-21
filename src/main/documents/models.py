from django.db import models
from django.conf import settings
from pgvector.django import HnswIndex, VectorField
from pypdf import PdfReader

from django_logic import Process as BaseProcess, ProcessManager, Transition, Action
from .tasks import extract_raw_text_from_pdf, split_raw_text_into_chunks, embed_document_chunks, save_to_pgvector, store_document_in_minio


MY_STATE_CHOICES = (
    ("get_document", "Get Document"),
    ("upload_document", "Upload Document"),
    ("extract_pdf_text", "Extract PDF Text"),
    ("split_text_into_chunks", "Split Text Into Chunks"),
    ("embed_chunks", "Embed Chunks"),
    ("save_to_pgvector", "Save to PGVector"),
    ("save_to_minio", "Save to MinIO"),
)

class DocumentLogic(BaseProcess):
    process_name = "document_logic"
    states = MY_STATE_CHOICES
    transitions = [
        Transition(
            action_name="upload_document",
            sources=["get_document"],
            target="upload_document",
            side_effects=[store_document_in_minio],
        ),
        Transition(
            action_name="extract_pdf_text",
            sources=["upload_document"],
            target="extract_pdf_text",
            side_effects=[extract_raw_text_from_pdf],
        ),
        Transition(
            action_name="split_text_into_chunks",
            sources=["extract_pdf_text"],
            target="split_text_into_chunks",
            side_effects=[split_raw_text_into_chunks],
        ),
        Transition(
            action_name="embed_chunks",
            sources=["split_text_into_chunks"],
            target="embed_chunks",
            side_effects=[embed_document_chunks],
        ),
        Action(action_name="save_to_pgvector", sources=["embed_chunks"], side_effects=[save_to_pgvector]),
        Action(action_name="save_to_minio", sources=["upload_document"]),
    ]


class Document(models.Model):
    title = models.CharField(max_length=500, unique=True, verbose_name="Title")
    file = models.FileField("File", upload_to="docs", max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    minio_bucket = models.CharField(max_length=63, default="docs", verbose_name="User's MinIO Bucket Name")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Document Owner"
    )
    
    process_state = models.CharField(
        max_length=32,
        choices=MY_STATE_CHOICES,
        default="get_document",
        verbose_name="Document Processing State",
    )

    def __str__(self):
        return self.title
    
    def get_raw_text(self, pages):
        text = ""
        for page in pages:
            text += page.extract_text() + "\n"
        return text
    
    def get_pages(self):
        from services.models import MinioStorage
        storage = MinioStorage()
    
        f = storage.get_file_stream(self.minio_bucket, self.file.name)
        
        import io
        stream = io.BytesIO(f.read())
        f.close()
        
        reader = PdfReader(stream)
        return reader.pages
    

class DocumentPages(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Document Pages"
    )
    
    pages = models.PositiveIntegerField(verbose_name="Number of Pages")

    def __str__(self):
        return str(self.pages)


class DocumentText(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Document Text"
    )
    text = models.TextField(verbose_name="Document Text")

    def __str__(self):
        return self.text[:60] if self.text else ""

class DocumentTextChunk(models.Model):
    document = models.ForeignKey(
        DocumentText,
        on_delete=models.CASCADE,
        related_name="text_chunks",
        verbose_name="Document Text Chunk",
    )
    content = models.TextField(default="", blank=True, verbose_name="Chunk Content")
    chunk_index = models.PositiveIntegerField(verbose_name="Chunk Index")

    def __str__(self):
        return self.content[:65] if self.content else ""


class DocumentChunkEmbedding(models.Model):
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
        verbose_name="Document Chunk Embedding",
    )

    chunk_index = models.PositiveIntegerField(verbose_name="Chunk Index")
    embedding = VectorField(dimensions=768, null=True, blank=True, verbose_name="Chunk Embedding")

    class Meta:
        ordering = ["document_id", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="uniq_document_chunk_index",
            )
        ]
        indexes = [
            HnswIndex(
                name="doc_chunk_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]

    def __str__(self):
        return f"Document {self.document_id} chunk {self.chunk_index}"


ProcessManager.bind_model_process(Document, DocumentLogic, state_field="process_state")