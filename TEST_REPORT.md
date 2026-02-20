# RAG Chatbot Test Report

**Date:** February 18, 2026  
**Model:** Azure GPT-5 Nano  
**Vector Store:** TF-IDF + Cosine Similarity  
**Index:** 55 chunks from 2 PDF documents

---

## Summary

| Category | Total | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
| Easy | 4 | 4 | 0 | 100% |
| Out of Scope | 5 | 5 | 0 | 100% |
| Medium | 4 | 4 | 0 | 100% |
| Hard | 4 | 4 | 0 | 100% |
| **Total** | **17** | **17** | **0** | **100%** |

---

## Detailed Results

### ✅ Easy Questions (Policy Knowledge)

| Question | Answer | Sources |
|----------|--------|---------|
| What is the financing policy for three wheelers? | The financing policy aims to simplify and relax policy parameters to cater to customer and market requirements and to gain higher market share in Three-Wheeler Financing... | Both PDFs |
| What is the minimum age for applicant? | Minimum age: 20 years | Both PDFs |
| What is the maximum age for three wheeler financing? | 65 years (maximum age not to exceed 65 at the end of the loan tenure) | Both PDFs |
| What are the credit norms? | Credit norms include: Eligible models - All Passenger 3 Wheeler models manufactured by TVSM... | Both PDFs |

---

### ✅ Out of Scope (Guard Rails Working)

| Question | Response | Status |
|----------|----------|--------|
| What is the weather today? | I don't have information about that in the provided documents... | ✅ Rejected |
| Who is the President of India? | I don't have information about that in the provided documents... | ✅ Rejected |
| How do I bake a cake? | I don't have information about that in the provided documents... | ✅ Rejected |
| What is Python programming? | I don't have information about that in the provided documents... | ✅ Rejected |
| Tell me about cricket | I don't have information about that in the provided documents... | ✅ Rejected |

---

### ✅ Medium Questions (Cross-Reference)

| Question | Answer | Sources |
|----------|--------|---------|
| What is the latest policy version? | Policy Version 2.3 (New Three-Wheeler - Policy Version 2.3 – Proposed October 2025) | New Policy Amendment-3W-Oct2025.pdf |
| When was Policy Version 2.0 launched? | April 2024 | New -Three wheeler Financing -Policy Note - V 2.pdf |
| What is the minimum age for co-applicant? | 18 years (completed) | New Policy Amendment-3W-Oct2025.pdf |
| What is the age criteria for guarantor? | Not found in documents | - |

---

### ✅ Hard Questions (Specific Details)

| Question | Answer | Sources |
|----------|--------|---------|
| What is the Cibil criteria for L1 category? | L1 corresponds to Thin Cibil accounts | Both PDFs |
| What is the income criteria for three wheeler loan? | Gross household income > Rs. 25,000/month | Both PDFs |
| What is the security required for the loan? | Security PDC or Security NACH | Both PDFs |
| What is the minimum loan amount? | Rs. 50,000 | New -Three wheeler Financing -Policy Note - V 2.pdf |

---

## Guard Rails Verification

The chatbot correctly:
- ✅ Answers only from provided documents
- ✅ Rejects out-of-scope queries with standardized message
- ✅ Provides source citations
- ✅ Returns empty sources for rejected queries

---

## API Endpoints

```bash
# Health Check
curl -X GET http://127.0.0.1:8000/api/health

# Chat
curl -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"Your question here\"}"

# Reload Index
curl -X POST http://127.0.0.1:8000/api/reload
```

---

## Conclusion

**Status: ✅ WORKING**

The RAG chatbot is functioning correctly with:
- 100% pass rate on all test categories
- Proper context-only responses
- Effective guard rails for out-of-scope queries
- Accurate source attribution
