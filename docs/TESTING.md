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
| Auth | 30 | Signup, login, session cookie, `/me`, profile, logout |
| Wallets | 58 | CRUD, ownership, account types and subtypes, EUR only, totals, summary |
| Net worth | 13 | Net worth day by day, worked out from the transactions |
| Categories | 58 | CRUD, hierarchy, system defaults, groups, order, per-user overrides |
| Category rules | 9 | Groups, transfer type, parent type, pagination |
| Transactions | 27 | CRUD, validation, filtering |
| Bulk transactions | 22 | Bulk edit and bulk delete, all or nothing |
| Hidden transactions | 9 | Out of lists, inbox and statistics, still in the balance |
| Review | 15 | Needs review set on import by preferences, mark reviewed |
| Statistics | 10 | Aggregations, reports |
| Validation | 29 | Business rule validation |
| Health | 3 | API and database availability |
| Bank sync | 42 | Mapping, connections, linking, sync, duplicates, expiry, currencies, longest history, provider errors, bank list, merchants on import |
| Categorization | 21 | Merchant keys, MCC map vs. seeded catalog, rule → MCC → inbox order, apply to similar, manual choices kept, rules ownership |
| Merchants | 33 | List, rename, website, Merge & delete, known spellings on import, gathering on sync |
| Merchant catalog | 39 | Known merchants against real bank spellings, go-betweens |
| Logos | 4 | Logos through the API |
| Transfers | 17 | Pairing own-account transfers, user choices kept, list order, the other side's account |
| **Total** | **439** | |

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
├── conftest.py               # Fixtures (test DB, client, auth, fake bank, Uncategorized)
├── bank_fakes.py             # Fake Open Banking provider + connect/sync helpers
├── test_auth.py              # Authentication endpoints
├── test_wallets.py           # Wallet CRUD, account types, summary
├── test_net_worth.py         # Net worth over time
├── test_categories.py        # Category CRUD, hierarchy, order, overrides
├── test_category_rules.py    # Groups, transfer type, parent type
├── test_transactions.py      # Transaction CRUD
├── test_bulk_transactions.py # Bulk edit and delete
├── test_hidden_transactions.py # Hiding transactions
├── test_review.py            # Review inbox
├── test_statistics.py        # Statistics + reports
├── test_validation.py        # Business rule validation
├── test_health.py            # Health check
├── test_bank.py              # Bank connections and sync
├── test_categorization.py    # Auto-categorization, rules
├── test_merchants.py         # Merchants, Merge & delete, gathering
├── test_merchant_catalog.py  # Known merchants
├── test_logos.py             # Merchant logos
└── test_transfers.py         # Own-account transfers
```
