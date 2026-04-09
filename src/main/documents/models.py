from django.db import models
from django.conf import settings
from pgvector.django import HnswIndex, VectorField
from pypdf import PdfReader

# django lifecycle
# django logic

class Document(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    file = models.FileField("File", upload_to="docs")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    minio_bucket = models.CharField(max_length=63, default="docs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]


    def __str__(self):
        return self.title
    

class DocumentPages(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True,
    )
    
    def get_pages(self):
        self.document.file.open("rb")
        reader = PdfReader(self.document.file)
        return reader.pages


class DocumentText(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True,
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
        related_name="text_chunks",
        null=True,
        blank=True,
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
        related_name="chunks",
        null=True,
        blank=True,
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