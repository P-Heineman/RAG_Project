# ADR 002: Audit Logging Strategy
- **Status**: Accepted.
- **Context**: Need to track system usage and RAG query performance.
- **Decision**: Store anonymized queries and confidence scores in a local JSON file.
- **Reason**: Simplifies auditing without the overhead of a full database for logs.
- **Constraint**: Mask all PII (IPs, Keys) before persisting to the log.
