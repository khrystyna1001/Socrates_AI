from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
import os

from .routers import auth, bart, health
from .models.bart import BARTRAGSystem


logger = logging.getLogger(__name__)

# Setup lifespan to initialize RAG system once on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    pdf_path = os.getenv("PDF_PATH", "/app/sources")
    
    print("--- Initializing RAG System ---")
    rag_instance = BARTRAGSystem(pdf_path=pdf_path)
    
    chunks = rag_instance.get_documents()
    rag_instance.create_embeddings_and_vector_db(chunks=chunks)
    rag_instance.setup_rag_chain()
    
    app.state.rag_app = rag_instance
    print("--- RAG System Ready ---")
    
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(bart.router)

# CORS
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)