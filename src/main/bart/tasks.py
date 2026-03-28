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
        _llm = OllamaLLM(model="deepseek-r1:latest")
    return _llm


@shared_task(bind=True)
def generate_bart_response_task(self, query_id, top_k=5):
    try:
        query = BARTQuery.objects.select_related("document").get(pk=query_id)
    except BARTQuery.DoesNotExist:
        return {"status": "error", "query_id": query_id, "message": "Query not found"}

    try:
        embedding_model = get_embedding_model()
        q_vec = embedding_model.embed_query(query.prompt)

        chunks_qs = (
            DocumentChunk.objects
            .filter(document=query.document, embedding__isnull=False)
            .annotate(distance=CosineDistance("embedding", q_vec))
            .order_by("distance")[:top_k]
        )
        context = "\n\n".join(chunk.content for chunk in chunks_qs)

        llm = get_llm()
        final_prompt = (
            "Answer using the context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{query.prompt}\n"
        )
        answer = str(llm.invoke(final_prompt))
        query.set_response(answer)

        return {"status": "ok", "query_id": query_id}

    except Exception as exc:
        logger.exception("Failed query_id=%s", query_id)
        return {"status": "error", "query_id": query_id, "message": str(exc)}
