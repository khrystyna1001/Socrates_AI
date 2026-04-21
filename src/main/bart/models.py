from django.db import models

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

class BARTQuery(models.Model):
    from documents.models import Document
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="queries",
        verbose_name="Query Model"
    )
    prompt = models.TextField(max_length=2000, verbose_name="Prompt")
    llm_response = models.TextField(blank=True, default="", verbose_name="Response")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Query {self.id} for document {self.document_id}"

    def set_llm_response(self, text: str):
        self.llm_response = text
        self.save(update_fields=["llm_response"])

class EmbeddingModel(models.Model):
    embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    
    def get_embedding_model(self):
        return self.embedding_model

class LLMModel(models.Model):
    llm = OllamaLLM(
            model="tinyllama:latest",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
            timeout=120
        )
    
    def get_llm(self):
        return self.llm
    
class TextSplitter(models.Model):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def get_text_splitter(self):
        return self.text_splitter
