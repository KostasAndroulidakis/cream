# CREAM

Personal finance tracker app.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Core Engine | C++ (validation, Money arithmetic) |
| Backend | Python, FastAPI (API, DB, statistics, reports) |
| Frontend | React, TypeScript |
| Database | PostgreSQL |

## Architecture

```text
┌─────────────────┐
│    Frontend     │  React + TypeScript
│   (REST/WS)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Backend      │  FastAPI (orchestrator)
│  ┌───────────┐  │
│  │ C++ Core  │  │  pybind11 bindings
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  ACID, NUMERIC(19,4)
└─────────────────┘
```

- **C++ Core**: Compute engine for validation and Money arithmetic. No DB/web access.
- **FastAPI**: Orchestrator. Handles HTTP, manages DB, statistics, and reports.
- **React**: UI layer, communicates via REST or WebSocket.
- **PostgreSQL**: ACID-compliant storage with Alembic migrations.

### Separation of Concerns

| Layer | Responsibilities |
|-------|------------------|
| **Backend (Python)** | HTTP/API, Authentication, DB read/write, Statistics (SQL aggregations), Reports (SQL queries) |
| **C++ Core** | Transaction validation, Money type (precise decimal arithmetic), Complex in-memory calculations |

The C++ core is a **compute-only** library. It receives data as input, performs calculations, and returns results. It has **no access** to the database or network.

## Project Structure

```text
cream/
├── core/           # C++ engine
│   ├── src/
│   ├── include/
│   ├── tests/
│   └── CMakeLists.txt
│
├── backend/        # Python/FastAPI
│   ├── app/
│   │   ├── api/
│   │   ├── models/     # SQLAlchemy
│   │   ├── schemas/    # Pydantic
│   │   └── services/
│   ├── migrations/     # Alembic
│   └── pyproject.toml
│
├── frontend/       # React/TypeScript
│   ├── src/
│   └── package.json
│
└── database/       # SQL schemas
    └── schema.sql
```

## Database Schema (MVP)

```text
┌─────────┐       ┌─────────────┐
│  users  │───1:N─│   wallets   │
└─────────┘       └─────────────┘
     │                   │
     │ 1:N               │ 1:N
     ▼                   ▼
┌────────────┐    ┌──────────────┐
│ categories │◄───│ transactions │
└────────────┘    └──────────────┘
```

| Table | Purpose |
| ------- | --------- |
| users | Authentication, profile |
| wallets | Bank accounts, cash, digital wallets |
| categories | Hierarchical income/expense categories |
| transactions | Financial transactions |

## MVP Features

- User signup/login
- Create and manage wallets
- Record income/expense transactions
- Categorize transactions (hierarchical categories)
- View balance per wallet
- Dashboard with summary

## Future Features

- Entities (merchants, employers)
- Tags
- Recurring transactions
- Budgets and spending limits
- Receipt attachments
- Reports and exports

## Specification

### Wallets

Track balances across:

- Bank Accounts
- Digital Wallets (PayPal, Google Pay, etc.)
- Cash/Personal Wallets
- Stashes

### Transactions

- Amount (positive for income, negative for expense)
- Category
- Wallet
- Date and time
- Description

### Program Flow

1. Login/Signup screen
2. Dashboard: balances, recent transactions, month summary
3. Add/edit transactions
4. Manage categories and wallets
5. Generate reports
