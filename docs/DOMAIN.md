# CREAM Domain Model

## Glossary

| Term | Definition |
| ------ | ------------ |
| **User** | A person who uses CREAM to track their finances |
| **Wallet** | A container for money (bank account, cash, digital wallet). Called **Account** in the UI, as in Monarch; the API and code keep "wallet" so it isn't confused with a bank's own accounts |
| **Transaction** | A single movement of money (income or expense) |
| **Category** | A classification for transactions (e.g., Food, Salary) |
| **Balance** | The current amount of money in a wallet |
| **Income** | Money received (positive transaction) |
| **Expense** | Money spent (negative transaction) |
| **Period** | A date range for reporting purposes |
| **Merchant** | Who a transaction was with, under a name the user can change; imports start with the bank's counterparty, else the transaction text |
| **MCC** | Merchant category code (ISO 18245) the bank reports for card payments, e.g. 5411 = grocery stores |
| **Merchant rule** | The user's choice "this merchant always goes to this category" |

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
├── display_name: what the app calls the user (optional, falls back to first_name)
├── birthday: date of birth (optional, a past date)
├── timezone: IANA timezone, e.g. Europe/Athens (optional, the browser's own when unset)
├── created_at: registration timestamp
└── updated_at: last modification timestamp
```

**Invariants**:

- Username must be unique across all users
- Email must be unique across all users
- Password must be stored as a secure hash, never plaintext

### User Preferences

How the app behaves for one user (Settings › Preferences). A user without saved preferences gets the defaults.

```text
UserPreferences
├── user_id: owner (one row per user, created when a preference first changes)
├── review_new_transactions: every new bank transaction needs review (default off)
├── review_uncategorized_transactions: new bank transactions left in Uncategorized need review (default on)
├── created_at: creation timestamp
└── updated_at: last modification timestamp
```

### Wallet

A container representing a source or destination of money.

```text
Wallet
├── id: unique identifier
├── user_id: owner reference
├── name: display name (e.g., "Main Bank Account")
├── type: wallet_type enum (Monarch's types: cash, investment, … credit_card, loan, …)
├── subtype: one of the type's subtypes (e.g. cash → checking), from the catalog
├── currency: ISO 4217 code; only "EUR" for now (older accounts may differ); fixed once it has transactions
├── initial_balance: starting balance (Money)
├── created_at: creation timestamp
└── updated_at: last modification timestamp
```

**Wallet Types** (as in Monarch; the full subtype lists are in `api/app/services/account_types.py`):

| Type | Class | Subtypes (examples) |
| ------ | ------- | ---------- |
| `cash` | Asset | CD, Checking, Savings, PayPal, Prepaid, Money Market, … (Plaid's depository list) |
| `investment` | Asset | Brokerage, Crypto Exchange, Pension, … (Plaid's investment list) |
| `real_estate` | Asset | Primary Home, Secondary Home, Rental Property |
| `vehicle` | Asset | Car, Boat, Motorcycle, Snowmobile, Bicycle, Other |
| `valuables` | Asset | Art, Jewelry, Collectibles, Furniture, Other |
| `other_asset` | Asset | Other |
| `credit_card` | Liability | Credit Card, PayPal |
| `mortgage` | Liability | Mortgage |
| `loan` | Liability | Auto, Business, Commercial, Construction, Consumer, Home, Home Equity, Loan, Mortgage, Overdraft, Line of Credit, Student |
| `other_liability` | Liability | Other |

**Invariants**:

- A wallet belongs to exactly one user
- Wallet name must not be empty
- Currency must be one CREAM supports: EUR only for now (`services/currencies.py`)
- A bank account links only to an account in its own currency
- Initial balance can be any value (including negative for debt accounts)
- The subtype is one of its type's subtypes; a new type without a subtype starts at the type's first
- A linked bank account starts as Cash › Checking

### Category

A classification for organizing transactions.

```text
Category
├── id: unique identifier
├── user_id: owner reference (NULL for system defaults)
├── parent_id: parent category reference (NULL for root)
├── name: display name (e.g., "Groceries")
├── type: category_type enum (income/expense/transfer)
├── key: stable identifier of a system category (e.g. "food_and_dining.groceries"), NULL for user categories
├── is_group: true for groups that organize categories (never assigned to transactions)
├── icon: emoji shown next to the name (system categories have Monarch's)
├── budget_by: groups only, "category" (default) or "group": how the group is budgeted
├── exclude_from_budget: categories only, left out of the budget with their transactions
└── created_at: creation timestamp
```

**Order**: each user can reorder the categories inside a group (Settings › Categories, drag and drop).
The order is stored per user in `category_positions`, since system categories are shared; categories
without a position follow in default order.

**Changing system categories**: they are shared, so a user's changes are stored as their own
`category_overrides` row: a new name, a budget choice, or `is_hidden` when they delete it. A hidden
category is gone for that user only: not listed, not assignable, never chosen by automatic
categorization. Deleting is refused while the user has transactions in it, and Uncategorized can't be
deleted.

**Category Types**:

| Type | Description | Used For |
| ------ | ------------- | ---------- |
| `income` | Money received | Salary, Gifts, Refunds |
| `expense` | Money spent | Food, Transport, Bills |
| `transfer` | Money moving between your own wallets | Account transfer, Cash & ATM, Credit card payment |

Transfers change wallet balances but are **excluded** from income, expense and category statistics,
so moving money between your own accounts is never counted twice.

**System Default Categories**:
Categories with `user_id = NULL` are system defaults, visible to all users but not modifiable.
They follow Monarch's default set: groups (e.g. "Food & Dining") containing categories (e.g. "Groceries"),
seeded by an Alembic migration. Each has a stable `key` for translations and automatic categorization.

**Invariants**:

- Category type is immutable after creation
- Parent category must exist if parent_id is set
- Category hierarchy must not contain cycles
- A subcategory has the same type as its parent
- Transactions use categories, never groups (`is_group = false`)
- User can only modify categories they own (user_id matches); system ones only through their own overrides
- System default categories cannot be modified or deleted

### Transaction

A single financial event recording money movement.

```text
Transaction
├── id: unique identifier
├── wallet_id: wallet reference
├── category_id: category reference
├── category_source: who chose the category (manual / rule / mcc / default)
├── amount: monetary value (Money)
├── description: optional note (the bank's text for imports)
├── occurred_at: when the transaction happened
├── external_id: bank identity of an imported transaction (NULL for manual entries)
├── counterparty: who the money went to / came from (imports)
├── merchant_category_code: the bank's MCC (imports)
├── merchant_key: normalized merchant (imports), what merchant rules match on
├── merchant_id: the merchant the user sees (optional)
├── is_hidden: left out of lists and statistics, still part of the balance
├── needs_review: waiting in the review inbox (independent of category and hiding)
├── created_at: record creation timestamp
└── updated_at: last modification timestamp
```

**Invariants**:

- Amount must not be zero
- Amount positive = income, negative = expense
- Wallet must exist and belong to the user
- Category must be accessible to the user
- occurred_at must not be in the future

### Merchant

```text
Merchant
├── id: unique identifier
├── user_id: owner reference
├── name: what the user sees, e.g. "Sklavenitis"
├── key: normalized name (case and spacing ignored)
├── created_at: creation timestamp
└── updated_at: last modification timestamp
```

**Invariants**:

- At most one merchant per name (case and spacing ignored) per user
- A bank import finds the user's merchant by the bank's name, or creates it (named as the bank first wrote it)
- Deleting a merchant leaves its transactions without a merchant

### Merchant Rule

```text
MerchantRule
├── id: unique identifier
├── user_id: owner reference
├── merchant_key: normalized merchant (case and spacing ignored)
├── merchant_name: the merchant as the bank wrote it, for display
├── category_id: where the merchant's transactions go
├── created_at: creation timestamp
└── updated_at: last modification timestamp
```

**Invariants**:

- At most one rule per merchant per user
- The category is assignable (accessible, not a group)
- Deleting a user category deletes the rules that point to it

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
| BR5.5 | Bank transactions can't be deleted (a sync would bring them back); they are hidden instead |

### BR6: Category Hierarchy Rules

| Rule | Description |
| ------ | ------------- |
| BR6.1 | Maximum hierarchy depth: unlimited (practical limit ~10) |
| BR6.2 | Category cannot be its own parent |
| BR6.3 | Category cannot create circular references |
| BR6.4 | Child category inherits nothing from parent (flat reporting) |

### BR7: Categorization Rules

| Rule | Description |
| ------ | ------------- |
| BR7.1 | An imported transaction's category: the user's merchant rule, else the MCC mapping, else Other → Uncategorized |
| BR7.2 | A category the user picks (`manual`) is never changed by rules or the MCC |
| BR7.3 | "Apply to similar" saves the merchant's rule and moves the merchant's other non-manual transactions to it |
| BR7.4 | Every sync retries the user's transactions still waiting in Uncategorized (`default`) |
| BR7.5 | Rules only ever touch the owner's transactions |
| BR7.6 | Deleting a rule keeps the categories it set |

### BR8: Review Rules

| Rule | Description |
| ------ | ------------- |
| BR8.1 | A new bank transaction needs review if the user reviews every new one, or it was left in Uncategorized and the user reviews those |
| BR8.2 | Only the user changes the review status after import: choosing a category or a rule categorizing it doesn't |
| BR8.3 | The review inbox lists visible transactions that need review; hiding one keeps its status |

## Aggregations

Income and expense aggregations leave out transfers between your own wallets and hidden transactions.
Balances always include every transaction, so they match the bank.

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
