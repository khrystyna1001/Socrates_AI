from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documents.models import Document, DocumentChunkEmbedding, DocumentTextChunk


class FakeEmbeddingBackend:
    def embed_documents(self, chunk_texts):
        return [[float(index + 1)] * 768 for index, _ in enumerate(chunk_texts)]


class DocumentEmbeddingTests(TestCase):
    def test_generate_embeddings_uses_document_text(self):
        user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="password123",
        )
        with self.captureOnCommitCallbacks(execute=True):
            document = Document.objects.create(
                title="Embedding Test",
                owner=user,
                file=SimpleUploadedFile("test.pdf", b"%PDF-1.4\n%"),
            )
        document_text = document.documenttext
        document_text.text = "First chunk. " * 120
        document_text.save(update_fields=["text"])

        with patch(
            "bart.models.EmbeddingModel.get_embedding_model",
            return_value=FakeEmbeddingBackend(),
        ):
            embeddings = document_text.generate_embeddings()

        self.assertGreater(len(embeddings), 0)
        self.assertEqual(
            document_text.text_chunks.count(),
            DocumentChunkEmbedding.objects.filter(document=document).count(),
        )
        self.assertEqual(
            DocumentTextChunk.objects.filter(document=document_text).first().chunk_index,
            0,
        )
