from bart import BARTRAGSystem
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.query import QueryRequest
import uvicorn

app = FastAPI()

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

@app.get("/")
async def read_root():
    return {"message": "BART RAG System API"}

@app.post("/query")
async def query_system(request: QueryRequest):
    bart_rag_system = BARTRAGSystem(pdf_path="/Users/khrystynka/Desktop/uni/programming 4/sources")
    chunks = bart_rag_system.get_documents()
    bart_rag_system.create_embeddings_and_vector_db(chunks=chunks)
    bart_rag_system.setup_rag_chain()
    
    answer, relevant_docs = bart_rag_system.process_query(request.question)
    return {"answer": answer, "sources": [doc.page_content for doc in relevant_docs]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)