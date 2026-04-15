from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Document, DocumentText, DocumentTextChunk, DocumentChunkEmbedding
from .serializers import DocumentSerializer, DocumentTextSerializer, DocumentTextChunkSerializer, DocumentChunkEmbeddingSerializer
from .tasks import create_document_with_upload


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-id")
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get("file")
        if uploaded_file is None:
            raise ValidationError({"file": "This field is required."})

        create_document_with_upload(
            serializer=serializer,
            user=self.request.user,
            uploaded_file=uploaded_file,
        )

class DocumentTextViewSet(viewsets.ModelViewSet):
    queryset = DocumentText.objects.all().order_by("-id")
    serializer_class = DocumentTextSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        pass

class DocumentTextChunkViewSet(viewsets.ModelViewSet):
    queryset = DocumentTextChunk.objects.all().order_by("-id")
    serializer_class = DocumentTextChunkSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        pass

class DocumentChunkEmbeddingViewSet(viewsets.ModelViewSet):
    queryset = DocumentChunkEmbedding.objects.all().order_by("-id")
    serializer_class = DocumentChunkEmbeddingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        pass
