from fastapi import APIRouter, Request, HTTPException
from ..models.query import QueryRequest

router = APIRouter()

@router.post("/query")
async def query_system(request: QueryRequest, raw_request: Request):
    rag_app = getattr(raw_request.app.state, "rag_app", None)
    
    if not rag_app:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    answer, sources, updated_history = rag_app.process_query(
        query=request.question, 
        chat_history=request.chat_history
    )
    
    return {
        "answer": answer, 
        "sources": sources,
        "chat_history": updated_history
    }