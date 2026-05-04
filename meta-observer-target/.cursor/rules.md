# The Watchtower Cursor Rules

## 1. RAG Standards
- **Chunking Strategy**: Use RecursiveCharacterTextSplitter with `chunk_size=500` and `overlap=50`.
- **Embeddings**: Always use `sentence-transformers/all-MiniLM-L6-v2` for local development.
- **Privacy**: No PII in vector store. Use `utils.mask_pii` before indexing.

## 2. Backend (FastAPI)
- **Async**: All DB and Vector Store operations MUST be async.
- **Typing**: Use Pydantic models for all API requests/responses. No generic Dicts.
- **Dependencies**: Use `FastAPI.Depends` for ChromaDB client and LLM service.

## 3. Frontend (React)
- **UI Components**: Use Shadcn/UI (Radix UI) exclusively.
- **State**: Use TanStack Query for server state.
- **Visuals**: Confidence scores must be color-coded (Green > 0.8, Yellow > 0.5, Red < 0.5).

## 4. Audit Logging
- **Location**: `backend/data/audit_log.json`.
- **Anonymization**: Mandatory masking of IPs and API keys.
- **Retention**: Keep logs for 30 days.

## 5. Resilience & Retries
- **Retries**: Max 3 attempts with exponential backoff for all AI/DB calls.
- **Safe Mode**: Fallback to local cache if Vector DB latency > 5s or status != 200.
- **Circuit Breaker**: Trip the breaker after 5 consecutive failures.

## 6. Prohibitions
- NEVER use `print()`. Use `structlog` or standard `logging`.
- NEVER hardcode the vector DB path. Use `VECTOR_DB_PATH` env var.
