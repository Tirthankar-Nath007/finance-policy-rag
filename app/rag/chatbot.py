import httpx
from typing import List, Tuple

from app.rag.faiss_store import faiss_store
from app.config import settings


OUT_OF_SCOPE_MESSAGE = "I don't have information about that in the provided documents. Please ask questions related to the policy documents."


def get_azure_chat_response(prompt: str) -> str:
    client = httpx.Client(verify=False, timeout=120.0)
    
    url = f"{settings.azure_openai_endpoint}/openai/deployments/gpt-5-nano/chat/completions?api-version=2025-01-01-preview"
    
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that only answers questions using the provided context. If the answer is not in the context, say you don't have that information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    headers = {
        "api-key": settings.azure_openai_api_key,
        "Content-Type": "application/json"
    }
    
    response = client.post(url, json=data, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    return content


def build_prompt(query: str, context_chunks: List[str], sources: List[str]) -> str:
    context = "\n\n---\n\n".join([
        f"[Source: {src}]\n{chunk}"
        for chunk, src in zip(context_chunks, sources)
    ])
    
    prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context from policy documents.

    INSTRUCTIONS:
    1. Only answer questions using the provided context below
    2. If the answer is not found in the context, respond with: "{OUT_OF_SCOPE_MESSAGE}"
    3. Do NOT make up or hallucinate any information
    4. Cite the source document(s) when providing answers
    5. Keep your answers concise and relevant

    CONTEXT:
    {context}

    QUESTION: {query}

    ANSWER:"""
    return prompt


def chat(query: str) -> Tuple[str, List[str]]:
    context_chunks, sources, scores = faiss_store.search(
        query,
        top_k=settings.top_k
    )
    
    if not context_chunks:
        return OUT_OF_SCOPE_MESSAGE, []
    
    prompt = build_prompt(query, context_chunks, sources)
    answer = get_azure_chat_response(prompt)
    
    unique_sources = list(dict.fromkeys(sources))
    
    return answer, unique_sources


def reload_index() -> dict:
    faiss_store.build_index()
    return {
        "status": "success",
        "message": f"Index built with {len(faiss_store.chunks)} chunks from {len(set(faiss_store.sources))} documents"
    }
