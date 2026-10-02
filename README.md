# CREAM

Personal finance tracker app.

## Tech Stack

| Layer | Technology |
| ------- | ------------ |
| Backend | Python, FastAPI |
| Frontend | React, TypeScript, Vite |
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
│    Backend      │  FastAPI
│   (Python)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  ACID, NUMERIC(19,4)
└─────────────────┘
```

- **FastAPI**: Handles HTTP, authentication, business logic, statistics, and reports.
- **React**: UI layer, communicates via REST API.
- **PostgreSQL**: ACID-compliant storage with precise decimal arithmetic.

## Project Structure

```text
cream/
├── docs/           # Documentation
│   ├── VISION.md
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── DOMAIN.md
│   ├── API.md
│   ├── PROGRESS.md
│   └── TESTING.md
│
├── api/            # Python/FastAPI
│   ├── app/
│   │   ├── api/        # HTTP route handlers
│   │   ├── models/     # SQLAlchemy ORM
│   │   ├── schemas/    # Pydantic validation
│   │   └── services/   # Business logic
│   ├── tests/          # pytest test suite
│   ├── migrations/     # Alembic migrations
│   └── pyproject.toml
│
└── web/            # React/TypeScript/Vite
    ├── src/
    │   ├── lib/         # API client, query client, utils
    │   ├── components/  # Shared UI components (shadcn/ui)
    │   ├── features/    # Feature modules (auth, wallets, transactions, reports)
    │   └── routes/      # Pages and router config
    └── package.json
```

## Database Schema

> **Source of truth:** the SQLAlchemy models in `api/app/models/`. Schema changes are applied via Alembic migrations in `api/migrations/` — never by hand.

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

- User signup/login (JWT in httpOnly session cookie)
- Create and manage wallets
- Record income/expense transactions
- Categorize transactions (hierarchical categories)
- View balance per wallet
- Statistics and reports

## API Endpoints

| Endpoint | Description |
| ---------- | ------------- |
| `GET /api/v1/health` | API and database availability (public) |
| `POST /api/v1/auth/signup` | User registration |
| `POST /api/v1/auth/login` | User login (sets session cookie) |
| `POST /api/v1/auth/logout` | End session |
| `GET /api/v1/auth/me` | Current user |
| `GET/POST/PATCH/DELETE /api/v1/wallets` | Wallet CRUD |
| `GET/POST/PATCH/DELETE /api/v1/categories` | Category CRUD |
| `GET/POST/PATCH/DELETE /api/v1/transactions` | Transaction CRUD |
| `GET /api/v1/statistics` | Aggregated statistics |
| `GET /api/v1/statistics/report` | Period-based reports |

## Development

### Backend

```bash
cd api/
uv sync                                  # Install dependencies
uv run uvicorn app.main:app --reload     # Run dev server (localhost:8000)
uv run pytest                            # Run tests
uv run alembic upgrade head              # Apply migrations
```

### Frontend

```bash
cd web/
npm install                       # Install dependencies
npm run dev                       # Run dev server (localhost:5173)
npm run build                     # Build for production
npm run lint                      # Run ESLint
```

## Future Features

- Entities (merchants, employers)
- Tags
- Recurring transactions
- Budgets and spending limits
- Receipt attachments
- Data export (CSV, JSON)
