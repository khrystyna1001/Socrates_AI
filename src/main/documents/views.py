from rest_framework import viewsets

from .models import Document
from .serializers import DocumentSerializer
from .tasks import process_document_task


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-id")
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        instance = serializer.save(status="pending")
        process_document_task.delay(instance.id)