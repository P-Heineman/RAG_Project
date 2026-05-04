# ADR 003: Resilience & Fallback Strategy
- **Status**: Accepted.
- **Context**: RAG systems depend on external Vector DBs and LLMs which may experience downtime.
- **Decision**: Implement a 'Safe Mode' fallback. If retrieval fails, use a localized keyword-based search on a cached subset of high-priority incidents.
- **Reasoning**: Ensures the system remains partially functional even during partial service outages.
- **Stale Cache Policy**: Cache is considered stale after 24 hours or after a successful index update.
