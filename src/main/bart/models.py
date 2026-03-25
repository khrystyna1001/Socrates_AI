import re
from django.db import models, migrations
from pgvector.django import VectorField, VectorExtension, HnswIndex, CosineDistance
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.llms import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings


# Create your models here.

class BARTModel(models.Model):
    document = models.FileField(upload_to="docs")

    def process_and_save_chunks(self, embedding_engine):
        llm = OllamaLLM(model="deepseek-r1:latest")
        loader = PyPDFLoader(self.document.path)
        raw_text = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(raw_text)
        
        for chunk in chunks:
            vector = embedding_engine.embed_query(chunk.page_content)

            prompt = f"Summarize the following document chunk in one sentence. Do not include introductory phrases:\n\n{chunk.page_content}"
            raw_response = llm.invoke(prompt)

            clean_summary = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()

            DocumentChunk.objects.create(
                parent_doc=self,
                content=chunk.page_content,
                embedding_clip_vit_l_14=vector,
                llm_summary=clean_summary
            )

class DocumentChunk(models.Model):
    parent_doc = models.ForeignKey(BARTModel, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    llm_summary = models.TextField(null=True, blank=True)
    embedding_clip_vit_l_14 = VectorField(dimensions=768, null=True, blank=True)

    class Meta:
        indexes = [
            HnswIndex(
                name="clip_l14_idx",
                fields=["embedding_clip_vit_l_14"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]