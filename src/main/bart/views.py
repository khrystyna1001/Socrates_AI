import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BARTModel
from .serializers import BARTSerializer

from .s3_client import get_s3_client

class BARTViewSet(viewsets.ModelViewSet):
    queryset = BARTModel.objects.all().order_by('-id')
    serializer_class = BARTSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        
        s3 = get_s3_client()
        bucket = os.getenv('AWS_STORAGE_BUCKET_NAME', 'docs')
        
        file_obj = instance.document
        s3.upload_fileobj(file_obj, bucket, instance.document.name)

        from .tasks import process_document_task
        process_document_task.delay(instance.id)