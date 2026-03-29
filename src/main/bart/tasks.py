import os

from celery import shared_task
from celery.utils.log import get_task_logger
from pgvector.django import CosineDistance
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama.llms import OllamaLLM

from .models import BARTQuery
from documents.models import DocumentChunk

logger = get_task_logger(__name__)
_embedding_model = None
_llm = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    return _embedding_model


def get_llm():
    global _llm
    if _llm is None:
        _llm = OllamaLLM(
            model="deepseek-r1:latest",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        )
    return _llm

def embed_user_prompt(query):
    embedding_model = get_embedding_model()
    q_vec = embedding_model.embed_query(query.prompt)
    return q_vec

def read_user_prompt(query, q_vec, top_k=5):
    chunks_qs = (
        DocumentChunk.objects
        .filter(document=query.document, embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", q_vec))
        .order_by("distance")[:top_k]
    )
    context = "\n\n".join(chunk.content for chunk in chunks_qs)
    return context

def invoke_bart_response(query, context):
    llm = get_llm()
    final_prompt = (
        "Answer using the context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query.prompt}\n"
    )
    answer = str(llm.invoke(final_prompt))
    query.set_response(answer)

    return answer

