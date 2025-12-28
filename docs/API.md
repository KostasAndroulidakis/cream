# CREAM API Specification

## Overview

- **Base URL**: `/api/v1`
- **Format**: JSON
- **Authentication**: JWT Bearer tokens
- **Versioning**: URL path (`/api/v1`, `/api/v2`, etc.)

## Authentication Requirement

All endpoints except `/auth/*` require authentication.

## API Endpoints

| Endpoint | Description |
| --- | --- |
| `POST /api/v1/auth/signup` | User registration |
| `POST /api/v1/auth/login` | User login (returns JWT) |
| `GET /api/v1/wallets` | List user wallets |
| `POST /api/v1/wallets` | Create wallet |
| `GET /api/v1/wallets/{id}` | Get wallet |
| `PATCH /api/v1/wallets/{id}` | Update wallet |
| `DELETE /api/v1/wallets/{id}` | Delete wallet |
| `GET /api/v1/categories` | List categories |
| `POST /api/v1/categories` | Create category |
| `GET /api/v1/categories/{id}` | Get category |
| `PATCH /api/v1/categories/{id}` | Update category |
| `DELETE /api/v1/categories/{id}` | Delete category |
| `GET /api/v1/transactions` | List transactions |
| `POST /api/v1/transactions` | Create transaction |
| `GET /api/v1/transactions/{id}` | Get transaction |
| `PATCH /api/v1/transactions/{id}` | Update transaction |
| `DELETE /api/v1/transactions/{id}` | Delete transaction |
| `GET /api/v1/statistics` | Aggregated statistics |
| `GET /api/v1/statistics/report` | Period reports |

### Headers

```text
Authorization: Bearer <jwt_token>
```

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

Authenticate and receive a token.

**Request**:

```json
{
  "username": "string",
  "password": "string"
}
```

**Response** `200 OK`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors**:

- `401`: Invalid credentials

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
    "type": "bank",
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
  "type": "bank | cash | digital | stash",
  "currency": "string (3 chars, default: EUR)",
  "initial_balance": "string (decimal, default: 0)"
}
```

**Response** `201 Created`:

```json
{
  "id": 1,
  "name": "Main Bank",
  "type": "bank",
  "currency": "EUR",
  "initial_balance": "1000.0000",
  "balance": "1000.0000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

- `422`: Validation error

#### GET /wallets/{id}

Get a specific wallet.

**Response** `200 OK`:

```json
{
  "id": 1,
  "name": "Main Bank",
  "type": "bank",
  "currency": "EUR",
  "initial_balance": "1000.0000",
  "balance": "1250.5000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

- `404`: Wallet not found
- `403`: Access denied (not owner)

#### PATCH /wallets/{id}

Update a wallet.

**Request** (all fields optional):

```json
{
  "name": "string",
  "type": "bank | cash | digital | stash",
  "currency": "string"
}
```

**Response** `200 OK`: Updated wallet object

**Errors**:

- `404`: Wallet not found
- `403`: Access denied
- `422`: Validation error

#### DELETE /wallets/{id}

Delete a wallet and all its transactions.

**Response** `204 No Content`

**Errors**:

- `404`: Wallet not found
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
    "name": "Food",
    "type": "expense",
    "parent_id": null,
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Groceries",
    "type": "expense",
    "parent_id": 1,
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
  "type": "income | expense",
  "parent_id": "integer | null (optional)"
}
```

**Response** `201 Created`:

```json
{
  "id": 3,
  "name": "Restaurants",
  "type": "expense",
  "parent_id": 1,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:

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

List all transactions for the user's wallets.

**Query Parameters**:

- `wallet_id` (optional): Filter by wallet

**Response** `200 OK`:

```json
[
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
]
```

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

- `404`: Wallet not found
- `403`: Access denied (not owner of wallet)
- `422`: Validation error (amount zero, future date, etc.)

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
  "occurred_at": "string (ISO 8601)"
}
```

**Response** `200 OK`: Updated transaction object

**Errors**:

- `404`: Transaction not found
- `403`: Access denied
- `422`: Validation error

#### DELETE /transactions/{id}

Delete a transaction.

**Response** `204 No Content`

**Errors**:

- `404`: Transaction not found
- `403`: Access denied

---

### Statistics

#### GET /statistics

Get overall statistics for the user.

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

**WalletType**: `"bank"`, `"cash"`, `"digital"`, `"stash"`

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
