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
├── backend/        # Python/FastAPI
│   ├── app/
│   │   ├── api/        # HTTP route handlers
│   │   ├── models/     # SQLAlchemy ORM
│   │   ├── schemas/    # Pydantic validation
│   │   └── services/   # Business logic
│   ├── tests/          # pytest test suite
│   ├── migrations/     # Alembic migrations
│   └── pyproject.toml
│
├── frontend/       # React/TypeScript/Vite
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   ├── types/       # TypeScript types
│   │   ├── hooks/       # Custom React hooks
│   │   └── context/     # React contexts
│   └── package.json
│
└── database/
    └── schema.sql  # Reference schema
```

## Database Schema

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

- User signup/login (JWT authentication)
- Create and manage wallets
- Record income/expense transactions
- Categorize transactions (hierarchical categories)
- View balance per wallet
- Statistics and reports

## API Endpoints

| Endpoint | Description |
| ---------- | ------------- |
| `POST /api/v1/auth/signup` | User registration |
| `POST /api/v1/auth/login` | User login (returns JWT) |
| `GET/POST/PATCH/DELETE /api/v1/wallets` | Wallet CRUD |
| `GET/POST/PATCH/DELETE /api/v1/categories` | Category CRUD |
| `GET/POST/PATCH/DELETE /api/v1/transactions` | Transaction CRUD |
| `GET /api/v1/statistics` | Aggregated statistics |
| `GET /api/v1/statistics/report` | Period-based reports |

## Development

### Backend

```bash
cd backend/
pip install -e ".[dev]"           # Install dependencies
uvicorn app.main:app --reload     # Run dev server (localhost:8000)
pytest                            # Run tests (121 tests)
alembic upgrade head              # Apply migrations
```

### Frontend

```bash
cd frontend/
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
