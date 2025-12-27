# CREAM Architecture

## Overview

CREAM follows a classic three-tier web architecture optimized for simplicity and maintainability.

```text
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                   React + TypeScript                         │
│              Single Page Application (SPA)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS / REST API
                          │ JSON payloads
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                   Python + FastAPI                           │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Routers   │  │  Services   │  │     Validation      │  │
│  │  (HTTP/API) │─▶│ (Business)  │─▶│  (Business Rules)   │  │
│  └─────────────┘  └──────┬──────┘  └─────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLAlchemy ORM + Pydantic              │    │
│  │           (Data Access + Serialization)             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQL / psycopg
                          │ Connection pooling
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
│                      PostgreSQL                              │
│                                                              │
│    ACID transactions, NUMERIC(19,4) precision               │
│    Indexed queries, Referential integrity                   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Frontend (React + TypeScript)

**Responsibility**: User interface and client-side logic

- Renders UI components
- Manages client-side state
- Communicates with backend via REST API
- Handles user input and validation feedback
- Stores JWT token for authentication

**Boundaries**:

- Does NOT access database directly
- Does NOT implement business logic
- Does NOT store sensitive data (except JWT in memory/localStorage)

**Technology Choices**:

| Choice | Rationale |
| -------- | ----------- |
| React | Component-based, large ecosystem, well-documented |
| TypeScript | Type safety, better IDE support, fewer runtime errors |
| SPA | Better UX, reduced server load, offline potential |

### Backend (Python + FastAPI)

**Responsibility**: Business logic, data access, and API

- Exposes REST API endpoints
- Authenticates and authorizes requests
- Validates input data (schema + business rules)
- Executes business logic
- Manages database transactions
- Returns structured responses

**Boundaries**:

- Does NOT render HTML (API only)
- Does NOT store state between requests (stateless)
- Does NOT expose database schema directly

**Technology Choices**:

| Choice | Rationale |
| -------- | ----------- |
| Python | Readable, large ecosystem, fast development |
| FastAPI | Modern async support, automatic OpenAPI docs, Pydantic integration |
| SQLAlchemy | Mature ORM, good PostgreSQL support, migration tooling |
| Pydantic | Data validation, serialization, type hints |
| JWT | Stateless auth, scalable, standard |

### Database (PostgreSQL)

**Responsibility**: Persistent data storage

- Stores all application data
- Enforces referential integrity (foreign keys)
- Provides ACID transactions
- Supports precise decimal arithmetic (NUMERIC)
- Enables efficient queries via indexes

**Boundaries**:

- Does NOT implement business logic (no stored procedures)
- Does NOT handle authentication (backend responsibility)
- Does NOT communicate with frontend directly

**Technology Choices**:

| Choice | Rationale |
| -------- | ----------- |
| PostgreSQL | ACID compliance, NUMERIC type, mature, free |
| NUMERIC(19,4) | Exact decimal arithmetic for money |
| Alembic | Database migrations, version control for schema |

## Data Flow

### Write Operation (Create Transaction)

```text
1. User submits form
   │
   ▼
2. Frontend validates input (basic)
   │
   ▼
3. Frontend sends POST /api/v1/transactions
   │ Authorization: Bearer <jwt>
   │ Body: {wallet_id, category_id, amount, ...}
   ▼
4. Backend: Router receives request
   │
   ▼
5. Backend: Auth middleware validates JWT
   │ Extracts user_id from token
   ▼
6. Backend: Pydantic validates schema
   │ Type checking, required fields
   ▼
7. Backend: Business validation
   │ Amount rules, date rules, ownership
   ▼
8. Backend: Service creates transaction
   │ SQLAlchemy model, db.add(), db.commit()
   ▼
9. Database: INSERT with ACID guarantees
   │
   ▼
10. Backend: Returns 201 + created entity
    │
    ▼
11. Frontend: Updates UI state
```

### Read Operation (Get Statistics)

```text
1. User navigates to dashboard
   │
   ▼
2. Frontend sends GET /api/v1/statistics
   │ Authorization: Bearer <jwt>
   ▼
3. Backend: Auth validates JWT, extracts user_id
   │
   ▼
4. Backend: Service queries database
   │ SELECT with SUM, GROUP BY
   │ Filtered by user's wallets
   ▼
5. Database: Executes optimized query
   │ Uses indexes on wallet_id, category_id
   ▼
6. Backend: Formats response
   │ Pydantic serialization
   ▼
7. Frontend: Renders dashboard
```

## Project Structure

```text
cream/
├── docs/                    # Documentation
│   ├── VISION.md
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md      # This file
│   ├── DOMAIN.md
│   └── API.md
│
├── backend/                 # Python/FastAPI backend
│   ├── app/
│   │   ├── api/            # HTTP route handlers
│   │   │   ├── auth.py
│   │   │   ├── wallets.py
│   │   │   ├── categories.py
│   │   │   ├── transactions.py
│   │   │   └── statistics.py
│   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── wallet.py
│   │   │   ├── category.py
│   │   │   └── transaction.py
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   │   ├── user.py
│   │   │   ├── wallet.py
│   │   │   ├── category.py
│   │   │   ├── transaction.py
│   │   │   └── statistics.py
│   │   ├── services/       # Business logic
│   │   │   ├── auth.py
│   │   │   └── validation.py
│   │   ├── config.py       # Configuration (env vars)
│   │   ├── database.py     # DB connection setup
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # pytest test suite
│   ├── migrations/         # Alembic migrations
│   └── pyproject.toml      # Dependencies
│
├── frontend/               # React/TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   └── package.json
│
└── database/
    └── schema.sql          # Reference schema
```

## Key Architectural Decisions

### ADR1: Stateless Backend

**Decision**: Backend stores no session state; all state is in JWT or database.

**Rationale**:

- Enables horizontal scaling
- Simplifies deployment
- No session storage needed

**Consequences**:

- JWT must contain user_id
- Token refresh needed for long sessions

### ADR2: SQL for Aggregations

**Decision**: Use SQL (SUM, GROUP BY) for statistics instead of application-level calculations.

**Rationale**:

- PostgreSQL is optimized for aggregations
- Reduces data transfer (aggregate in DB, not app)
- Leverages database indexes

**Consequences**:

- Some queries may be complex
- Must ensure proper indexing

### ADR3: No Soft Deletes

**Decision**: DELETE operations actually remove data from database.

**Rationale**:

- Simpler data model
- GDPR-friendly (actual deletion)
- No "deleted" flag complexity

**Consequences**:

- No undo functionality (by design)
- Must be clear in UI that delete is permanent

### ADR4: Single Currency per Wallet

**Decision**: Each wallet has one currency; no automatic conversion.

**Rationale**:

- Avoids exchange rate complexity
- Users can create multiple wallets for different currencies
- No external API dependencies

**Consequences**:

- Total balance across currencies shows nominal sum
- Future: may add currency conversion as optional feature

### ADR5: Hierarchical Categories with SQL

**Decision**: Category hierarchy stored with parent_id, queried via recursive CTE or application logic.

**Rationale**:

- Simple schema (self-referential foreign key)
- PostgreSQL supports recursive queries
- Flexible depth

**Consequences**:

- Must prevent cycles in application layer
- Deep hierarchies may need optimization

## Security Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Transport Security                                       │
│     └── HTTPS (TLS) for all communications                  │
│                                                              │
│  2. Authentication                                           │
│     └── JWT tokens with expiration                          │
│     └── bcrypt password hashing                             │
│                                                              │
│  3. Authorization                                            │
│     └── User can only access own resources                  │
│     └── Verified on every request                           │
│                                                              │
│  4. Input Validation                                         │
│     └── Pydantic schema validation                          │
│     └── Business rule validation                            │
│     └── SQL injection prevention (ORM)                      │
│                                                              │
│  5. Data Isolation                                           │
│     └── All queries filter by user_id                       │
│     └── Foreign keys enforce referential integrity          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Considerations

Current architecture supports vertical scaling. For horizontal scaling:

1. **Backend**: Already stateless, can run multiple instances behind load balancer
2. **Database**: PostgreSQL supports read replicas for read-heavy workloads
3. **Caching**: Can add Redis for session/query caching if needed (not in MVP)

## Deployment Architecture (Production)

```text
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
│                    (nginx / cloud LB)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
     ┌─────────┐    ┌─────────┐    ┌─────────┐
     │ Backend │    │ Backend │    │ Backend │
     │   (1)   │    │   (2)   │    │   (n)   │
     └────┬────┘    └────┬────┘    └────┬────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ PostgreSQL  │
                   │  (primary)  │
                   └─────────────┘
```
