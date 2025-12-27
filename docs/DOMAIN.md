# CREAM Domain Model

## Glossary

| Term | Definition |
| ------ | ------------ |
| **User** | A person who uses CREAM to track their finances |
| **Wallet** | A container for money (bank account, cash, digital wallet) |
| **Transaction** | A single movement of money (income or expense) |
| **Category** | A classification for transactions (e.g., Food, Salary) |
| **Balance** | The current amount of money in a wallet |
| **Income** | Money received (positive transaction) |
| **Expense** | Money spent (negative transaction) |
| **Period** | A date range for reporting purposes |

## Entities

### User

A registered individual who owns wallets and tracks transactions.

```text
User
├── id: unique identifier
├── username: unique login name
├── email: unique email address
├── password_hash: securely hashed password
├── first_name: given name
├── last_name: family name
├── created_at: registration timestamp
└── updated_at: last modification timestamp
```

**Invariants**:

- Username must be unique across all users
- Email must be unique across all users
- Password must be stored as a secure hash, never plaintext

### Wallet

A container representing a source or destination of money.

```text
Wallet
├── id: unique identifier
├── user_id: owner reference
├── name: display name (e.g., "Main Bank Account")
├── type: wallet_type enum
├── currency: 3-letter currency code (e.g., "EUR")
├── initial_balance: starting balance (Money)
├── created_at: creation timestamp
└── updated_at: last modification timestamp
```

**Wallet Types**:

| Type | Description | Examples |
| ------ | ------------- | ---------- |
| `bank` | Traditional bank account | Checking, Savings |
| `cash` | Physical currency | Wallet, Safe |
| `digital` | Digital payment service | PayPal, Venmo, Google Pay |
| `stash` | Savings or reserve | Emergency fund, Vacation fund |

**Invariants**:

- A wallet belongs to exactly one user
- Wallet name must not be empty
- Currency code must be exactly 3 characters
- Initial balance can be any value (including negative for debt accounts)

### Category

A classification for organizing transactions.

```text
Category
├── id: unique identifier
├── user_id: owner reference (NULL for system defaults)
├── parent_id: parent category reference (NULL for root)
├── name: display name (e.g., "Groceries")
├── type: category_type enum (income/expense)
└── created_at: creation timestamp
```

**Category Types**:

| Type | Description | Used For |
| ------ | ------------- | ---------- |
| `income` | Money received | Salary, Gifts, Refunds |
| `expense` | Money spent | Food, Transport, Bills |

**System Default Categories**:
Categories with `user_id = NULL` are system defaults, visible to all users but not modifiable.

**Invariants**:

- Category type is immutable after creation
- Parent category must exist if parent_id is set
- Category hierarchy must not contain cycles
- User can only modify categories they own (user_id matches)
- System default categories cannot be modified or deleted

### Transaction

A single financial event recording money movement.

```text
Transaction
├── id: unique identifier
├── wallet_id: wallet reference
├── category_id: category reference
├── amount: monetary value (Money)
├── description: optional note
├── occurred_at: when the transaction happened
├── created_at: record creation timestamp
└── updated_at: last modification timestamp
```

**Invariants**:

- Amount must not be zero
- Amount positive = income, negative = expense
- Wallet must exist and belong to the user
- Category must be accessible to the user
- occurred_at must not be in the future

## Value Objects

### Money

A precise decimal representation of monetary value.

```text
Money
├── value: NUMERIC(19,4)
└── Precision: 4 decimal places
```

**Properties**:

- **Range**: -999,999,999,999,999.9999 to 999,999,999,999,999.9999
- **Minimum non-zero**: 0.0001
- **Storage**: Fixed-point decimal (not floating-point)

**Invariants**:

- No floating-point representation (prevents rounding errors)
- All arithmetic preserves 4 decimal places
- Comparison is exact (no epsilon tolerance)

**Examples**:

```text
Valid:    100.0000, -50.5000, 0.0001, 999999999.9999
Invalid:  0.00001 (too precise), 1e10 (scientific notation)
```

### Timestamp

A point in time with timezone awareness.

```text
Timestamp
├── value: TIMESTAMPTZ (PostgreSQL)
└── Format: ISO 8601 with timezone
```

**Invariants**:

- Always stored in UTC
- Displayed in user's local timezone (frontend responsibility)

## Relationships

```text
┌─────────────────────────────────────────────────────────────┐
│                     Entity Relationships                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    User (1) ─────────────────────────── (*) Wallet          │
│      │                                       │               │
│      │                                       │               │
│      │ (1)                              (1)  │               │
│      │                                       │               │
│      ▼                                       ▼               │
│    (*) Category ◄─────────────────────── (*) Transaction    │
│      │                                                       │
│      │ (0..1)                                               │
│      │                                                       │
│      ▼                                                       │
│    (*) Category  [self-reference: parent_id]                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Cardinality:
- User has many Wallets
- User has many Categories (including access to system defaults)
- Wallet has many Transactions
- Category has many Transactions
- Category may have one Parent Category
- Category may have many Child Categories
```

## Business Rules

### BR1: Balance Calculation

```text
wallet.balance = wallet.initial_balance + SUM(transactions.amount)
                 WHERE transactions.wallet_id = wallet.id
```

- Balance is always calculated, never stored
- Includes all transactions regardless of date
- Can be negative (overdraft/debt)

### BR2: Transaction Amount Rules

| Rule | Description |
| ------ | ------------- |
| BR2.1 | Amount = 0 is forbidden |
| BR2.2 | Amount > 0 indicates income |
| BR2.3 | Amount < 0 indicates expense |
| BR2.4 | Minimum absolute value: 0.0001 |
| BR2.5 | Maximum absolute value: 999,999,999.9999 |

### BR3: Date Rules

| Rule | Description |
| ------ | ------------- |
| BR3.1 | `occurred_at` must not be in the future |
| BR3.2 | `occurred_at` can be any past date |
| BR3.3 | `created_at` is set automatically |
| BR3.4 | `updated_at` is set on every modification |

### BR4: Ownership Rules

| Rule | Description |
| ------ | ------------- |
| BR4.1 | User can only see their own wallets |
| BR4.2 | User can only see their own transactions |
| BR4.3 | User can see their categories + system defaults |
| BR4.4 | User can only modify their own categories |
| BR4.5 | User cannot modify system default categories |

### BR5: Deletion Rules

| Rule | Description |
| ------ | ------------- |
| BR5.1 | Deleting a wallet deletes all its transactions |
| BR5.2 | Deleting a category is blocked if transactions reference it |
| BR5.3 | Deleting a parent category deletes child categories |
| BR5.4 | User account deletion deletes all owned data |

### BR6: Category Hierarchy Rules

| Rule | Description |
| ------ | ------------- |
| BR6.1 | Maximum hierarchy depth: unlimited (practical limit ~10) |
| BR6.2 | Category cannot be its own parent |
| BR6.3 | Category cannot create circular references |
| BR6.4 | Child category inherits nothing from parent (flat reporting) |

## Aggregations

### Total Balance

```text
total_balance = SUM(wallet.balance) FOR ALL user wallets
```

### Total Income (All Time)

```text
total_income = SUM(transaction.amount)
               WHERE amount > 0
               AND wallet.user_id = current_user
```

### Total Expenses (All Time)

```text
total_expenses = ABS(SUM(transaction.amount))
                 WHERE amount < 0
                 AND wallet.user_id = current_user
```

### Period Aggregations

For a given date range [start_date, end_date]:

```text
period_income = SUM(amount) WHERE amount > 0 AND occurred_at IN range
period_expenses = ABS(SUM(amount)) WHERE amount < 0 AND occurred_at IN range
period_net = period_income - period_expenses
```

### Category Breakdown

```text
category_total = SUM(ABS(amount)) GROUP BY category_id
category_count = COUNT(*) GROUP BY category_id
```

## State Transitions

### Transaction Lifecycle

```text
[Created] ──▶ [Active] ──▶ [Deleted]
                 │
                 ▼
            [Modified]
                 │
                 ▼
            [Active]
```

- Transactions have no "pending" or "draft" state
- Once created, a transaction is immediately active
- Modifications update the `updated_at` timestamp
- Deletion is permanent (no soft delete)

### Wallet Lifecycle

```text
[Created] ──▶ [Active] ──▶ [Deleted]
                 │              │
                 ▼              ▼
            [Modified]    [Transactions
                 │         Cascade Deleted]
                 ▼
            [Active]
```

## Edge Cases

### Zero Balance

- Valid state: wallet can have zero balance
- Displayed as "0.00" or equivalent

### Negative Balance

- Valid state: represents debt or overdraft
- No automatic blocking of transactions
- User responsibility to manage

### Empty Wallet

- Wallet with no transactions
- Balance = initial_balance

### Orphan Transactions

- Not possible: wallet_id is required and validated
- Cascade delete ensures cleanup

### Category Without Transactions

- Valid state: category exists but unused
- Can be deleted without issues

### Future Dates

- Not allowed for `occurred_at`
- Validation rejects with clear error message
