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
- A web app laid out like Monarch Money: sidebar, Accounts, Transactions, Review and Settings
- Accounts (bank, cash, investments, real estate, vehicles, loans…) with Monarch's types, net worth over
  time and a summary of assets and liabilities; EUR only for now
- Transactions grouped by day, with Monarch's default categories; bulk edit, hide, delete (manual ones)
- Bank sync (Enable Banking, read-only PSD2): connect a bank, link its accounts, import booked transactions
  without duplicates, as far back as the bank allows
- Auto-categorization: merchant rules learned from your choices, then the bank's merchant category code
  (MCC); new transactions wait in a **Review** inbox, as your preferences say
- Merchants: clean names for known merchants (efood, Wolt, Apple…), logos, rename, Merge & delete
- Transfers between your own accounts are found and left out of cash flow
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
│   │   └── services/   # Business logic (banking/ = Enable Banking; categorization/ = MCC map, rules, transfers)
│   ├── migrations/     # Alembic migrations
│   ├── scripts/        # export_openapi.py (feeds the web type generator)
│   └── tests/          # pytest suite
└── web/                # React / TypeScript / Vite
    └── src/
        ├── lib/        # API client + generated types, query client, money/date/amount helpers
        ├── components/ # Shared UI (shadcn/ui in components/ui)
        ├── features/   # auth, profile, wallets, transactions, categories, categorization, merchants, bank, health
        └── routes/     # Pages, layout, guards, router
```

## Database

> **Source of truth:** the SQLAlchemy models in `api/app/models/`. Schema changes go through Alembic
> migrations in `api/migrations/`, never by hand.

```text
users ──1:N── wallets ──1:N── transactions ──N:1── categories (groups → categories, system + own)
  │              ▲               │  └── transfer pair (another transaction)
  │              │               └──N:1── merchants ──1:N── merchant_aliases
  ├──1:N── bank_connections ──1:N── bank_accounts ──(links to one wallet)
  ├──1:N── merchant_rules ──N:1── categories
  └──1:1── user_preferences; category_positions / category_overrides (per-user order and hiding)
```

| Table | Purpose |
| ------- | --------- |
| users | Accounts and login |
| wallets | Bank accounts, cash, digital wallets, stashes |
| categories | System default groups/categories (stable `key`) and user categories |
| transactions | Money in/out; imported ones carry `external_id`, counterparty, MCC and `merchant_key`; `category_source` says who chose the category; `transfer_pair_id` links the two sides of a transfer |
| category_positions, category_overrides | The user's order of categories, and their changes to system ones (name, budget, hidden) |
| merchants, merchant_aliases | Who the money went to, and every name that means them (banks' spellings, the user's names) |
| merchant_rules | "This merchant always goes to this category", one per merchant per user |
| user_preferences | How the app behaves for the user (e.g. which new transactions need review) |
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

### Merchant Logos (optional)

Create a free account at [Logo.dev](https://www.logo.dev) and set its publishable key in `.env`:
`CREAM_LOGO_DEV_TOKEN=pk_…`. Without it, merchants show their initial.

### Bank Sync (optional)

1. Create an application at [Enable Banking](https://enablebanking.com) (Sandbox to develop, Production
   in restricted mode for your own accounts). Redirect URL: `http://localhost:5173/connections/callback`
   for Sandbox; Production only accepts https, so `https://localhost:5173/connections/callback`.
   Activate a Production app with **Activate by linking accounts** (it can then read only those accounts).
2. Store the downloaded private key **outside the repo** and readable only by you:

   ```bash
   mkdir -p ~/.config/cream && chmod 700 ~/.config/cream
   mv ~/Downloads/<application-id>.pem ~/.config/cream/enablebanking-sandbox.pem
   chmod 600 ~/.config/cream/enablebanking-sandbox.pem
   ```

3. Set `CREAM_ENABLEBANKING_APP_ID` and `CREAM_ENABLEBANKING_KEY_PATH` (absolute path) in `.env`,
   restart the API, then use **Settings › Institutions** in the app.
4. Production only: serve the web app over https with a locally trusted certificate
   ([mkcert](https://github.com/FiloSottile/mkcert)). Vite switches to https when `web/.cert/` has one
   (git-ignored):

   ```bash
   mkcert -install
   mkdir -p web/.cert && mkcert -cert-file web/.cert/localhost.pem -key-file web/.cert/localhost-key.pem localhost
   ```

   and set `CREAM_ENABLEBANKING_REDIRECT_URL=https://localhost:5173/connections/callback` in `.env`.

## Future Features

- A transaction's side panel, Split, and a rules editor like Monarch's (e.g. rename merchant)
- ATM withdrawals into a Cash account; transactions in other currencies
- Scheduled background sync and consent renewal
- Investments (Freedom24, SnapTrade, CSV)
- Greek translation
- CSV import for older history
- Budgets, recurring transactions, reports and charts
