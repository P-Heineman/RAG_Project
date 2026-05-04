# System Architecture

## Data Flow
1. **Ingest**: Raw Incident -> PII Masking -> Chunking -> Embedding -> ChromaDB.
2. **Query**: User Question -> Embedding -> Vector Search -> Context Window -> LLM -> Answer.

## Decision: Local Vector DB
- **Choice**: ChromaDB.
- **Reason**: Lightweight, persistent, and supports async operations better than FAISS for this scale.

## Decision: PII Masking Layer
- **Choice**: Regex-based masking + Presidio (optional).
- **Critical**: This happens BEFORE any data leaves the local environment.

## Critical Fragility
- **Audit Log**: Every query is logged to `audit_log.json`. If the file grows too large, it may cause I/O delays.
- **Service Downtime**: Handled by the **Resilience Layer**. Uses a local cache as a fallback to prevent total system failure.
- **Hallucinations**: AI might suggest a fix that isn't in the retrieved context. Rules must enforce "Answer ONLY from context".
- **Similarity Drift**: Non-technical queries might pull irrelevant logs. AI must implement a threshold filter.
