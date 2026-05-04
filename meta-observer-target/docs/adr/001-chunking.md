# ADR 001: Chunking Strategy
- **Status**: Accepted.
- **Context**: Incident reports vary from short logs to long post-mortems.
- **Decision**: 500-character chunks with 50-character overlap.
- **Consequence**: Ensures enough context for the LLM while keeping embeddings precise.

# ADR 002: Metadata Filtering
- **Status**: Mandatory.
- **Requirement**: Every entry in ChromaDB must include `severity`, `service_name`, and `timestamp` in metadata.
