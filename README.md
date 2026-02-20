# Finance Policy RAG Chatbot

A RAG (Retrieval Augmented Generation) based chatbot that answers questions about three-wheeler financing policies using FastAPI, TF-IDF vector search, and Azure OpenAI's GPT-5 Nano model.

## Features

- **PDF Document Processing**: Extracts and chunks text from policy PDFs
- **TF-IDF Vector Search**: Uses scikit-learn TF-IDF for semantic search
- **Guard Rails**: Ensures responses only come from provided documents
- **Azure OpenAI Integration**: Uses GPT-5 Nano for natural language responses
- **REST API**: FastAPI-based endpoints for chat, health check, and index management

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── rag/
│   │   ├── pdf_processor.py # PDF text extraction & chunking
│   │   ├── faiss_store.py  # TF-IDF index management
│   │   └── chatbot.py      # RAG pipeline with guard rails
│   └── routers/
│       └── chat.py          # API endpoints
├── data/
│   ├── index_vectors.pkl   # Persisted TF-IDF vectors
│   └── index_vectorizer.pkl # Persisted TF-IDF vectorizer
├── documents/              # PDF documents (add your PDFs here)
│   ├── New -Three wheeler Financing -Policy Note - V 2.pdf
│   └── New Policy Amendment-3W-Oct2025.pdf
├── .env                    # Environment variables (create this)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.12+
- Docker & Docker Compose (for Docker setup)
- Azure OpenAI API access

## Setup with Virtual Environment

### 1. Clone and Navigate

```bash
cd finance-policy-rag
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

## Setup with Docker

### 1. Configure Environment Variables

Create a `.env` file:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
```

### 2. Build and Run

```bash
docker-compose up --build
```

The server will start at `http://localhost:8000`

### 3. Rebuild Index (if PDFs change)

```bash
docker-compose exec rag-chatbot python -c "from app.rag.chatbot import reload_index; reload_index()"
```

---

## How to Add More Documents

### Step 1: Add PDF Files

Place your new PDF files in the `documents/` folder:

```bash
# Copy new PDFs to documents folder
cp new-policy.pdf documents/
```

### Step 2: Rebuild the Index

**Option A: Using the API (recommended)**
```bash
curl -X POST http://localhost:8000/api/reload
```

**Option B: Using Python directly**
```bash
# If running locally with venv
python -c "from app.rag.chatbot import reload_index; reload_index()"

# If running with Docker
docker-compose exec rag-chatbot python -c "from app.rag.chatbot import reload_index; reload_index()"
```

### Step 3: Verify

Check the health endpoint to confirm the index was rebuilt:
```bash
curl -X GET http://localhost:8000/api/health
```

The response should show the updated chunk count.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check service health and index status |
| POST | `/api/chat` | Chat with the policy documents |
| POST | `/api/reload` | Rebuild the index from PDFs |

### Example Usage

**Health Check:**
```bash
curl -X GET http://localhost:8000/api/health
```

**Chat:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the minimum age for applicant?"}'
```

**Rebuild Index:**
```bash
curl -X POST http://localhost:8000/api/reload
```

---

## Guard Rails

The chatbot is configured to:
- **Only answer** from provided PDF documents
- **Reject out-of-scope** queries with a standardized message
- **Provide source citations** for all answers
- **Use relevance threshold** (0.1) to filter irrelevant results

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `chunk_size` | 800 | Characters per text chunk |
| `chunk_overlap` | 100 | Overlap between chunks |
| `top_k` | 5 | Number of chunks to retrieve |
| `relevance_threshold` | 0.1 | Minimum similarity score |

Modify these in `app/config.py` as needed.

---

## Testing

Example test questions:

```bash
# Policy questions (should work)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the minimum age for applicant?"}'

# Out of scope (should reject)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather today?"}'
```

---

## Tech Stack

- **Backend**: FastAPI
- **Vector Search**: TF-IDF (scikit-learn)
- **LLM**: Azure OpenAI GPT-5 Nano
- **PDF Processing**: pypdf
- **HTTP Client**: httpx

---

## License

Internal use only - TVS Credit Services
