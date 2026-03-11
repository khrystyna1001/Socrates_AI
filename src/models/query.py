from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    chat_history: list = []
