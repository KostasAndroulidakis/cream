# Testing

## Overview

All tests are located in `api/tests/` and use pytest. Run them from `api/` via uv.

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_auth.py
```

## Test Coverage

| Module | Tests | Description |
| -------- | ------- | ------------- |
| Auth | 16 | Signup, login, session cookie, `/me`, logout |
| Wallets | 30 | CRUD, ownership, currency rules, totals |
| Categories | 28 | CRUD, hierarchy, system defaults |
| Transactions | 27 | CRUD, validation, filtering |
| Statistics | 10 | Aggregations, reports |
| Validation | 29 | Business rule validation |
| Health | 3 | API and database availability |
| Category rules | 9 | Groups, transfer type, parent type, pagination |
| Bank sync | 22 | Mapping, connections, linking, sync, duplicates, expiry |
| **Total** | **174** | |

## Validation Rules Tested

| Rule | Description |
| ------ | ------------- |
| VR1.1 | Amount must not be zero |
| VR1.2 | Amount >= 0.0001 |
| VR1.3 | Amount <= 999,999,999.9999 |
| VR1.4 | `occurred_at` must not be in the future |
| VR1.5 | `wallet_id` must be valid and owned |
| VR1.6 | `category_id` must be accessible |
| VR2.4 | Currency must be exactly 3 characters |
| VR3.4 | Category hierarchy must not contain cycles |
| VR4.1 | Username must be 3-50 characters |
| VR4.3 | Password must be at least 8 characters |

## Test Structure

```text
api/tests/
├── conftest.py          # Fixtures (test DB, client, auth)
├── test_auth.py         # Authentication endpoints
├── test_wallets.py      # Wallet CRUD
├── test_categories.py   # Category CRUD + hierarchy
├── test_transactions.py # Transaction CRUD
├── test_statistics.py   # Statistics + reports
└── test_validation.py   # Business rule validation
```
