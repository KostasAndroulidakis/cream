# CREAM

Personal finance tracker app.

## Specificaton

- Track transactions per wallet. Wallets can be:
  - Bank Accounts
  - Digital Wallets (PayPal, Google Pay, etc)
  - Personal Wallets
  - Stashes
  - or anything that tracks a money balance.

## Objects

- `Wallet`: holds a balance
  - `balance`
  - `history`: history of transactions

- `Transaction`: annotated transaction
  - `amount`: signed + or -
  - `source`: income
  - `target`: expense
  - `date`: date and time
  - `description`

## Program Behavior

- Program starts:
  - Show login screen
  - Validate credentials
  - Option for "remember me"
  - 'Log In' button leads to Dashboard
  - Option for "Sign up"
  if user click on "Sign up":
    - Show signup screen
    - Create account (name, username, password)
    - Login user to Dashboard

- Main Dashboard:
  - Summary of accounts and balances
  - Recent transactions
  - Month-to-date income vs. expenses
  - Balance status
  - Settings:
    - Set up bank accounts (name, initial balance)
    - Create default categories

- Navigation options:
  - Add transaction (income/expense)
  - View/edit transactions
  - Generate reports
  - Manage balance
  - Account settings

- Transaction entry:
  - Amount
  - Category (dropdown + option to create new)
  - Account (bank or cash)
  - Date and time
  - Description/notes
  - Receipt photo (optional)

- Reports section:
  - Monthly summaries
  - Category breakdowns
  - Income vs. expenses over time
  - Export options

- Balance section:
  - Set spending limits by category
  - Track progress
  - Alerts for approaching limits
