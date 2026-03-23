from django.db import models, migrations
from pgvector.django import VectorField, VectorExtension, HnswIndex, CosineDistance
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.llms import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings


# Create your models here.


class Migration(migrations.Migration):
    operations = [
        VectorExtension()
    ]

class BARTModel(models.Model):
    document = models.FileField(upload_to="docs")
    
    llm = OllamaLLM(model="deepseek-r1:latest")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    embeddings_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")

    def process_and_save_chunks(self, embedding_model):
        raw_text = self.load_pdf_document()        
        chunks = self.split_document_to_chunks(raw_text)
        
        for chunk_text in chunks:
            vector = embedding_model.embed_query(chunk_text.page_content)
            
            DocumentChunk.objects.create(
                parent_doc=self,
                content=chunk_text.page_content,
                embedding_clip_vit_l_14=vector
            )

    def load_pdf_document(self):
        loader = PyPDFLoader(self.document.path)
        return loader.load()
    
    def split_document_to_chunks(self, text):
        return self.text_splitter.split_documents(text)

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