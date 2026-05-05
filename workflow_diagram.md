## Agentic RAG Workflow Diagram

```mermaid
graph TD
    %% Nodes
    Start([User Query Input])
    Validate[Input Validation & <br/> Query Rewriting]
    Router{Event Router <br/> (LLM Decision)}
    Semantic[Semantic Search <br/> (Vector Store)]
    Structured[Structured Search <br/> (JSON Knowledge Base)]
    CheckResults{Results Found?}
        Fallback[Broad Search <br/> (Fallback Mechanism)]
    Synthesize[Response Synthesis <br/> (LLM)]
    End([Final Response])

    %% Flow
    Start --> Validate
    Validate --> Router
    Router -- "Conceptual/Semantic" --> Semantic
    Router -- "Structured/Lists" --> Structured
    Semantic --> CheckResults
    CheckResults -- "Yes" --> Synthesize
    CheckResults -- "No" --> Fallback
    Fallback --> Synthesize
    Structured --> Synthesize
    Synthesize --> End

    %% Styling
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style End fill:#f9f,stroke:#333,stroke-width:2px
    style Router fill:#fff4dd,stroke:#d4a017,stroke-width:2px
    style Validate fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style Semantic fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Structured fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Fallback fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Synthesize fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

