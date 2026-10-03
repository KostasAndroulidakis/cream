# Implementation Progress

CREAM is built in **vertical slices**: each slice delivers one thing a user can do, end to end
(database → API → web), and is usable on its own when it ships.

> **Legend:** ✅ Done · 🔜 Next · ⬜ Planned

## Overview

| # | Slice | User outcome | Status |
| --- | --- | --- | --- |
| 0 | Walking skeleton | "I can see that the app, API and database are connected" | ✅ |
| 1 | Accounts | "I can sign up, log in and log out securely" | ✅ |
| 2 | Wallets | "I can see my wallets, their balances and my totals per currency" | ✅ |
| 3 | Transactions | "I can record an expense or income in seconds" | ✅ |
| 4 | Bank sync | "My bank transactions arrive in CREAM without typing them" | ✅ (Sandbox) |
| 5 | Auto-categorization | "Imported transactions land in the right category" | ✅ |
| 6 | Manage records | "I can fix and remove wallets and transactions" | 🔜 |
| 7 | Transfers | "Moving money between my accounts isn't counted as spending" | ⬜ |
| 8 | Always in sync | "Banks sync on their own and tell me when to reconnect" | ⬜ |
| 9 | Insights | "I can see where my money went this month" | ⬜ |
| 10 | Greek | "I can use CREAM in Greek" | ⬜ |
| 11 | History import | "My older history is in CREAM too (CSV)" | ⬜ |
| 12 | Dashboard | "My home page shows what I care about, the way I like it" | ⬜ |

---

## Done

### ✅ Slice 0: Walking skeleton

| Layer | Delivered |
| --- | --- |
| Infra | PostgreSQL via Docker Compose; shared root `.env` (single source for credentials) |
| DB | Alembic baseline migration: tz-aware timestamps, enums stored by value, indexes |
| API | `GET /api/v1/health` (API + database), typed response |
| Web | Vite + React + TS, Tailwind + shadcn/ui, TanStack Query, dev proxy, OpenAPI type generation, system status card |

### ✅ Slice 1: Accounts

| Layer | Delivered |
| --- | --- |
| API | Signup, login, logout, `/auth/me`; JWT in `httpOnly` / `Secure` / `SameSite=Strict` cookie; bcrypt |
| Web | Login and signup pages with validation, protected routes with return-to, logout, expired session → login |

### ✅ Slice 2: Wallets

| Layer | Delivered |
| --- | --- |
| API | ISO currency codes (normalized), currency locked once transactions exist, `/wallets/totals` per currency |
| Web | Wallet list with balances, headline totals per currency, add-wallet dialog, exact decimal formatting |

### ✅ Slice 3: Transactions

| Layer | Delivered |
| --- | --- |
| DB | Monarch's default categories (15 groups, 60 categories) with stable keys; `transfer` category type |
| API | Transfers excluded from income/expense stats; groups not assignable; parent/child type rule; pagination |
| Web | Add-transaction dialog (expense/income, grouped categories, decimal comma), recent transactions |

### ✅ Slice 4: Bank sync (Enable Banking)

| Layer | Delivered |
| --- | --- |
| DB | `bank_connections`, `bank_accounts`; transactions gain `external_id`, `counterparty`, MCC |
| API | Connect (single-use state), link accounts to wallets, manual sync of booked transactions, duplicate-safe IDs, first-sync balance reconciliation, disconnect |
| Web | Banks page: connect, callback, link to new/existing wallet, sync now with results |
| Verified | Sandbox with Mock ASPSP (146 transactions imported, balance matches the bank) |

### ✅ Slice 5: Auto-categorization

| Layer | Delivered |
| --- | --- |
| DB | `merchant_rules`; transactions gain `merchant_key` (normalized merchant) and `category_source` (`manual` / `rule` / `mcc` / `default`); backfill of existing imports |
| API | Import order: your merchant rule → MCC map (~1,100 codes, Plaid's taxonomy as a guide) → Uncategorized; every sync also retries transactions still waiting; `GET /transactions/uncategorized`, `POST /transactions/{id}/categorize` (optional rule + apply to similar), `GET/DELETE /rules` |
| Rules | Never override a category you picked by hand; one rule per merchant (case and spacing ignored) |
| Web | **Review** page (nav badge with the count): inbox with a quick picker and "Always use for …", merchant rules list; change any category from Recent transactions (✨ marks automatic ones); sync summary shows how many were categorized |
| Verified | Migration on PostgreSQL (upgrade, backfill, downgrade, `alembic check`); UI at desktop and phone widths |

---

## Next

### 🔜 Slice 6: Manage records

Edit and delete wallets and transactions; hide default categories you don't use.

Done so far (API): bank transactions can't be deleted; transactions can be hidden (`is_hidden`): left out
of lists, the review inbox and statistics, still part of the wallet balance.

## Planned

### ⬜ Slice 7: Transfers

Record a transfer between two wallets as one action; detect and pair matching in/out bank transactions.
Only money moving between **your own** wallets is a `transfer` (left out of cash flow). Money sent to
someone else is an expense; money someone sends you is income, even when the bank calls it a transfer.

### ⬜ Slice 8: Always in sync

Scheduled background sync (respecting bank rate limits), reconnect flow before consent expires,
Production (restricted mode) with real accounts, starting with the most stable banks (Revolut, N26).

### ⬜ Slice 9: Insights

Monthly income vs expenses (cash flow), spending by category with charts, per-currency statistics.
Cash flow leaves out own-wallet transfers and hidden transactions.
Net worth in one currency: totals converted with exchange rates, next to the exact per-currency totals.

### ⬜ Slice 10: Greek

Greek UI and category names, using the stable category keys.

### ⬜ Slice 11: History import

CSV import for older history and for days when a bank connection is down.

### ⬜ Slice 12: Dashboard

App layout in the style of Monarch: sidebar navigation (Dashboard, Accounts, Transactions, Cash Flow,
Reports, Budget, Recurring, Goals, Investments) and a dashboard of cards (budget, spending vs. last
period, net worth, recent transactions, recurring, goals, investments), each with its own period picker.
**Customize** button to choose and arrange the cards; **Settings** page. CREAM keeps its own name and logo.
Cards arrive with their features (e.g. net worth and spending in Slice 9).

---

## Later

Ideas agreed on but not scheduled into a slice yet.

- **Transaction review like Monarch's:** a separate "needs review / reviewed" flag, independent of the
  category, settable by hand or by rules. Hiding a transaction would then keep its review status. Today the
  review inbox simply means "Uncategorized", and hiding a transaction takes it out of the inbox.

---

## Known Gaps

- `/statistics` still sums amounts across currencies (`/wallets/totals` is correct); fixed in Slice 9
- No session refresh: sessions end after `CREAM_ACCESS_TOKEN_EXPIRE_MINUTES`
- Tests run on SQLite; Postgres-specific behavior (e.g. NUMERIC precision) is not covered by tests
- HTTPS and deployment configuration not set up yet
- MCC can't tell coffee shops from fast food (both 5814): rules fix it after the first choice
- Merchant rules match the bank's counterparty, or its text when there is none; texts with one-off details
  (card numbers, dates) never repeat, so "Always use for" starts unticked for them

## Requirements Coverage

| Area | Status | Notes |
| --- | --- | --- |
| FR1 Users | ✅ | Signup, login, logout, `/me`, data isolation |
| FR2 Wallets | ✅ | CRUD in API; edit/delete in UI comes in Slice 6 |
| FR3 Categories | ✅ | System defaults + own categories, hierarchy, cycle detection; auto-categorization (rules, MCC) |
| FR4 Transactions | ✅ | CRUD in API; edit/delete in UI comes in Slice 6 |
| FR5 Statistics | ✅ | Per-currency statistics pending (Slice 9) |
| FR6 Reports | ✅ (API) | Reports UI comes in Slice 9 |
| VR1–VR4 Validation | ✅ | Amounts, dates, names, currencies, users |
| NFR1 Correctness | ✅ | NUMERIC(19,4), no floats anywhere (API or web) |
| NFR3 Security | ✅ | Cookie sessions, bcrypt, ownership checks, PSD2 key outside repo; HTTPS pending |
| NFR4–NFR6 | ✅ | Timestamps, error handling, migrations, test suite (see [TESTING.md](TESTING.md)) |
