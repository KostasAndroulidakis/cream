# CREAM Architecture

## Overview

CREAM follows a classic three-tier web architecture optimized for simplicity and maintainability.

```text
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                   React + TypeScript                        │
│              Single Page Application (SPA)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS / REST API
                          │ JSON payloads
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│                   Python + FastAPI                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Routers   │  │  Services   │  │     Validation      │  │
│  │  (HTTP/API) │─▶│ (Business)  │─▶│  (Business Rules)   │  │
│  └─────────────┘  └──────┬──────┘  └─────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLAlchemy ORM + Pydantic              │    │
│  │           (Data Access + Serialization)             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQL / psycopg
                          │ Connection pooling
                          ▼
                          │                    ┌─────────────────────┐
                          │   HTTPS, JWT RS256 │   Enable Banking    │
                          ├───────────────────▶│ (PSD2 AIS, optional)│
                          │                    └─────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                              │
│                      PostgreSQL                             │
│                                                             │
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
- Never handles the JWT: the browser stores it as an `httpOnly` cookie

**Boundaries**:

- Does NOT access database directly
- Does NOT implement business logic
- Does NOT store sensitive data (no tokens in memory or localStorage)

**Technology Choices**:

| Choice | Rationale |
| -------- | ----------- |
| React | Component-based, large ecosystem, well-documented |
| TypeScript | Type safety, better IDE support, fewer runtime errors |
| SPA | Better UX, reduced server load, offline potential |
| Vite dev proxy | `/api` is proxied to FastAPI, so the browser sees one origin: no CORS needed in development |
| Generated API types | `openapi-typescript` + `openapi-fetch`: Pydantic schemas are the single source of truth |
| TanStack Query | Server state, caching and invalidation instead of hand-written fetch effects |
| Tailwind + shadcn/ui | Accessible primitives (Base UI) with a small set of design tokens |

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
| JWT in `httpOnly` cookie | Stateless auth; JavaScript can't read the token (XSS can't steal it) |
| uv | Fast, reproducible Python environments with a lockfile |

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
   │ Cookie: cream_session=<jwt> (sent by the browser)
   │ Body: {wallet_id, category_id, amount, ...}
   ▼
4. Backend: Router receives request
   │
   ▼
5. Backend: Auth dependency validates JWT from cookie
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
   │ Cookie: cream_session=<jwt> (sent by the browser)
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
│   ├── API.md
│   ├── PROGRESS.md
│   └── TESTING.md
│
├── compose.yaml             # PostgreSQL for development
├── .env.example             # Copy to .env (never committed)
│
├── api/                     # Python/FastAPI backend
│   ├── app/
│   │   ├── api/            # HTTP route handlers (auth, bank, categories, health, statistics, transactions, wallets)
│   │   ├── models/         # SQLAlchemy ORM models: the schema's source of truth
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic
│   │   │   ├── auth.py, session.py      # Passwords, JWT, session cookie
│   │   │   ├── authorization.py         # Ownership and access checks
│   │   │   ├── wallets.py, statistics.py, validation.py, health.py
│   │   │   ├── transactions.py, merchants.py   # Edit rules (single and bulk), merchants
│   │   │   ├── review.py, preferences.py       # Review inbox, user preferences
│   │   │   ├── banking/                 # Enable Banking: client, mapping, connections, sync
│   │   │   └── categorization/          # Merchant keys, MCC map, auto-categorizer, rules
│   │   ├── config.py       # Settings from the root .env
│   │   ├── database.py     # Engine, session, Base (global type rules)
│   │   └── main.py         # FastAPI app entry point
│   ├── migrations/         # Alembic migrations (incl. seeded default categories)
│   ├── scripts/            # export_openapi.py for web type generation
│   ├── tests/              # pytest suite (SQLite in memory, fake bank provider)
│   └── pyproject.toml      # Dependencies (uv)
│
└── web/                    # React/TypeScript/Vite frontend
    ├── src/
    │   ├── lib/            # API client + generated schema, query client, money/date/amount helpers
    │   ├── components/     # Shared UI; components/ui = shadcn/ui
    │   ├── features/       # auth, wallets, transactions, categories, categorization, bank, health
    │   └── routes/         # Pages, app layout, auth guards, router
    └── package.json
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

- Totals are shown per currency (`/wallets/totals`), never summed across currencies
- Known gap: `/statistics` still sums income/expenses nominally across currencies
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

### ADR6: Session Cookie Instead of Bearer Tokens

**Decision**: The JWT lives in an `httpOnly`, `Secure`, `SameSite=Strict` cookie scoped to `/api`.
`Authorization: Bearer` headers are not accepted.

**Rationale**:

- JavaScript (and so any XSS) can never read the token
- `SameSite=Strict` plus JSON-only request bodies block cross-site request forgery
- Same origin in development through the Vite proxy

**Consequences**:

- A 401 on any request ends the session in the web client and returns to login
- No token refresh yet: sessions last `CREAM_ACCESS_TOKEN_EXPIRE_MINUTES`

### ADR7: Monarch's Default Categories and a Transfer Type

**Decision**: Seed Monarch's default category set (groups containing categories) with stable keys,
and add a `transfer` category type that is excluded from income/expense statistics.

**Rationale**:

- A proven taxonomy beats an invented one; stable keys enable translations and MCC mapping
- With several synced accounts, moving money between them must not count twice

**Consequences**:

- Transactions use categories, never groups; a subcategory has its parent's type
- The seed lives frozen inside its migration; catalog changes need new migrations

### ADR8: Optional Bank Sync via Enable Banking

**Decision**: Read-only bank sync through Enable Banking (licensed PSD2 AISP), restricted to the
owner's own accounts. Manual entry stays first-class.

**Rationale**:

- Covers the owner's banks (Eurobank, Piraeus, N26, Revolut, PayPal) without a PSD2 licence
- Read-only, revocable consent; data is stored only in CREAM's own database

**Consequences**:

- Consent expires after at most 180 days; the user reconnects
- Only booked transactions are imported; identity = bank `transaction_id` or a fingerprint, with
  same-day repeats numbered (bank `entry_reference` values are reused and are not unique)
- The first sync sets the wallet's initial balance so CREAM matches the bank exactly
- The provider's private key stays outside the repository (`CREAM_ENABLEBANKING_KEY_PATH`)

### ADR9: Rule-First Auto-Categorization with a Category Source

**Decision**: Categorize imports in a fixed order (the user's merchant rule, then a static MCC map, then
Uncategorized) and record on every transaction who chose its category (`manual` / `rule` / `mcc` / `default`).

**Rationale**:

- The user's own choices are the strongest signal; MCC is a good generic fallback (Plaid's taxonomy as a guide)
- Knowing the source lets automation fix its own guesses without ever overwriting a deliberate choice
- Deterministic and explainable: no model to train, the same input always lands in the same category

**Consequences**:

- Merchants are matched by a normalized key (counterparty, else the bank text), stored on the transaction
- The MCC map lives in code (`services/categorization/mcc.py`) and maps to category keys; a test checks
  every key exists in the seeded catalog
- Each sync retries `default` transactions, so a better map or a new rule also fixes older imports
- The Uncategorized system category doubled as the review inbox (replaced by ADR10)

### ADR10: Review Status Independent of the Category

**Decision**: A `needs_review` flag on every transaction is the review inbox, as in Monarch. Imports set it
from the user's preferences (review every new transaction, or only those left in Uncategorized); after that
only the user changes it.

**Rationale**:

- "I've looked at this" and "this has a category" are different: a category from a rule or the MCC can still
  be worth a look, and an uncategorized transfer may be fine as it is
- Hiding and reviewing stay separate too, so showing a transaction again doesn't lose its status

**Consequences**:

- Choosing a category no longer empties the inbox: the user marks transactions reviewed (✓, or in bulk)
- Preferences live in `user_preferences`, one optional row per user; defaults come from the model
- Rules that set the review status come with the rules editor

### ADR11: Monarch's Account Types, One Catalog in Code

**Decision**: Accounts use Monarch's types (each an asset or a liability) and subtypes (Plaid's taxonomy, with the
lists Monarch shows for real estate, vehicles, valuables and loans). The catalog lives in
`services/account_types.py`; the API validates against it and serves it (`GET /wallets/types`) with labels.

**Rationale**:

- Monarch's grouping (Cash, Investments, … Credit Card, Loans) drives the Accounts page and net worth
- One catalog: validation, labels and order can't drift apart; the web keeps only the icons

**Consequences**:

- `wallets.type` is the group, `wallets.subtype` a key checked against it; a type alone gets its first subtype
- Existing wallets became Cash (bank → Checking, digital → PayPal, cash and stash → Savings)
- The code keeps the name "wallet"; the UI says "account"

## Security Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Transport Security                                      │
│     └── HTTPS (TLS) for all communications                  │
│                                                             │
│  2. Authentication                                          │
│     └── JWT in httpOnly/Secure/SameSite=Strict cookie       │
│     └── bcrypt password hashing                             │
│                                                             │
│  3. Authorization                                           │
│     └── User can only access own resources                  │
│     └── Verified on every request                           │
│                                                             │
│  4. Input Validation                                        │
│     └── Pydantic schema validation                          │
│     └── Business rule validation                            │
│     └── SQL injection prevention (ORM)                      │
│                                                             │
│  5. Data Isolation                                          │
│     └── All queries filter by user_id                       │
│     └── Foreign keys enforce referential integrity          │
│                                                             │
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
│                      Load Balancer                          │
│                    (nginx / cloud LB)                       │
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
