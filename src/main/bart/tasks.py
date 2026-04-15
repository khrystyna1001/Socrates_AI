import os

from celery import shared_task
from celery.utils.log import get_task_logger
from pgvector.django import CosineDistance

from .models import LLMModel, EmbeddingModel
from documents.models import DocumentChunkEmbedding

logger = get_task_logger(__name__)

def embed_user_prompt(query):
    embedding_model = EmbeddingModel().get_embedding_model()
    q_vec = embedding_model.embed_query(query.prompt)
    return q_vec

def read_user_prompt(query, q_vec, top_k=5):
    chunks_qs = (
        DocumentChunkEmbedding.objects
        .filter(document=query.document, embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", q_vec))
        .order_by("distance")[:top_k]
    )
    context = "\n\n".join(chunk.chunk.content for chunk in chunks_qs)
    return context

def invoke_bart_response(query, context):
    llm = LLMModel().get_llm()
    final_prompt = (
        "Answer using the context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query.prompt}\n"
    )
    answer = str(llm.invoke(final_prompt))
    query.set_llm_response(answer)

    return answer

