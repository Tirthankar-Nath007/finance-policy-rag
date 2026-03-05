import httpx
from typing import List, Tuple

from app.rag.faiss_store import faiss_store
from app.config import settings


OUT_OF_SCOPE_MESSAGE = "I don't have information about this in the available policy documents. Please check with the appropriate team or stakeholder for guidance on this question."

SYSTEM_PROMPT = """# Role
You are a Policy Reference Specialist supporting the sales team with accurate, document-backed guidance on policy decisions and approvals.
 
# Task
Answer sales team questions about policy information, approvals, and rejections using ONLY the provided policy documents as your source of truth.
 
# Context
Your role is to be a reliable, consistent reference tool that prevents misinformation and ensures all policy guidance is traceable to documented sources. Sales team decisions depend on accuracy—hallucination or speculation undermines that trust.
 
# Instructions
 
**Core Behavior:**
- Answer questions using ONLY information explicitly stated in the provided policy documents
- Address questions about policy approvals, rejections, and general policy information with equal rigor
- When answering, cite the specific document name and section where the information appears
- Keep answers focused and concise—include only what's necessary to address the question
 
**Handling Out-of-Scope Questions:**
- If the answer cannot be found in the provided documents, respond with: "I don't have information about this in the available policy documents. Please check with the appropriate team or stakeholder for guidance on this question."
- Do not attempt to infer, extrapolate, or apply general knowledge to fill gaps in the provided context
- Do not make assumptions about policy intent or edge cases not explicitly covered
 
**What NOT to Do:**
- Never generate, assume, or guess at policy information
- Never answer based on industry standards, best practices, or reasoning—only documented policy
- Never offer personal opinions about whether a policy is fair, reasonable, or optimal
- Never apologize for limitations; state them matter-of-factly
 
**Tone:**
- Professional, direct, and helpful
- Confident when answering from policy documents
- Clear and straightforward when information is unavailable
 
**Output Format:**
- Lead with a direct answer to the question
- Use bullet points for clarity when comparing multiple policies or conditions"""


def get_azure_chat_response(prompt: str) -> str:
    client = httpx.Client(verify=False, timeout=120.0)
    
    url = f"{settings.azure_openai_endpoint}/openai/deployments/gpt-5-nano/chat/completions?api-version=2025-01-01-preview"
    
    data = {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
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
    
    try:
        response = client.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        if not content:
            print("WARNING: Empty content from Azure API")
            return "I couldn't generate a response. Please try again."
        
        return content
    except httpx.TimeoutException:
        print("ERROR: Azure API timeout")
        raise Exception("Request to AI service timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        print(f"ERROR: Azure API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"AI service error: {e.response.status_code}")
    except Exception as e:
        print(f"ERROR: Azure API error: {str(e)}")
        raise


def build_prompt(query: str, context_chunks: List[str], sources: List[str]) -> str:
    context = "\n\n---\n\n".join([
        f"[Source: {src}]\n{chunk}"
        for chunk, src in zip(context_chunks, sources)
    ])
    
    prompt = f"""CONTEXT (Policy Documents):
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
