# CREAM Requirements

## Functional Requirements

### FR1: User Management

- FR1.1: Users can create an account with username, email, and password
- FR1.2: Users can log in with username and password
- FR1.3: Users receive a token upon successful authentication
- FR1.4: Users can only access their own data
- FR1.5: Usernames and emails must be unique across the system

### FR2: Wallet Management

- FR2.1: Users can create wallets with name, type, currency, and initial balance
- FR2.2: Users can view a list of all their wallets
- FR2.3: Users can view details of a specific wallet including current balance
- FR2.4: Users can update wallet name, type, and currency
- FR2.5: Users can delete a wallet (and all associated transactions)
- FR2.6: Wallet types include: bank, cash, digital, stash
- FR2.7: Wallet balance is calculated as: initial_balance + sum(transactions)

### FR3: Category Management

- FR3.1: Users can create custom categories with name and type (income/expense)
- FR3.2: Users can view all categories (personal and system defaults)
- FR3.3: Users can update their own categories
- FR3.4: Users can delete their own categories
- FR3.5: Users cannot modify or delete system default categories
- FR3.6: Categories can have a parent category (hierarchical structure)
- FR3.7: Category hierarchy must not contain cycles

### FR4: Transaction Management

- FR4.1: Users can create transactions with wallet, category, amount, date, and description
- FR4.2: Users can view all their transactions
- FR4.3: Users can filter transactions by wallet
- FR4.4: Users can view details of a specific transaction
- FR4.5: Users can update transaction details
- FR4.6: Users can delete transactions
- FR4.7: Positive amounts represent income, negative amounts represent expenses
- FR4.8: Users can only create transactions for wallets they own

### FR5: Statistics

- FR5.1: Users can view total balance across all wallets
- FR5.2: Users can view total income (sum of positive transactions)
- FR5.3: Users can view total expenses (sum of negative transactions)
- FR5.4: Users can view balance per wallet
- FR5.5: Users can view spending breakdown by category
- FR5.6: Users can view income breakdown by category

### FR6: Reports

- FR6.1: Users can generate reports for a specific date range
- FR6.2: Reports include income, expenses, and net change for the period
- FR6.3: Reports include transaction count for the period
- FR6.4: Reports include breakdown by category with totals and counts
- FR6.5: Reports include breakdown by wallet with income/expense/net

---

## Non-Functional Requirements

### NFR1: Correctness

- NFR1.1: All monetary calculations must use fixed-point decimal arithmetic
- NFR1.2: Monetary values must support 4 decimal places (NUMERIC(19,4))
- NFR1.3: No floating-point errors in financial calculations
- NFR1.4: Transactions must be ACID-compliant
- NFR1.5: Balance calculations must always be consistent with transaction history
- NFR1.6: Data validation must reject invalid inputs before persistence

### NFR2: Performance

- NFR2.1: API response time < 200ms for single-entity operations
- NFR2.2: API response time < 500ms for list operations (up to 1000 items)
- NFR2.3: API response time < 1s for statistics and reports
- NFR2.4: System must handle 10,000+ transactions per user without degradation
- NFR2.5: Database queries must use appropriate indexes

### NFR3: Security

- NFR3.1: Passwords must be hashed using a secure algorithm (bcrypt)
- NFR3.2: Authentication must use JWT tokens with expiration
- NFR3.3: All endpoints (except auth) must require authentication
- NFR3.4: Users must not be able to access other users' data
- NFR3.5: API must validate all inputs to prevent injection attacks
- NFR3.6: Sensitive data must not be logged
- NFR3.7: HTTPS must be used in production

### NFR4: Auditability

- NFR4.1: All entities must have created_at timestamp
- NFR4.2: Mutable entities must have updated_at timestamp
- NFR4.3: Transaction dates (occurred_at) must be preserved accurately
- NFR4.4: Deleted data should be actually removed (no soft deletes for MVP)

### NFR5: Reliability

- NFR5.1: System must handle database connection failures gracefully
- NFR5.2: Invalid requests must return appropriate error messages
- NFR5.3: System must not lose data on crashes
- NFR5.4: Database must support point-in-time recovery (PostgreSQL)

### NFR6: Maintainability

- NFR6.1: Code must have >80% test coverage for critical paths
- NFR6.2: API must be versioned (v1, v2, etc.)
- NFR6.3: Database schema changes must use migrations
- NFR6.4: Configuration must be externalized (environment variables)

### NFR7: Scalability (Future)

- NFR7.1: Architecture must support horizontal scaling of backend
- NFR7.2: Database must support read replicas if needed
- NFR7.3: Stateless backend (no server-side sessions)

---

## Validation Rules

### VR1: Transaction Validation

- VR1.1: Amount must not be zero
- VR1.2: Amount must be >= 0.0001 (minimum precision)
- VR1.3: Amount must be <= 999,999,999.9999 (maximum value)
- VR1.4: occurred_at must not be in the future
- VR1.5: wallet_id must reference an existing wallet owned by the user
- VR1.6: category_id must reference an accessible category

### VR2: Wallet Validation

- VR2.1: Name must not be empty
- VR2.2: Name must be <= 100 characters
- VR2.3: Type must be one of: bank, cash, digital, stash
- VR2.4: Currency must be a valid 3-letter code

### VR3: Category Validation

- VR3.1: Name must not be empty
- VR3.2: Name must be <= 100 characters
- VR3.3: Type must be one of: income, expense
- VR3.4: parent_id must not create a cycle in the hierarchy

### VR4: User Validation

- VR4.1: Username must be 3-50 characters
- VR4.2: Email must be a valid email format
- VR4.3: Password must be at least 8 characters

---

## Constraints

### Technical Constraints

- TC1: Backend must be implemented in Python with FastAPI
- TC2: Database must be PostgreSQL
- TC3: All monetary values stored as NUMERIC(19,4)
- TC4: API must follow REST conventions
- TC5: Authentication via JWT tokens

### Business Constraints

- BC1: Single-user system (no sharing between users)
- BC2: No bank account integration
- BC3: No real-time currency conversion
- BC4: No automated transaction import
