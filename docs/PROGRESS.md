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
| 4 | Bank sync | "My bank transactions arrive in CREAM without typing them" | ✅ |
| 5 | Auto-categorization | "Imported transactions land in the right category" | ✅ |
| 6 | Manage records | "I can fix and remove wallets and transactions" | 🔜 (mostly done) |
| 7 | Transfers | "Moving money between my accounts isn't counted as spending" | 🔜 (in progress) |
| 8 | Always in sync | "Banks sync on their own and tell me when to reconnect" | ⬜ |
| 9 | Insights | "I can see where my money went this month" | ⬜ (net worth done) |
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
| Settings | Monarch's Settings page: menu of Account and Household sections, **Profile** editable (`PATCH /auth/me`), **Institutions** (the former Banks page, with Monarch's Edit Account dialog: name, balance, type, credit limit, invert balance, hide account, exclude balance, hide transactions, delete), **Categories** (groups with emoji, drag and drop to reorder, saved per user; Create/Edit Group with budget choice, Create Category with emoji picker and budget exclusion, delete); the other sections are marked coming soon |

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
| Web | Settings › Institutions (Monarch's layout): connect, callback, link to new/existing wallet, sync now with results, reconnect when access expires |
| Verified | Sandbox with Mock ASPSP (146 transactions imported, balance matches the bank) |
| Production | Enable Banking production app in restricted mode (only the owner's linked accounts), https dev server with a local mkcert certificate; Revolut, N26 and PayPal connected with real data |
| Later additions | First sync asks for the **longest** history the bank gives (Revolut: back to Oct 2024, 1,562 transactions); bank list from Enable Banking with CREAM's own catalog (websites, most popular in Greece first); PayPal's multi-currency account (`XXX`) kept in EUR; provider error reasons and a notice for banks that share no accounts |

### ✅ Slice 5: Auto-categorization

| Layer | Delivered |
| --- | --- |
| DB | `merchant_rules`; transactions gain `merchant_key` (normalized merchant) and `category_source` (`manual` / `rule` / `mcc` / `default`); backfill of existing imports |
| API | Import order: your merchant rule → MCC map (~1,100 codes, Plaid's taxonomy as a guide) → Uncategorized; every sync also retries transactions still waiting; `GET /transactions/uncategorized`, `POST /transactions/{id}/categorize` (optional rule + apply to similar), `GET/DELETE /rules` |
| Rules | Never override a category you picked by hand; one rule per merchant (case and spacing ignored) |
| Web | **Review** page (nav badge with the count): inbox with a quick picker and "Always use for …", merchant rules list; change any category from Recent transactions (✨ marks automatic ones); sync summary shows how many were categorized |
| Later additions | Monarch-style review: `needs_review` independent of the category, set on import by the user's preferences (`user_preferences`); "Needs review" view in Transactions, mark one or all reviewed, review status in bulk edit |
| Verified | Migration on PostgreSQL (upgrade, backfill, downgrade, `alembic check`); UI at desktop and phone widths |

---

## Next

### 🔜 Slice 6: Manage records (mostly done)

| Area | Delivered |
| --- | --- |
| Transactions | Hide and show (`is_hidden`: out of lists, the review inbox and statistics, still in the balance); bank imports can't be deleted, manual ones can (with confirmation); Transactions page grouped by day with category emoji, account logo and merchant logo columns; **bulk edit** (category, merchant: search or create, review status, hide) and bulk delete, confirmed before applying |
| Accounts | Monarch's Accounts page: accounts grouped by type with totals, net worth card and chart, **Summary** card (assets and liabilities by type); one **Add account** dialog in Monarch's steps (banks with search and most popular, Enable Banking consent screen, manual types with their own forms); Monarch's account types and subtypes (only those held in Greece); an account opens **Edit Account** (name, balance, type, credit limit, invert balance, hide, exclude, delete) |
| Categories | Settings › Categories like Monarch's: groups with emoji, drag and drop to reorder (saved per user), Create/Edit Group with budget choice, Create Category with emoji picker, delete (system ones hidden for the user only) |
| Merchants | `merchants` with **aliases** (every spelling that means the merchant); Settings › Merchants (sorted by count or name, searchable); **Edit merchant** (rename, website); **Merge & delete** (its transactions and aliases move to another merchant); a catalog of known merchants (efood, Wolt, Apple, Skroutz…) gathers the banks' spellings into one merchant on import and on every sync, leaving names the user chose alone (`named_by_user`); banks and PayPal only lend their logo; **logos** from Logo.dev through the API |
| Settings | Monarch's Settings page: Profile (editable), Institutions, Categories, Merchants; the rest marked coming soon |
| Currency | EUR only for now (ADR12), one place to open more |

Still to do: a transaction's **side panel** (›) to edit one transaction and see its details, and **Split**.

### 🔜 Slice 7: Transfers (in progress)

Only money moving between **your own** accounts is a transfer (left out of cash flow). Money sent to
someone else is an expense; money someone sends you is income, even when the bank calls it a transfer.

| Step | Status |
| --- | --- |
| **T1** Pair the two sides: −X in one account and +X in another, at most 3 days apart (closest wins); both go to Transfers › Transfer (`category_source: transfer`), each keeps the other (`transfer_pair_id`); same-day pairs listed together; a side without any text shows the other account's name | ✅ |
| **T2** A purchase through PayPal with a bank card counts once: the bank's "Paypal \*…" line is paired with PayPal's purchase (≤3 days, the bank's amount equal or up to 10% more for conversion and fees); the bank's line stays the purchase at what was really paid, PayPal's becomes a hidden transfer | ✅ |
| **T3** ATM withdrawals: Transfer, plus the money arriving in a manual **Cash** account (created when missing), where cash spending is entered by hand | 🔜 |
| **T4** Transactions in other currencies are imported (most likely why "Paypal \*a148246" has no EUR purchase on PayPal's side; it stays an expense on the bank's side meanwhile) | ⬜ |
| Record a transfer between two accounts by hand as one action | ⬜ |

## Planned

### ⬜ Slice 8: Always in sync

Scheduled background sync (respecting bank rate limits: about 4 unattended refreshes a day per account),
reconnect flow before consent expires. Production (restricted mode) with real accounts already works
(Slice 4); Piraeus Bank and Eurobank still fail on the bank's side.

### ⬜ Slice 9: Insights

Monthly income vs expenses (cash flow), spending by category with charts. Net worth (assets minus
liabilities, day by day) is already on the Accounts page. Cash flow leaves out own-account transfers and
hidden transactions. EUR only, so every total is a plain sum.

### ⬜ Slice 10: Greek

Greek UI and category names, using the stable category keys.

### ⬜ Slice 11: History import

CSV import for older history and for days when a bank connection is down.

### ⬜ Slice 12: Dashboard

App layout in the style of Monarch: sidebar navigation (in place, with the pages built so far; Cash Flow,
Reports, Budget, Recurring, Goals and Investments arrive with their features) and a dashboard of cards (budget, spending vs. last
period, net worth, recent transactions, recurring, goals, investments), each with its own period picker.
**Customize** button to choose and arrange the cards; **Settings** page. CREAM keeps its own name and logo.
Cards arrive with their features (e.g. net worth and spending in Slice 9).

---

## Later

Ideas agreed on but not scheduled into a slice yet.

- **More currencies:** CREAM is EUR-only for now (as Monarch keeps to one currency). Opening others means
  adding them to `services/currencies.py`, then per-currency statistics and a net worth converted with
  exchange rates. Accounts created earlier in other currencies still work and show their own totals.
- **Rules that set the review status** (Monarch's "Then set review status"), with the rules editor.
- **Rules editor like Monarch's:** conditions on the merchant or the bank's original text, actions such as
  **Rename merchant** and set category, applied to existing transactions too.
- **Add transaction** with Monarch's merchant field ("Create new … merchant").
- **Edit merchant:** Choose photo / Remove (logos uploaded by the user); recurring merchants.
- **Accounts page:** drag and drop to rearrange the cards.
- **Investments:** Freedom24 (its own API), SnapTrade (IBKR, Degiro, eToro, Trading 212, crypto exchanges),
  CSV import (e.g. Revolut investments, which no aggregator reaches).

---

## Known Gaps

- `/statistics` sums amounts across currencies; only matters for accounts created before CREAM went EUR-only
- No session refresh: sessions end after `CREAM_ACCESS_TOKEN_EXPIRE_MINUTES`
- Tests run on SQLite; Postgres-specific behavior (e.g. NUMERIC precision) is not covered by tests
- HTTPS and deployment configuration not set up yet
- MCC can't tell coffee shops from fast food (both 5814): rules fix it after the first choice
- Merchant rules match the bank's counterparty, or its text when there is none; texts with one-off details
  (card numbers, dates) never repeat, so "Always use for" starts unticked for them
- Banks limit unattended refreshes (PSD2: about 4 a day per account); more give `429 Too many requests`
  until the next day
- Banks give only a booking date, no time: same-day transactions list in import order (transfer pairs
  aside); two banks may book the two sides of a transfer on different days
- Transfers are matched by amount and date only: a payment to someone else on the same day as an equal
  income from someone else in another account would pair wrongly (the user can change the category)
- Unknown shops paid through PayPal keep the bank's text (e.g. "Paypal \*onlinedeliv") until merged or
  renamed by hand, even when paired with PayPal's purchase, which names the shop
- Refunds through PayPal aren't paired yet: PayPal's refund and the bank's money back both count

## Requirements Coverage

| Area | Status | Notes |
| --- | --- | --- |
| FR1 Users | ✅ | Signup, login, logout, `/me`, data isolation |
| FR2 Wallets | ✅ | CRUD in API and UI (Accounts page, Add account, Edit Account) |
| FR3 Categories | ✅ | System defaults + own categories, hierarchy, cycle detection; auto-categorization (rules, MCC) |
| FR4 Transactions | ✅ | CRUD in API; bulk edit, hide and delete in UI; one-transaction side panel pending |
| FR5 Statistics | ✅ | Net worth over time; cash flow pending (Slice 9) |
| FR6 Reports | ✅ (API) | Reports UI comes in Slice 9 |
| VR1–VR4 Validation | ✅ | Amounts, dates, names, currencies, users |
| NFR1 Correctness | ✅ | NUMERIC(19,4), no floats anywhere (API or web) |
| NFR3 Security | ✅ | Cookie sessions, bcrypt, ownership checks, PSD2 key outside repo; HTTPS pending |
| NFR4–NFR6 | ✅ | Timestamps, error handling, migrations, test suite (see [TESTING.md](TESTING.md)) |
