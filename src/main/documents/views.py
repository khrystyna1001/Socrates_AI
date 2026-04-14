from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Document
from .serializers import DocumentSerializer

from services.models import MinioStorage


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

        user_bucket = MinioStorage().build_user_bucket_name(self.request.user.id)

        instance = serializer.save(
            owner=self.request.user,
            minio_bucket=user_bucket,
            file="",
        )
        instance.document_logic.upload_document(
            uploaded_file=uploaded_file,
            user=self.request.user,
        )
