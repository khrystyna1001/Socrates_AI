# bart/tasks.py
import requests
from celery import shared_task
from django.conf import settings
from .models import Book
from langchain_community.embeddings import HuggingFaceEmbeddings


@shared_task
def generate_huggingface_embedding(book_data):
    model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    content_to_embed = book_data.get('title', 'Untitled')
    
    vector = model.embed_query(content_to_embed)
    
    book_data['embedding'] = vector
    save_to_postgres.delay(book_data)
    
    return f"Vector generated for Book {book_data.get('id')}"

@shared_task(bind=True, max_retries=5)
def save_to_postgres(self, book_data):
    try:
        book, created = Book.objects.get_or_create(
            defaults={
                'content': book_data.get('title', 'Untitled'),
                'page_number': book_data.get('page_number', 0),
                'embedding': book_data.get('embedding')
            }
        )
        return f"Postgres: Saved Book {book.id}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)