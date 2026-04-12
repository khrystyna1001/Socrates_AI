from django.db import models, transaction
from django.conf import settings
from pgvector.django import HnswIndex, VectorField
from pypdf import PdfReader

from django_logic import Process as BaseProcess, Transition, Action
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook


# MY_STATE_CHOICES = (
#      ('draft', 'Draft'),
#      ('approved', 'Approved'),
#      ('paid', 'Paid'),
#      ('void', 'Void'),
#  )

# def update_data(*args, **kwargs):
#     return None

# class DocumentLogic(BaseProcess):
#     states = MY_STATE_CHOICES
#     transitions = [
#         Transition(action_name='approve', sources=['draft'], target='approved'),
#         Transition(action_name='pay', sources=['approve'], target='paid'),
#         Transition(action_name='void', sources=['draft', 'approved'], target='void'),
#         Action(action_name='update', side_effects=[update_data]),
#     ]

class Document(LifecycleModel):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    file = models.FileField("File", upload_to="docs")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    minio_bucket = models.CharField(max_length=63, default="docs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    @hook(AFTER_CREATE)
    def initialize_related_models(self):
        def create_related_models():
            DocumentPages.objects.get_or_create(document=self)
            document_text, _ = DocumentText.objects.get_or_create(document=self)
            DocumentTextChunk.objects.get_or_create(document=document_text)
            DocumentChunk.objects.get_or_create(
                document=self,
                chunk_index=0,
                defaults={"embedding": None},
            )

        transaction.on_commit(create_related_models)

    def __str__(self):
        return self.title
    

class DocumentPages(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=False
    )
    
    def get_pages(self):
        self.document.file.open("rb")
        reader = PdfReader(self.document.file)
        return reader.pages


class DocumentText(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=False
    )
    text = models.TextField(default="")

    def get_raw_text(self, pages):
        for page in pages:
            self.text += page.extract_text() + "\n"
        return self.text


class DocumentTextChunk(models.Model):
    document = models.ForeignKey(
        DocumentText,
        on_delete=models.CASCADE,
        related_name="text_chunks"
    )
    chunks = []

    def split_raw_text_into_chunks(self, text, chunk_size):
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            self.chunks.append(chunk)
        return self.chunks


class DocumentChunk(models.Model):
    
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
