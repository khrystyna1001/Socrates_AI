# bart/tasks.py
import requests
from celery import shared_task
from django.conf import settings
from .models import BARTModel


@shared_task
def process_document_task(doc_id):
    try:
        instance = BARTModel.objects.get(id=doc_id)
        embedding_model = BARTModel.embeddings_model
        instance.process_and_save_chunks(embedding_model)
        
        return f"Document {doc_id} processed successfully."
    except Exception as e:
        return f"Error: {str(e)}"