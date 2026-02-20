from fastapi import FastAPI
from app.routers import chat
from app.rag.faiss_store import faiss_store

app = FastAPI(
    title="Finance Policy RAG Chatbot",
    description="A RAG-based chatbot that answers questions from finance policy documents",
    version="1.0.0"
)

app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.on_event("startup")
async def startup_event():
    if faiss_store.load_index():
        print(f"Loaded existing index with {len(faiss_store.chunks)} chunks")
    else:
        print("No existing index found. Use /api/reload to build the index from PDFs.")
