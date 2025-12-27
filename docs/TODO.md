# TODO: Code Quality Issues

Found 26 issues (7 HIGH, 15 MEDIUM, 4 LOW) during code review.

## SRP (Single Responsibility Principle) Violations

- [x] **#1 HIGH** `api/statistics.py:26-128` - `get_statistics()` is 100+ lines mixing business logic with HTTP handling. Extract to service layer.
  - Fixed: Created `services/statistics.py` with `calculate_statistics()`
- [x] **#2 HIGH** `api/statistics.py:131-237` - `get_report()` is 100+ lines mixing business logic with HTTP handling. Extract to service layer.
  - Fixed: Created `services/statistics.py` with `calculate_report()`
- [x] **#3 MEDIUM** `api/transactions.py:13-32` - `verify_wallet_ownership()` and `get_user_transaction()` mix retrieval + authorization.
  - Fixed: Moved to `services/authorization.py`
- [x] **#4 MEDIUM** `api/categories.py:12-35` - Two nearly identical helper functions `get_accessible_category()` and `get_user_category()` (DRY violation).
  - Fixed: Unified in `services/authorization.py` with `get_category(allow_system, require_ownership)`
- [x] **#5 MEDIUM** `api/wallets.py:12` - `get_user_wallet()` mixes retrieval and authorization.
  - Fixed: Moved to `services/authorization.py`
- [ ] **#6 MEDIUM** `api/auth.py:12-29` - `signup()` mixes duplicate checking, hashing, creation, and response formatting.

## SSOT (Single Source of Truth) Violations

- [x] **#7 HIGH** Multiple API files - Ownership verification pattern duplicated across `wallets.py:17-18`, `categories.py:21,33-34`, `transactions.py:18-19,30-31`.
  - Fixed: Centralized in `services/authorization.py`
- [x] **#8 MEDIUM** Multiple files - Identical `model_dump()` update pattern repeated in `wallets.py:61-62`, `categories.py:80-81`, `transactions.py:117-118`.
  - Fixed: Created `services/helpers.py` with `apply_update()`
- [x] **#9 MEDIUM** `api/statistics.py` - Decimal conversion from query results repeated 5+ times.
  - Fixed: Centralized `_to_decimal()` in `services/statistics.py`
- [x] **#10 MEDIUM** `api/statistics.py:33-34,140-141` - User wallet filtering duplicated in both endpoints.
  - Fixed: Created `get_user_wallets()` and `get_user_wallet_ids()` in `services/statistics.py`
- [ ] **#11 LOW** `api/auth.py:14-17` - Duplicate user checking pattern for username and email.

## Security Issues

- [x] **#12 HIGH** `api/transactions.py:76` - `category_id` not validated to belong to user before creation.
  - Fixed: Added `verify_category_access()` in `create_transaction` and `update_transaction`
- [x] **#13 HIGH** `api/categories.py:55` - `parent_id` could reference another user's category, no validation.
  - Fixed: Added `verify_category_access()` in `create_category` and `update_category`
- [x] **#14 MEDIUM** Multiple files - `model_dump()` converts all fields, could expose sensitive data if added to schemas.
  - Reviewed: Not a current vulnerability. Input schemas (Create/Update) don't contain sensitive fields. Output schemas (Read) explicitly define exposed fields.

## Performance Issues

- [x] **#15 HIGH** `models/wallet.py:40-43` - `balance` property uses N+1 query pattern, iterates all transactions in memory.
  - Fixed: Replaced with `column_property` using SQL subquery - balance calculated in single query
- [x] **#16 HIGH** `api/statistics.py` - No pagination for large result sets, loads all data into memory.
  - Fixed: Added `limit` parameter (default 50) to category breakdown queries in `services/statistics.py`
- [x] **#17 MEDIUM** `api/transactions.py:43` - Loads all wallet IDs into Python instead of using subquery.
  - Fixed: Created `get_user_wallet_ids_subquery()` in authorization service, used in `list_transactions`

## Error Handling Issues

- [ ] **#18 MEDIUM** `api/auth.py:12-17` - No error logging on failed signup attempts.
- [ ] **#19 MEDIUM** `api/transactions.py:69-71,113-115` - Validation errors returned as untyped detail list, no schema.
- [ ] **#20 MEDIUM** `api/wallets.py:14` - No try/catch for database errors during wallet operations.
- [ ] **#21 MEDIUM** `database.py:14-19` - No context manager error handling in `get_db()`.

## Type/Validation Issues

- [ ] **#22 MEDIUM** `services/validation.py:146-148` - Naive datetime assumed to be UTC (dangerous assumption).
- [ ] **#23 MEDIUM** `services/auth.py:55-77` - `get_current_user()` duplicates `get_current_user_id()` logic.

## Other Issues

- [ ] **#24 LOW** `main.py:14-16` - Health check doesn't verify database connectivity.
- [ ] **#25 LOW** Multiple models - Duplicate datetime defaults using lambda, should use base class.
- [ ] **#26 LOW** `api/statistics.py:65-68,164-166,207-208` - Repeated SQL conditional aggregation pattern.
  - Partially fixed: Moved to `_sum_income_expr()` and `_sum_expenses_expr()` in `services/statistics.py`

## Summary

| Category | HIGH | MEDIUM | LOW | Fixed |
| ---------- | ------ | -------- | ----- | ----- |
| SRP Violations | 2 | 4 | 0 | 5/6 |
| SSOT Violations | 1 | 3 | 1 | 4/5 |
| Security Issues | 2 | 1 | 0 | 3/3 ✅ |
| Performance Issues | 2 | 1 | 0 | 3/3 ✅ |
| Error Handling | 0 | 4 | 0 | 0/4 |
| Type/Validation | 0 | 2 | 0 | 0/2 |
| Other | 0 | 0 | 3 | 1/3 |
| **TOTAL** | **7** | **15** | **4** | **16/26** |

## New Services Created

| Service | Purpose |
| ------- | ------- |
| `services/authorization.py` | Centralized ownership verification |
| `services/statistics.py` | Statistics business logic |
| `services/helpers.py` | Common utilities (`apply_update`) |
