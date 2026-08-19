# CSV Evidence Tracker Architecture Diagram

> **Authorship:** This architecture diagram was designed and created by Alianis Reyes Reyes for the CSV Evidence Tracker portfolio project. It represents a portfolio-safe demonstration environment using synthetic data only.

## System Context

```mermaid
flowchart LR
    U[Portfolio Reviewer / Demo User]
    B[Browser]
    N[Nginx Reverse Proxy]
    F[React Frontend]
    A[FastAPI Backend]
    AM[Audit Middleware]
    R[API Routers]
    S[Risk Scoring Service]
    DB[(SQLite Database)]
    D[Synthetic Seed Data]

    U --> B
    B --> N
    N --> F
    N --> A
    F -->|HTTPS / JSON API| A
    A --> AM
    AM --> R
    R --> S
    R --> DB
    AM --> DB
    D --> DB
```

## Component Responsibilities

| Component | Responsibility |
|---|---|
| React frontend | Presents dashboard, traceability, test execution, deviation, and audit-trail demonstration views. |
| Nginx reverse proxy | Serves the frontend and routes API traffic to the backend in the containerized demonstration environment. |
| FastAPI backend | Exposes API endpoints and coordinates validation-workflow operations. |
| API routers | Group endpoint logic by functional area, including requirements, tests, deviations, evidence, and audit records. |
| Audit middleware | Records selected application actions as audit-trail-style events. |
| Risk scoring service | Calculates or derives risk-oriented metrics used in the demonstration workflow. |
| SQLite database | Stores synthetic CSV evidence-tracker records and audit events. |
| Synthetic seed data | Provides fictional demonstration records; no real regulated, patient, product, or proprietary data is permitted. |

## Data and Request Flow

```mermaid
sequenceDiagram
    actor User as Portfolio Reviewer / Demo User
    participant UI as React Frontend
    participant Proxy as Nginx
    participant API as FastAPI Backend
    participant Audit as Audit Middleware
    participant Router as API Router
    participant DB as SQLite

    User->>UI: View or update demonstration record
    UI->>Proxy: HTTP request
    Proxy->>API: Forward request
    API->>Audit: Capture action context
    Audit->>Router: Continue request
    Router->>DB: Query or persist synthetic record
    DB-->>Router: Result
    Router-->>Audit: Response outcome
    Audit->>DB: Record audit-style event
    Audit-->>API: Complete response
    API-->>Proxy: JSON response
    Proxy-->>UI: JSON response
    UI-->>User: Render result
```

## Deployment View

```mermaid
flowchart TB
    subgraph Docker Compose Demonstration Environment
        direction TB
        nginx[Nginx Container]
        frontend[React Frontend Build]
        backend[FastAPI Application Container]
        sqlite[(SQLite File Volume)]

        nginx --> frontend
        nginx --> backend
        backend --> sqlite
    end

    user[Local Browser] --> nginx
```

## Scope and Limitations

This diagram documents a demonstration architecture, not a production GxP architecture. It does not claim validated infrastructure, production-grade identity management, electronic signatures, backup and disaster recovery, formal change control, or compliance with 21 CFR Part 11. The system is intended only for local or portfolio demonstration with synthetic data.
