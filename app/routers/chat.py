from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.chatbot import chat, reload_index, OUT_OF_SCOPE_MESSAGE
from app.rag.faiss_store import faiss_store


router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    out_of_scope: bool


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, message="Message cannot be empty")
    
    try:
        answer, sources = chat(request.message)
        out_of_scope = answer == OUT_OF_SCOPE_MESSAGE
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            out_of_scope=out_of_scope
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_endpoint():
    try:
        result = reload_index()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_endpoint():
    index_loaded = faiss_store.vectors is not None
    
    return {
        "status": "healthy",
        "index_loaded": index_loaded,
        "chunks_count": len(faiss_store.chunks) if faiss_store.chunks else 0
    }
