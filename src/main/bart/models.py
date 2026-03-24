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
        loader = PyPDFLoader(self.document.path)
        raw_text = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(raw_text)
        
        for chunk in chunks:
            vector = embedding_engine.embed_query(chunk.page_content)
            DocumentChunk.objects.create(
                parent_doc=self,
                content=chunk.page_content,
                embedding_clip_vit_l_14=vector
            )

class DocumentChunk(models.Model):
    parent_doc = models.ForeignKey(BARTModel, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
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