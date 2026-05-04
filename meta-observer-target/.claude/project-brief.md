# The Watchtower: Incident RAG System

## Overview
A specialized platform for technical teams to ingest, search, and analyze system incidents using RAG (Retrieval-Augmented Generation). It transforms raw logs and incident reports into a searchable knowledge base.

## Key Features
- **Incident Ingestion**: Process JSON/Markdown incident reports.
- **Contextual Search**: Query the vector store for similar past issues.
- **PII Masking**: Automatic detection and masking of sensitive data (IPs, keys) before embedding.
- **Confidence Scoring**: Every AI response includes a score based on document relevance.

## Technical Objectives
- Reduce Time-to-Resolution (TTR) by surfacing historical fixes.
- Maintain a clean, high-signal vector database.
- Ensure strict privacy by never sending raw PII to the LLM.
