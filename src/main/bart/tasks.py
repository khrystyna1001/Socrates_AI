# bart/tasks.py
from celery import shared_task
from .models import BARTModel
from langchain_huggingface import HuggingFaceEmbeddings

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    return _embedding_model

@shared_task
def process_document_task(doc_id):
    try:
        instance = BARTModel.objects.get(id=doc_id)
        
        embedding_model = get_embedding_model()
        instance.process_and_save_chunks(embedding_model)
        
        return f"Document {doc_id} processed successfully."
    except BARTModel.DoesNotExist:
        return f"Error: Document {doc_id} not found."
    except Exception as e:
        print(f"FAILED TO PROCESS: {str(e)}")
        return f"Error: {str(e)}"