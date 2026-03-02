# Project Setup Problems & Solutions

This document details all the issues faced while building the Finance Policy RAG Chatbot and their solutions.

---

## Environment & Tools

- **OS**: Windows
- **Python**: 3.12
- **Package Manager**: Initially uv, then switched to pip
- **LLM**: Azure OpenAI GPT-5 Nano
- **Vector Store**: Initially FAISS, switched to TF-IDF

---

## Problem 1: UV Package Manager Issues

### Symptoms
- UV failed to install large packages (torch, transformers)
- Cache access denied errors
- Slow dependency resolution

### Solution
Switched to pip with local virtual environment:
```bash
python -m venv venv
pip install -r requirements.txt
```

---

## Problem 2: Azure Embedding Deployment Not Found

### Symptoms
```
openai.NotFoundError: Error code: 404 - {'error': {'code': 'DeploymentNotFound', 'message': 'The API deployment for this resource does not exist'}}
```

When trying to use `text-embedding-3-small`:
```
GET https://fintechproject.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings
→ 404 DeploymentNotFound
```

### Investigation
Listed available models via API:
```python
client.get('https://fintechproject.openai.azure.com/openai/models?api-version=2025-01-01-preview')
```

Found that while `text-embedding-3-small` was available as a **model**, it was **not deployed** as an endpoint.

### Solution
Switched to local TF-IDF vectorization instead of neural embeddings:
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    stop_words='english',
    max_features=5000,
    ngram_range=(1, 2)
)
```

---

## Problem 3: HuggingFace Model Download Blocked

### Symptoms
```
SSL: CERTIFICATE_VERIFY_FAILED certificate verify failed: self-signed certificate in certificate chain
```

When trying to use sentence-transformers for local embeddings:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # Failed
```

Corporate network blocked access to HuggingFace.

### Solution
Used TF-IDF which requires no external downloads.

---

## Problem 4: SSL Certificate Errors with Azure

### Symptoms
```
httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

### Solution
Disabled SSL verification:
```python
client = httpx.Client(verify=False)
```

---

## Problem 5: Wrong Azure Endpoint URL

### Symptoms
```
openai.NotFoundError: Error code: 404 - {'error': {'code': '404', 'message': 'Resource not found'}}
```

### Root Cause
Stored full URL in `.env`:
```env
AZURE_OPENAI_ENDPOINT=https://fintechproject.openai.azure.com/openai/deployments/gpt-5-nano/chat/completions?api-version=2025-01-01-preview
```

But Azure client adds `/openai/deployments/{model}/` to the endpoint, causing doubled paths.

### Solution
Changed `.env` to use base URL only:
```env
AZURE_OPENAI_ENDPOINT=https://fintechproject.openai.azure.com
```

---

## Problem 6: GPT-5 Nano Parameter Issues

### Symptoms

**Issue A: max_tokens not supported**
```
openai.BadRequestError: {'error': {'message': "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead."}}
```

**Issue B: temperature not supported**
```
openai.BadRequestError: {'error': {'message': "Unsupported value: 'temperature' does not support 0.3 with this model. Only the default (1) value is supported."}}
```

**Issue C: Empty responses (Main Problem)**
When using the openai library, longer prompts returned empty content:
```python
response.choices[0].message.content  # → ""
response.choices[0].finish_reason    # → "length"
```

The model was using all tokens for "reasoning_tokens" (128-1000 tokens) and not outputting any content.

### Investigation
Testing with direct httpx worked:
```python
import httpx

client = httpx.Client(verify=False)
url = f"{azure_endpoint}/openai/deployments/gpt-5-nano/chat/completions?api-version=2025-01-01-preview"
data = {
    "messages": [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": prompt}
    ]
}
response = client.post(url, json=data, headers=headers)
# → Worked! Got proper content
```

### Solution
Used httpx directly instead of openai library:
```python
import httpx

def get_azure_chat_response(prompt: str) -> str:
    client = httpx.Client(verify=False, timeout=120.0)
    
    url = f"{settings.azure_openai_endpoint}/openai/deployments/gpt-5-nano/chat/completions?api-version=2025-01-01-preview"
    
    data = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    
    headers = {
        "api-key": settings.azure_openai_api_key,
        "Content-Type": "application/json"
    }
    
    response = client.post(url, json=data, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]
```

---

## Problem 7: TF-IDF Index File Naming

### Symptoms
Looking for `.faiss` files that didn't exist.

### Solution
Changed to `.pkl` files:
```python
# Before (didn't work)
settings.index_path = Path("data/index.faiss")

# After (works)
settings.index_path = Path("data/index")
# Saves as: data/index_vectors.pkl, data/index_vectorizer.pkl
```

---

## Problem 8: Health Endpoint Wrong Attribute

### Symptoms
```
AttributeError: 'FAISSStore' object has no attribute 'index'
```

### Root Cause
After switching from FAISS to TF-IDF, the class no longer had an `index` attribute.

### Solution
Changed to check `vectors` instead of `index`:
```python
# Before
index_loaded = faiss_store.index is not None

# After
index_loaded = faiss_store.vectors is not None
```

---

## Problem 9: Windows Path Issues in Commands

### Symptoms
- Backslashes in paths caused unicode escape errors
- Couldn't start server in background properly

### Solution
- Use raw strings: `r'F:\path'` or forward slashes
- Use Python to spawn server instead of background processes

---

## Summary of Key Learnings

### Azure OpenAI Setup
1. **Check deployments first** - Not all models are deployed
2. **Use base URL only** - Don't include `/deployments/` in env vars
3. **Test with httpx first** - More reliable than openai library
4. **Check parameter support** - Different models support different params

### Embeddings
1. **Have a fallback** - TF-IDF works offline
2. **Network restrictions matter** - Can't always download models
3. **Consider cost** - Local embeddings are free

### Development Tools
1. **uv not always better** - pip more reliable in restricted networks
2. **Test incrementally** - Build index before testing chat

---

## File Changes Summary

| File | Change |
|------|--------|
| `.env` | Changed to base URL only |
| `app/rag/faiss_store.py` | Switched to TF-IDF |
| `app/rag/chatbot.py` | Used httpx instead of openai |
| `app/routers/chat.py` | Fixed attribute check |
| `app/config.py` | Updated pdf_dir to documents/ |

---

## Alternative Approaches to Try

If you want to use proper embeddings in the future:

1. **Deploy embedding model in Azure**
   - Go to Azure OpenAI Studio
   - Deploy `text-embedding-3-small`
   - Use the deployment name in code

2. **Use a different cloud provider**
   - AWS Bedrock
   - Google Vertex AI

3. **Host embedding model separately**
   - Use a server with internet access
   - Run Ollama or similar locally
