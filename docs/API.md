# CREAM API Specification

## Overview

- **Base URL**: `/api/v1`
- **Format**: JSON
- **Authentication**: JWT in an `httpOnly` session cookie
- **Versioning**: URL path (`/api/v1`, `/api/v2`, etc.)

## Authentication Requirement

All endpoints except `/health`, `/auth/signup`, `/auth/login` and `/auth/logout` require authentication.

## API Endpoints

| Endpoint | Description |
| --- | --- |
| `POST /api/v1/auth/signup` | User registration |
| `GET /api/v1/health` | API and database availability (public) |
| `POST /api/v1/auth/login` | User login (sets session cookie) |
| `POST /api/v1/auth/logout` | End session (clears cookie) |
| `GET /api/v1/auth/me` | Current authenticated user |
| `PATCH /api/v1/auth/me` | Change own profile: names, display name, birthday, timezone (Settings › Profile) |
| `GET /api/v1/wallets` | List user wallets |
| `POST /api/v1/wallets` | Create wallet |
| `GET /api/v1/wallets/totals` | Combined balance per currency |
| `GET /api/v1/wallets/summary` | Net worth and each account type's total |
| `GET /api/v1/wallets/{id}` | Get wallet |
| `PATCH /api/v1/wallets/{id}` | Edit Account: name, type/subtype, `balance` (the starting balance absorbs the difference), `credit_limit`, `invert_balance` (flips the sign), `is_hidden`, `exclude_balance`, `hide_transactions` |
| `DELETE /api/v1/wallets/{id}` | Delete wallet |
| `GET /api/v1/categories` | List categories (in the user's order within each group) |
| `PUT /api/v1/categories/order` | Reorder one group's categories: `{category_ids}` lists all of them, once (204) |
| `POST /api/v1/categories` | Create category, or group (`is_group`, `budget_by`); `icon`, `exclude_from_budget` |
| `GET /api/v1/categories/{id}` | Get category |
| `PATCH /api/v1/categories/{id}` | Update category; on a system one only `name` and `budget_by`, for this user only |
| `DELETE /api/v1/categories/{id}` | Delete category, or group with its categories (409 while they hold transactions); system ones are hidden for this user only |
| `GET /api/v1/transactions` | List transactions |
| `POST /api/v1/transactions` | Create transaction |
| `GET /api/v1/transactions/needs-review` | Review inbox: transactions that need review |
| `POST /api/v1/transactions/needs-review/mark-all-reviewed` | Mark every transaction in the inbox reviewed |
| `POST /api/v1/transactions/bulk-update` | Same changes on several transactions (all or none) |
| `POST /api/v1/transactions/bulk-delete` | Delete several transactions entered by hand (all or none) |
| `GET /api/v1/transactions/{id}` | Get transaction |
| `PATCH /api/v1/transactions/{id}` | Update transaction |
| `POST /api/v1/transactions/{id}/categorize` | Set the category, optionally as a merchant rule |
| `DELETE /api/v1/transactions/{id}` | Delete transaction |
| `GET /api/v1/rules` | List merchant rules |
| `DELETE /api/v1/rules/{id}` | Delete a merchant rule |
| `GET /api/v1/merchants` | List merchants |
| `GET /api/v1/statistics` | Aggregated statistics |
| `GET /api/v1/statistics/report` | Period reports |

### Session Cookie

Login sets the JWT as a cookie; the browser sends it automatically. JavaScript never sees the token.

```text
Set-Cookie: cream_session=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/api; Max-Age=1800
```

- `HttpOnly`: not readable from JavaScript (XSS cannot steal it)
- `SameSite=Strict` + JSON-only bodies: not sent on cross-site requests (CSRF protection)
- `Path=/api`: only sent to API routes
- Name configurable via `CREAM_AUTH_COOKIE_NAME`; `Secure` via `CREAM_AUTH_COOKIE_SECURE`
- `Authorization: Bearer` headers are **not** accepted

### Token Structure

```json
{
  "sub": "user_id",
  "exp": 1234567890
}
```

### Token Expiration

- Default: 30 minutes
- Configurable via `CREAM_ACCESS_TOKEN_EXPIRE_MINUTES`

---

## Endpoints

### Authentication

#### POST /auth/signup

Create a new user account.

**Request**:

```json
{
  "username": "string (3-50 chars)",
  "email": "string (valid email)",
  "password": "string (min 8 chars)",
  "first_name": "string",
  "last_name": "string"
}
```

**Response** `201 Created`:

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

- `400`: Username already exists
- `400`: Email already exists
- `422`: Validation error

#### POST /auth/login

Verify credentials and start a session.

**Request**:

```json
{
  "username": "string",
  "password": "string"
}
```

**Response** `200 OK`: the user (same shape as signup), plus the `Set-Cookie` header above.

**Errors**:

- `401`: Invalid credentials

#### POST /auth/logout

Clear the session cookie. Always succeeds.

**Response** `204 No Content`

#### GET /auth/me

Return the authenticated user (same shape as signup).

**Errors**:

- `401`: Not authenticated

---

### Wallets

#### GET /wallets

List all wallets for the authenticated user.

**Response** `200 OK`:

```json
[
  {
    "id": 1,
    "name": "Main Bank",
    "type": "cash",
    "subtype": "checking",
    "currency": "EUR",
    "initial_balance": "1000.0000",
    "balance": "1250.5000",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
]
```

#### POST /wallets

Create a new wallet.

**Request**:

```json
{
  "name": "string (max 100 chars)",
  "type": "cash | investment | real_estate | vehicle | valuables | other_asset | credit_card | mortgage | loan | other_liability (default: cash)",
  "subtype": "string, one of the type's subtypes (default: the type's first)",
  "currency": "EUR (the only currency for now, and the default)",
  "initial_balance": "string (decimal, default: 0)"
}
```

**Response** `201 Created`:

```json
{
  "id": 1,
  "name": "Main Bank",
  "type": "cash",
  "subtype": "checking",
  "currency": "EUR",
  "initial_balance": "1000.0000",
  "balance": "1000.0000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

- `422`: Validation error, or a subtype that isn't one of the type's

#### GET /wallets/types

What an account can be, as in Monarch: the types (each an asset or a liability) and their subtypes, in Monarch's
order. The first subtype is the one a new account gets when none is given.

**Response** `200 OK`:

```json
[
  {
    "type": "cash",
    "label": "Cash",
    "account_class": "asset",
    "subtypes": [{ "key": "cd", "label": "CD" }, { "key": "checking", "label": "Checking" }]
  }
]
```

#### GET /wallets/summary

The Accounts page's numbers: net worth and each account type's total, counted by one rule (accounts set to
"Exclude account balance" count in neither). `types` lists only the types the user has accounts of, in
Monarch's order; liabilities carry their sign (debt is negative), so net worth is the plain sum.

**Response** `200 OK`:

```json
{
  "net_worth": [{ "currency": "EUR", "balance": "8800.5000", "wallet_count": 4 }],
  "types": [
    { "type": "cash", "account_class": "asset", "totals": [{ "currency": "EUR", "balance": "1250.5000", "wallet_count": 2 }] },
    { "type": "credit_card", "account_class": "liability", "totals": [{ "currency": "EUR", "balance": "-450.0000", "wallet_count": 1 }] }
  ]
}
```

#### GET /wallets/totals

Combined balance of the user's wallets, one entry per currency. Currencies are never converted or mixed.

**Response** `200 OK`:

```json
[
  { "currency": "EUR", "balance": "1450.5000", "wallet_count": 2 },
  { "currency": "USD", "balance": "300.0000", "wallet_count": 1 }
]
```

#### GET /wallets/{id}

Get a specific wallet.

**Response** `200 OK`:

```json
{
  "id": 1,
  "name": "Main Bank",
  "type": "cash",
  "subtype": "checking",
  "currency": "EUR",
  "initial_balance": "1000.0000",
  "balance": "1250.5000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

- `404`: Account not found (the wallet doesn't exist)
- `403`: Access denied (not owner)

#### PATCH /wallets/{id}

Update a wallet.

**Request** (all fields optional):

```json
{
  "name": "string",
  "type": "see POST /wallets",
  "subtype": "string",
  "currency": "string"
}
```

**Response** `200 OK`: Updated wallet object. A new `type` without a `subtype` starts at the type's first
subtype; a `subtype` alone must be one of the current type's (`422` otherwise).

**Errors**:

- `404`: Account not found (the wallet doesn't exist)
- `403`: Access denied
- `409`: Currency change on a wallet that already has transactions
- `422`: Validation error

#### DELETE /wallets/{id}

Delete a wallet and all its transactions.

**Response** `204 No Content`

**Errors**:

- `404`: Account not found (the wallet doesn't exist)
- `403`: Access denied

---

### Categories

#### GET /categories

List all accessible categories (user's + system defaults).

**Response** `200 OK`:

```json
[
  {
    "id": 1,
    "name": "Food & Dining",
    "type": "expense",
    "parent_id": null,
    "key": "group.food_and_dining",
    "is_group": true,
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Groceries",
    "type": "expense",
    "parent_id": 1,
    "key": "food_and_dining.groceries",
    "is_group": false,
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

#### POST /categories

Create a new category.

**Request**:

```json
{
  "name": "string (max 100 chars)",
  "type": "income | expense | transfer",
  "parent_id": "integer | null (optional, same type as the parent)"
}
```

**Response** `201 Created`:

```json
{
  "id": 3,
  "name": "Restaurants",
  "type": "expense",
  "parent_id": 1,
  "key": null,
  "is_group": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

- `400`: Type doesn't match the parent's type
- `422`: Validation error

#### GET /categories/{id}

Get a specific category.

**Response** `200 OK`: Category object

**Errors**:

- `404`: Category not found
- `403`: Access denied (other user's private category)

#### PATCH /categories/{id}

Update a category (user-owned only).

**Request** (all fields optional):

```json
{
  "name": "string",
  "parent_id": "integer | null"
}
```

**Response** `200 OK`: Updated category object

**Errors**:

- `404`: Category not found
- `403`: Cannot modify system default category
- `403`: Access denied
- `422`: Validation error

#### DELETE /categories/{id}

Delete a category (user-owned only).

**Response** `204 No Content`

**Errors**:

- `404`: Category not found
- `403`: Cannot modify system default category
- `403`: Access denied

---

### Transactions

#### GET /transactions

List transactions for the user's wallets, newest first.

**Query Parameters**:

- `wallet_id` (optional): Filter by wallet
- `include_hidden` (optional, default `false`): Also list hidden transactions
- `limit` (optional, default 50, max 200): Page size
- `offset` (optional, default 0): Items to skip

**Response** `200 OK`:

```json
[
  {
    "id": 1,
    "wallet_id": 1,
    "category_id": 2,
    "category_source": "mcc",
    "amount": "-45.5000",
    "description": "Card payment",
    "occurred_at": "2025-01-15T12:00:00Z",
    "counterparty": "SKLAVENITIS",
    "merchant_category_code": "5411",
    "merchant_key": "sklavenitis",
    "merchant": { "id": 4, "name": "SKLAVENITIS" },
    "is_imported": true,
    "is_hidden": false,
    "created_at": "2025-01-15T14:35:00Z"
  }
]
```

`category_source` says who chose the category: `manual` (the user), `rule` (a merchant rule), `mcc` (the
bank's merchant category code) or `default` (nothing matched; left in Uncategorized). Automatic
categorization never changes a `manual` category. `merchant_key` is the normalized merchant of an imported
transaction (counterparty, else its text; case and spacing ignored), or `null` when there is none.
`merchant` is who the money went to or came from, as the user sees it: imported transactions start with
the bank's merchant; `null` when unknown (e.g. manual entries).
A hidden transaction (`is_hidden`) still counts in its wallet's balance, but is left out of lists, the
review inbox and statistics.

**Errors**:

- `403`: Access denied (filtering by other user's wallet)

#### POST /transactions

Create a new transaction.

**Request**:

```json
{
  "wallet_id": "integer",
  "category_id": "integer",
  "amount": "string (decimal, non-zero)",
  "description": "string | null (optional)",
  "occurred_at": "string (ISO 8601 datetime)"
}
```

**Response** `201 Created`:

```json
{
  "id": 1,
  "wallet_id": 1,
  "category_id": 2,
  "amount": "-45.5000",
  "description": "Weekly groceries",
  "occurred_at": "2025-01-15T14:30:00Z",
  "created_at": "2025-01-15T14:35:00Z",
  "updated_at": "2025-01-15T14:35:00Z"
}
```

**Errors**:

- `404`: Account not found (the wallet doesn't exist)
- `403`: Access denied (not owner of wallet)
- `422`: Validation error (amount zero, future date, category is a group, etc.)

#### GET /transactions/needs-review

The review inbox: the user's transactions with `needs_review`, newest first. Bank imports get it from the
user's preferences (by default, those that found no category); the user sets or clears it with
`PATCH /transactions/{id}` or `bulk-update`. Choosing a category doesn't clear it.

**Query Parameters**: `limit` (default 50, max 200), `offset` (default 0)

**Response** `200 OK`:

```json
{ "total": 12, "items": [ /* transaction objects */ ] }
```

`total` counts every transaction that needs review, not just this page. Hidden transactions are left out
but keep their status: shown again, they are back in the inbox.

#### POST /transactions/needs-review/mark-all-reviewed

Mark every transaction in the review inbox reviewed ("Mark all N as reviewed").

**Response** `200 OK`: `{ "affected": 6 }`. Hidden transactions aren't in the inbox, so they keep their status.

#### POST /transactions/bulk-update

Apply the same changes to up to 500 transactions. Every change is checked on every transaction first: if any
is refused, none is applied.

**Request** (`changes` needs at least one field; a field left out means "no change"):

```json
{
  "transaction_ids": [12, 15, 19],
  "changes": {
    "category_id": 7,
    "occurred_at": "2026-09-01T12:00:00Z",
    "description": "string | null (null clears the notes)",
    "is_hidden": true,
    "needs_review": false,
    "merchant_name": "Corner Shop"
  }
}
```

**Response** `200 OK`: `{ "affected": 3 }` (an ID sent twice counts once). A new category becomes the
user's own choice (`category_source` `manual`). `merchant_name` sets the user's merchant with that name
(case and spacing ignored), creating it if there is none yet.

**Errors**:

- `404`: Any of the transactions doesn't exist or isn't the user's
- `422`: No changes, a `null` other than `description`, a blank `merchant_name`, a future date, a category
  group, or a date change that includes a bank transaction (the bank sets its dates)

#### POST /transactions/bulk-delete

Delete up to 500 transactions entered by hand: `{ "transaction_ids": [3, 4] }` → `{ "affected": 2 }`.

**Errors**: `404` as above; `409` if any of them came from a bank (hide those instead).

#### GET /transactions/{id}

Get a specific transaction.

**Response** `200 OK`: Transaction object

**Errors**:

- `404`: Transaction not found
- `403`: Access denied

#### PATCH /transactions/{id}

Update a transaction.

**Request** (all fields optional):

```json
{
  "category_id": "integer",
  "amount": "string (decimal)",
  "description": "string | null",
  "occurred_at": "string (ISO 8601)",
  "is_hidden": "boolean (not null)",
  "needs_review": "boolean (not null)"
}
```

**Response** `200 OK`: Updated transaction object. Changing `category_id` makes `category_source` `manual`.
`is_hidden` hides or shows the transaction, and `needs_review` puts it in the review inbox or marks it reviewed;
leaving either out keeps it as it is. The bank sets the `amount` and
`occurred_at` of its transactions: sending either for an imported transaction returns `422` (send only the
fields that change).

**Errors**:

- `404`: Transaction not found
- `403`: Access denied
- `422`: Validation error

#### POST /transactions/{id}/categorize

Set the category the user picked (`category_source` becomes `manual`). With `apply_to_similar`, also save
a merchant rule and move the merchant's other transactions there, except those the user categorized by hand.
Future imports from the merchant follow the rule.

**Request**:

```json
{ "category_id": 7, "apply_to_similar": true }
```

**Response** `200 OK`:

```json
{
  "transaction": { /* updated transaction */ },
  "rule": { "id": 1, "merchant_name": "SKLAVENITIS", "category_id": 7, "created_at": "…", "updated_at": "…" },
  "similar_updated": 4
}
```

`rule` is `null` without `apply_to_similar`. One rule per merchant: categorizing again updates it.

**Errors**:

- `404` / `403`: Transaction or category not found / not accessible
- `422`: Category is a group, or `apply_to_similar` on a transaction without a merchant

#### DELETE /transactions/{id}

Delete a transaction entered by hand. Bank transactions can't be deleted (the next sync would bring
them back): hide them with `PATCH {"is_hidden": true}` instead.

**Response** `204 No Content`

**Errors**:

- `404`: Transaction not found
- `403`: Access denied
- `409`: The transaction was imported from a bank

---

### Merchant Rules

"Transactions from this merchant go to this category", created with `POST /transactions/{id}/categorize`.

| Endpoint | Description |
| --- | --- |
| `GET /rules` | The user's rules, by merchant: `[{id, merchant_name, category_id, created_at, updated_at}]` |
| `DELETE /rules/{id}` | Forget a rule (`204`). Transactions keep their categories; future imports fall back to the MCC. `404` for another user's rule |

---

### Merchants

Who transactions were with, as the user names them. Bank imports find or create them; the user changes a
transaction's merchant with `merchant_name` in `POST /transactions/bulk-update`.

| Endpoint | Description |
| --- | --- |
| `GET /merchants` | The user's merchants that have transactions, by name: `[{id, name}]` |

---

### Bank Connections

Optional read-only bank sync through Enable Banking (PSD2). Requires `CREAM_ENABLEBANKING_APP_ID` and
`CREAM_ENABLEBANKING_KEY_PATH`; otherwise these endpoints return `503`. Provider failures return `502`.

| Endpoint | Description |
| --- | --- |
| `GET /bank/aspsps?country=GR` | Banks available in a country |
| `POST /bank/connections` | Start: `{aspsp_name, country}` → `{url}` (send the user there) |
| `POST /bank/connections/complete` | Finish with the bank redirect's `{state, code}` → connection with accounts |
| `GET /bank/connections` | Connections (active/expired) with their accounts |
| `DELETE /bank/connections/{id}` | Disconnect (revokes consent); wallets and imported transactions stay |
| `POST /bank/accounts/{id}/link` | Link an account to `{wallet_id}`, or to a new wallet when `null` |
| `POST /bank/sync` | Import new booked transactions of all linked accounts → per-account `{imported, categorized, error}` |

**Sync rules**:

- Only booked transactions are imported (pending ones can still change)
- Each bank transaction is imported at most once per wallet (`external_id`): the bank's `transaction_id`
  when present, otherwise a fingerprint (reference, date, amount, text). `entry_reference` alone is not
  unique (banks reuse it), and identical same-day transactions are numbered (`#2`, `#3`)
- Imported transactions get a category automatically: the user's merchant rule, else the MCC mapping
  (Plaid's taxonomy as a guide), else **Other → Uncategorized**. Every sync also retries transactions still
  there; `categorized` counts both
- New imports need review as the user's preferences say: by default only those left in Uncategorized
- First sync reads 90 days back and sets the wallet's initial balance so it matches the bank; later syncs
  re-read the last 3 days to catch late bookings
- The `state` parameter is single-use and bound to the user who started the connection (CSRF protection)

---

### Statistics

#### GET /statistics

Get overall statistics for the user. Income, expenses and category totals leave out transfers between
your own wallets and hidden transactions; balances include every transaction. The same applies to
`/statistics/report`.

**Response** `200 OK`:

```json
{
  "total_balance": "5250.0000",
  "total_income": "8000.0000",
  "total_expenses": "2750.0000",
  "wallet_balances": [
    {
      "wallet_id": 1,
      "wallet_name": "Main Bank",
      "balance": "4250.0000"
    },
    {
      "wallet_id": 2,
      "wallet_name": "Cash",
      "balance": "1000.0000"
    }
  ],
  "spending_by_category": [
    {
      "category_id": 1,
      "category_name": "Food",
      "total": "1500.0000"
    }
  ],
  "income_by_category": [
    {
      "category_id": 5,
      "category_name": "Salary",
      "total": "8000.0000"
    }
  ]
}
```

#### GET /statistics/report

Get a financial report for a specific period.

**Query Parameters** (required):

- `start_date`: ISO 8601 datetime
- `end_date`: ISO 8601 datetime

**Response** `200 OK`:

```json
{
  "period": {
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z"
  },
  "summary": {
    "income": "4000.0000",
    "expenses": "2750.0000",
    "net_change": "1250.0000",
    "transaction_count": 45
  },
  "by_category": [
    {
      "category_id": 1,
      "category_name": "Food",
      "type": "expense",
      "total": "800.0000",
      "count": 15
    }
  ],
  "by_wallet": [
    {
      "wallet_id": 1,
      "wallet_name": "Main Bank",
      "income": "4000.0000",
      "expenses": "2000.0000",
      "net_change": "2000.0000"
    }
  ]
}
```

**Errors**:

- `422`: Missing or invalid date parameters

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Format (422)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "amount"],
      "msg": "Amount must not be zero",
      "input": "0"
    }
  ]
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
| ------ | --------- | ------- |
| `200` | OK | Successful GET, PATCH |
| `201` | Created | Successful POST |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Business logic error (duplicate username) |
| `401` | Unauthorized | Missing or invalid token |
| `403` | Forbidden | Access denied (not owner) |
| `404` | Not Found | Resource doesn't exist |
| `422` | Unprocessable Entity | Validation error |
| `500` | Internal Server Error | Unexpected server error |

---

## Data Types

### Decimal (Money)

- Format: String representation of decimal number
- Precision: 4 decimal places
- Example: `"1234.5678"`, `"-99.0000"`, `"0.0001"`

### DateTime

- Format: ISO 8601 with timezone
- Example: `"2025-01-15T14:30:00Z"`, `"2025-01-15T14:30:00+02:00"`

### Enums

**WalletType**: `"cash"`, `"investment"`, `"real_estate"`, `"vehicle"`, `"valuables"`, `"other_asset"` (assets);
`"credit_card"`, `"mortgage"`, `"loan"`, `"other_liability"` (liabilities). Subtypes: `GET /wallets/types`

**CategoryType**: `"income"`, `"expense"`

---

## Rate Limiting

Not implemented in MVP. Future consideration:

- 100 requests per minute per user
- 429 Too Many Requests response

---

## Pagination

Not implemented in MVP. Future consideration for list endpoints:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 50
}
```

Query parameters: `?page=1&per_page=50`

---

## Filtering and Sorting

### Current Support

- `GET /transactions?wallet_id=1` - Filter by wallet

### Future Consideration

- `?sort=occurred_at:desc` - Sorting
- `?category_id=1` - Filter by category
- `?from=2025-01-01&to=2025-01-31` - Date range filter

---

## Versioning Strategy

- Current version: `v1`
- Breaking changes require new version (`v2`)
- Non-breaking additions allowed in current version
- Old versions supported for minimum 6 months after deprecation

### Breaking Changes (require new version)

- Removing fields from responses
- Changing field types
- Changing endpoint paths
- Changing required fields

### Non-Breaking Changes (allowed in current version)

- Adding new optional fields to requests
- Adding new fields to responses
- Adding new endpoints
- Adding new query parameters
