# CREAM

Personal finance tracker: every wallet, every euro, in one place. Enter transactions by hand or sync
them from your banks (read-only Open Banking).

> The name comes from Wu-Tang Clan's "C.R.E.A.M." ("Cash Rules Everything Around Me").

## Tech Stack

| Layer | Technology |
| ------- | ------------ |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, managed with `uv` |
| Frontend | React, TypeScript, Vite, Tailwind CSS, shadcn/ui (Base UI), TanStack Query, React Router |
| Database | PostgreSQL 18 (Docker Compose) |
| Bank sync | Enable Banking (PSD2 Account Information, optional) |

## Architecture

```text
┌──────────────────────┐   /api/* proxied by Vite in dev (single origin, no CORS)
│   web  (React SPA)   │──────────────────────────────┐
└──────────────────────┘                              ▼
                                         ┌──────────────────────┐      ┌──────────────────┐
                                         │   api  (FastAPI)     │─────▶│  Enable Banking  │
                                         │  httpOnly cookie JWT │ JWT  │  (PSD2, optional)│
                                         └──────────┬───────────┘ RS256└──────────────────┘
                                                    ▼
                                         ┌──────────────────────┐
                                         │ PostgreSQL           │  NUMERIC(19,4), ACID
                                         └──────────────────────┘
```

- **api**: authentication, business rules, statistics, bank sync. Single source of truth for data rules.
- **web**: UI only. TypeScript types are generated from the API's OpenAPI schema (`npm run gen:api`).
- **PostgreSQL**: exact decimal money, schema managed only by Alembic migrations.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for details and decisions.

## Features

- Signup / login with an `httpOnly` session cookie (the browser's JavaScript never sees the token)
- Wallets (bank, cash, digital, stash), one currency each; totals shown **per currency**, never mixed
- Income and expense transactions with Monarch's default categories (groups → categories)
- Transfer category type: moves money between your wallets without counting as income or expense
- Bank sync: connect a bank, link accounts to wallets, import booked transactions without duplicates
- Auto-categorization: merchant rules learned from your choices, then the bank's merchant category code (MCC);
  the rest waits in a **Review** inbox
- Expired sessions return to the login page automatically

Progress and what's next: [`docs/PROGRESS.md`](docs/PROGRESS.md).

## Project Structure

```text
cream/
├── compose.yaml        # PostgreSQL for development
├── .env.example        # Copy to .env (never committed)
├── docs/               # Vision, requirements, architecture, domain, API, progress, testing
├── api/                # Python / FastAPI
│   ├── app/
│   │   ├── api/        # HTTP route handlers
│   │   ├── models/     # SQLAlchemy ORM models (schema source of truth)
│   │   ├── schemas/    # Pydantic request/response models
│   │   └── services/   # Business logic (banking/ = Enable Banking; categorization/ = MCC map, rules, inbox)
│   ├── migrations/     # Alembic migrations
│   ├── scripts/        # export_openapi.py (feeds the web type generator)
│   └── tests/          # pytest suite
└── web/                # React / TypeScript / Vite
    └── src/
        ├── lib/        # API client + generated types, query client, money/date/amount helpers
        ├── components/ # Shared UI (shadcn/ui in components/ui)
        ├── features/   # auth, wallets, transactions, categories, categorization, bank, health
        └── routes/     # Pages, layout, guards, router
```

## Database

> **Source of truth:** the SQLAlchemy models in `api/app/models/`. Schema changes go through Alembic
> migrations in `api/migrations/`, never by hand.

```text
users ──1:N── wallets ──1:N── transactions ──N:1── categories (groups → categories, system + own)
  │              ▲
  ├──1:N── bank_connections ──1:N── bank_accounts ──(links to one wallet)
  └──1:N── merchant_rules ──N:1── categories
```

| Table | Purpose |
| ------- | --------- |
| users | Accounts and login |
| wallets | Bank accounts, cash, digital wallets, stashes |
| categories | System default groups/categories (stable `key`) and user categories |
| transactions | Money in/out; imported ones carry `external_id`, counterparty, MCC and `merchant_key`; `category_source` says who chose the category |
| merchant_rules | "This merchant always goes to this category", one per merchant per user |
| bank_connections | One bank consent (PSD2, up to 180 days) |
| bank_accounts | Accounts shared by a bank, linked to wallets |

## Getting Started

**Prerequisites:** Docker with the Compose plugin, [`uv`](https://docs.astral.sh/uv/), Node.js.

1. Configure environment (database credentials, optional bank sync):

   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d db
   ```

3. API: install, migrate, run (`localhost:8000`, docs at `/docs`):

   ```bash
   cd api
   uv sync
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload
   ```

4. Web: install and run (`localhost:5173`):

   ```bash
   cd web
   npm install
   npm run dev
   ```

### Common Commands

| Where | Command | What it does |
| --- | --- | --- |
| `api/` | `uv run pytest` | Run the test suite |
| `api/` | `uv run alembic revision --autogenerate -m "..."` | Create a migration from model changes (review it!) |
| `api/` | `uv run alembic check` | Verify models and database match |
| `web/` | `npm run gen:api` | Regenerate TypeScript types after API changes |
| `web/` | `npm run lint` / `npm run build` | Lint / type-check and build |

### Bank Sync (optional)

1. Create an application at [Enable Banking](https://enablebanking.com) (Sandbox to develop, Production
   in restricted mode for your own accounts). Redirect URL: `http://localhost:5173/connections/callback`.
2. Store the downloaded private key **outside the repo** and readable only by you:

   ```bash
   mkdir -p ~/.config/cream && chmod 700 ~/.config/cream
   mv ~/Downloads/<application-id>.pem ~/.config/cream/enablebanking-sandbox.pem
   chmod 600 ~/.config/cream/enablebanking-sandbox.pem
   ```

3. Set `CREAM_ENABLEBANKING_APP_ID` and `CREAM_ENABLEBANKING_KEY_PATH` (absolute path) in `.env`,
   restart the API, then use **Banks** in the app.

## Future Features

- Edit/delete wallets and transactions; transfers between wallets from the UI
- Scheduled background sync and consent renewal
- Greek translation
- CSV import for older history
- Budgets, recurring transactions, reports and charts
