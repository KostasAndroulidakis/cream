# Testing

## Overview

All tests are located in `backend/tests/` and use pytest.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py
```

## Test Coverage

| Module | Tests | Description |
| -------- | ------- | ------------- |
| Auth | 9 | Signup, login, JWT validation |
| Wallets | 18 | CRUD operations, ownership checks |
| Categories | 28 | CRUD, hierarchy, system defaults |
| Transactions | 27 | CRUD, validation, filtering |
| Statistics | 10 | Aggregations, reports |
| Validation | 29 | Business rule validation |
| **Total** | **121** | |

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
backend/tests/
├── conftest.py          # Fixtures (test DB, client, auth)
├── test_auth.py         # Authentication endpoints
├── test_wallets.py      # Wallet CRUD
├── test_categories.py   # Category CRUD + hierarchy
├── test_transactions.py # Transaction CRUD
├── test_statistics.py   # Statistics + reports
└── test_validation.py   # Business rule validation
```
