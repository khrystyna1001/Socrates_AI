from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from celery import chain

from .models import Document
from .serializers import DocumentSerializer
from .tasks import upload_pdf_document, extract_pdf_text, split_pdf_into_chunks, embed_chunks, save_to_pgvector, save_to_minio

from services.models import MinioStorage


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-id")
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        mystorage = MinioStorage()
        uploaded_file = self.request.FILES.get("file")
        if uploaded_file is None:
            raise ValidationError({"file": "This field is required."})

        user_bucket = mystorage.build_user_bucket_name(self.request.user.id)
        object_key = mystorage.upload_user_file(uploaded_file, user_bucket)

        instance = serializer.save(
            owner=self.request.user,
            minio_bucket=user_bucket,
            file=object_key,
        )

        #replace with a logic model
        chain(
            upload_pdf_document.s(instance.id),
            extract_pdf_text.s(),
            split_pdf_into_chunks.s(),
            embed_chunks.s(),
            save_to_pgvector.s(),
            save_to_minio.s(),
        ).delay()
