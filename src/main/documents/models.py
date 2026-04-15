from django.db import models, transaction
from django.conf import settings
from pgvector.django import HnswIndex, VectorField
from pypdf import PdfReader

from django_logic import Process as BaseProcess, ProcessManager, Transition, Action
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook
from .tasks import extract_raw_text_from_pdf, split_raw_text_into_chunks, embed_document_chunks, save_to_pgvector, store_document_in_minio, process_document_pipeline


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


class Document(LifecycleModel):
    title = models.CharField(max_length=255, unique=True)
    file = models.FileField("File", upload_to="docs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    minio_bucket = models.CharField(max_length=63, default="docs")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    
    process_state = models.CharField(
        max_length=32,
        choices=MY_STATE_CHOICES,
        default="get_document",
    )

    @hook(AFTER_CREATE)
    def initialize_related_models(self):
        def create_related_models():
            process_document_pipeline.delay(self.pk)

        transaction.on_commit(create_related_models)

    def __str__(self):
        return self.title
    
    def get_raw_text(self, pages):
        for page in pages:
            self.text += page.extract_text() + "\n"
        return self.text
    
    def get_pages(self):
        self.document.file.open("rb")
        reader = PdfReader(self.document.file)
        return reader.pages
    

class DocumentPages(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
    )
    
    pages = models.PositiveIntegerField()

    def __str__(self):
        return self.pages


class DocumentText(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
    )
    text = models.TextField()

    def __str__(self):
        return self.text[:60] if self.text else ""

class DocumentTextChunk(models.Model):
    document = models.ForeignKey(
        DocumentText,
        on_delete=models.CASCADE,
        related_name="text_chunks"
    )
    content = models.TextField(default="", blank=True)
    chunk_index = models.PositiveIntegerField()

    def __str__(self):
        return self.content[:65] if self.content else ""


class DocumentChunkEmbedding(models.Model):
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks"
    )

    chunk_index = models.PositiveIntegerField()
    embedding = VectorField(dimensions=768, null=True, blank=True)

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