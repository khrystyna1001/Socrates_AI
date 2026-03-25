import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BARTModel
from .serializers import BARTSerializer
from .tasks import process_document_task


class BARTViewSet(viewsets.ModelViewSet):
    queryset = BARTModel.objects.all().order_by('-id')
    serializer_class = BARTSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        process_document_task.delay(instance.id)