# Implementation Progress

> **Legend:** ✅ Implemented  ·  ⬜ Not Implemented

---

## Backend API

### ✅ User Management (FR1)

- ✅ User registration with username, email, password
- ✅ User login with JWT in httpOnly session cookie
- ✅ Logout (clears session cookie)
- ✅ Current user endpoint (`/auth/me`)
- ✅ Token-based authentication on all endpoints
- ✅ User data isolation (users can only access own data)
- ✅ Unique username and email validation
- ✅ Username length validation (3-50 chars)
- ✅ Password minimum length validation (8 chars)

### ✅ Wallet Management (FR2)

- ✅ Create wallet with name, type, currency, initial balance
- ✅ List all user wallets
- ✅ Get wallet details with current balance
- ✅ Update wallet (name, type, currency)
- ✅ Delete wallet (cascades to transactions)
- ✅ Wallet types: bank, cash, digital, stash
- ✅ Balance calculation: initial_balance + sum(transactions)
- ✅ Currency validation (ISO 4217 format, normalized to uppercase)
- ✅ Currency locked once a wallet has transactions (409)
- ✅ Totals per currency (`/wallets/totals`), never mixed
- ✅ Wallet name validation (1-100 chars)

### ✅ Category Management (FR3)

- ✅ Create custom categories (name, type)
- ✅ List categories (personal + system defaults)
- ✅ Update own categories
- ✅ Delete own categories
- ✅ System default categories protection
- ✅ Hierarchical categories (parent_id)
- ✅ Cycle detection in category hierarchy
- ✅ Default categories (Monarch's set) seeded as groups + categories with stable keys
- ✅ Transfer category type, excluded from income/expense statistics
- ✅ Subcategory type must match its parent; groups can't hold transactions

### ✅ Transaction Management (FR4)

- ✅ Create transactions (wallet, category, amount, date, description)
- ✅ List transactions newest first, with pagination (limit/offset)
- ✅ Filter transactions by wallet
- ✅ Get transaction details
- ✅ Update transactions
- ✅ Delete transactions
- ✅ Positive = income, negative = expense
- ✅ Wallet ownership validation
- ✅ Category access validation

### ✅ Statistics (FR5)

- ✅ Total balance across all wallets
- ✅ Total income (sum of positive transactions)
- ✅ Total expenses (sum of negative transactions)
- ✅ Balance per wallet
- ✅ Spending breakdown by category
- ✅ Income breakdown by category

### ✅ Reports (FR6)

- ✅ Generate reports for date range
- ✅ Period income, expenses, net change
- ✅ Transaction count for period
- ✅ Category breakdown with totals and counts
- ✅ Wallet breakdown with income/expense/net

---

## Validation Rules

### ✅ Transaction Validation (VR1)

- ✅ Amount must not be zero
- ✅ Amount >= 0.0001 (minimum precision)
- ✅ Amount <= 999,999,999.9999 (maximum)
- ✅ `occurred_at` must not be in the future
- ✅ `wallet_id` must exist and be owned by user
- ✅ `category_id` must be accessible

### ✅ Wallet Validation (VR2)

- ✅ Name must not be empty
- ✅ Name <= 100 characters
- ✅ Type must be valid enum
- ✅ Currency must be a 3-letter code (`eur` → `EUR`)

### ✅ Category Validation (VR3)

- ✅ Name must not be empty
- ✅ Name <= 100 characters
- ✅ Type must be income or expense
- ✅ parent_id must not create cycle

### ✅ User Validation (VR4)

- ✅ Username 3-50 characters
- ✅ Email valid format
- ✅ Password minimum 8 characters

---

## Non-Functional Requirements

### ✅ Correctness (NFR1)

- ✅ Fixed-point decimal arithmetic (NUMERIC(19,4))
- ✅ 4 decimal places precision
- ✅ No floating-point in financial calculations
- ✅ ACID-compliant transactions
- ✅ Consistent balance calculations
- ✅ Input validation before persistence

### ✅ Security (NFR3)

- ✅ Bcrypt password hashing
- ✅ JWT tokens with expiration
- ✅ Authentication required on all endpoints
- ✅ User data isolation
- ✅ Input validation (Pydantic + business rules)
- ✅ SQL injection prevention (ORM)
- ⬜ HTTPS in production (deployment config)

### ✅ Auditability (NFR4)

- ✅ `created_at` on all entities
- ✅ `updated_at` on mutable entities
- ✅ `occurred_at` preserved on transactions
- ✅ Hard deletes (no soft deletes)

### ✅ Reliability (NFR5)

- ✅ Database error handling
- ✅ Appropriate error messages
- ✅ Session rollback on errors
- ✅ Health check endpoint

### ✅ Maintainability (NFR6)

- ✅ pytest suite (see TESTING.md)
- ✅ API versioning (v1)
- ✅ Alembic migrations
- ✅ Environment variable configuration

---

## Frontend

### ✅ Project Setup

- ✅ Vite + React + TypeScript
- ✅ Tailwind CSS + shadcn/ui
- ✅ React Router + TanStack Query
- ✅ Feature-based structure (lib, components, features, routes)
- ✅ TypeScript types generated from OpenAPI schema (`npm run gen:api`)
- ✅ Vite dev proxy to API
- ✅ System status page (walking skeleton: web → API → DB)

### ⬜ Core Infrastructure

- ✅ API client service (typed, openapi-fetch)
- ✅ Current user query (`useCurrentUser`)
- ✅ Protected routes (redirect to login and back)
- ✅ Expired session (any 401) returns to login

### ⬜ User Interface

- ✅ Authentication pages (login, signup, logout)
- ⬜ Dashboard with statistics
- ✅ Wallet list with balances and totals per currency
- ✅ Add wallet dialog
- ⬜ Edit and delete wallets
- ✅ Add transaction (expense/income) and recent transactions
- ⬜ Edit and delete transactions
- ⬜ Category management UI
- ⬜ Reports and charts

---

## Future Features (Post-MVP)

### ⬜ Recurring Transactions

- ⬜ Define recurring transaction templates
- ⬜ Automatic transaction generation
- ⬜ Edit/delete recurring rules

### ⬜ Budget Planning

- ⬜ Set spending limits per category
- ⬜ Budget vs actual tracking
- ⬜ Alerts when approaching limits

### ✅ Bank Sync (Enable Banking)

- ✅ Connect a bank (PSD2 consent, single-use state)
- ✅ Link bank accounts to new or existing wallets
- ✅ Manual sync: booked transactions only, no duplicates, balance matches the bank
- ✅ Disconnect (revokes consent, keeps data)
- ⬜ Scheduled background sync
- ⬜ Reconnect flow for expired consent
- ⬜ Production (restricted mode) with real accounts

### ⬜ Multi-Currency

- ⬜ Currency conversion rates
- ⬜ Cross-currency reporting
- ⬜ Base currency setting

### ⬜ Data Import/Export

- ⬜ CSV export
- ⬜ JSON export
- ⬜ CSV import with mapping

### ⬜ Tags

- ⬜ Tag transactions with labels
- ⬜ Filter by tags
- ⬜ Tag-based reporting

### ⬜ Receipt Attachments

- ⬜ Upload receipt images
- ⬜ Link to transactions
- ⬜ Image storage

---

## Summary

| Component | Status |
| ----------- | -------- |
| Backend API | ✅ Complete |
| Validation | ✅ Complete |
| Non-Functional | ✅ Complete |
| Frontend Setup | ✅ Complete |
| Frontend Infrastructure | ⬜ In Progress |
| Frontend UI | ⬜ Not Started |
| Future Features | ⬜ Post-MVP |
