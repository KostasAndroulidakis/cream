# CREAM Vision

## The Problem

Most people have no clear picture of their financial health. Money flows in and out across multiple accounts—bank accounts, digital wallets, cash—without visibility into where it goes. Existing solutions are either:

- **Too complex**: Enterprise accounting software designed for businesses, not individuals
- **Too limited**: Spreadsheets that require manual effort and break easily
- **Too invasive**: Apps that require linking bank accounts and sharing sensitive credentials
- **Too expensive**: Subscription services that charge monthly fees for basic tracking

The result: people avoid tracking finances altogether, leading to overspending, missed savings opportunities, and financial stress.

## The User

CREAM is designed for **individuals who want control over their finances** without complexity:

- People who use multiple payment methods (cards, cash, digital wallets)
- Those who want one view across all their banks, entered by hand or synced on their own terms
- Users who prefer manual entry for privacy and accuracy, or optional bank sync for convenience
- Anyone who has tried spreadsheets but found them tedious

**Not for**: Businesses, accountants, or investors trading securities.

## The Value Proposition

CREAM provides **clarity and control** over personal finances:

1. **See everything in one place**: All wallets, all transactions, unified view
2. **Understand spending patterns**: Categorized expenses with clear breakdowns
3. **Track progress over time**: Historical reports and trends
4. **Stay in control**: Manual entry means you decide what to track
5. **Privacy-first**: Bank connections are optional, read-only (PSD2) and revocable; your data stays in your own database

## Success Goals

### Primary Goals

1. **Accuracy**: Every transaction is recorded correctly with proper decimal precision
2. **Simplicity**: Core workflows (add transaction, check balance) take seconds
3. **Insight**: Users can answer "where did my money go?" within 30 seconds
4. **Reliability**: Data is never lost or corrupted

### Secondary Goals

1. **Speed**: All operations feel instant (<200ms response time)
2. **Accessibility**: Works on any device with a browser
3. **Longevity**: Data format is simple and exportable

### Success Metrics

- User can add a transaction in under 10 seconds
- Dashboard loads in under 1 second
- Monthly report generation is instant
- Zero data loss incidents

## What CREAM Is NOT

To maintain focus, CREAM explicitly does **not** aim to be:

| Not This | Why |
| ---------- | ----- |
| **Investment tracker** | Different domain (stocks, crypto have different needs) |
| **Business accounting** | No invoicing, no tax reports, no multi-user |
| **Budgeting enforcer** | We show data, we don't restrict spending |
| **AI financial advisor** | We provide data, not recommendations |
| **Social finance app** | No sharing, no comparisons, no gamification |

## Product Principles

1. **Data ownership**: Users own their data, can export anytime
2. **No dark patterns**: No upsells, no artificial limitations
3. **Offline-capable**: Core features work without internet (future)
4. **Transparent**: Open source, auditable code
5. **Respectful**: No tracking, no analytics, no ads

## MVP Scope

The minimum viable product includes:

- User authentication (signup/login)
- Wallet management (create, edit, delete)
- Transaction recording (income/expense with categories)
- Category management (hierarchical, custom categories)
- Balance tracking (per wallet, total)
- Basic statistics (income vs expenses, by category)
- Period reports (monthly, custom date range)

## Future Considerations (Post-MVP)

These are explicitly out of scope for MVP but may be considered later:

- Recurring transactions
- Budget planning and alerts
- Multi-currency support with conversion
- Data import/export (CSV, JSON)
- Mobile native apps
- Receipt photo attachments
- Tags and advanced filtering

## Decision Log

- **2026-10: Optional bank sync.** Manual-only entry was the original stance. Bank connections were added
  for personal use through Enable Banking (licensed PSD2 AISP, "restricted mode": only the owner's own
  accounts). Read-only access, consent expires after at most 180 days, and manual entry remains first-class.
