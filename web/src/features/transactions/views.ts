import { allTransactionsQueryOptions, needsReviewTransactionsQueryOptions } from "./api"

/** The lists the Transactions page can show, picked from the dropdown above the list. */
export const TRANSACTION_VIEWS = {
  all: {
    label: "All transactions",
    query: allTransactionsQueryOptions,
    emptyMessage: "No transactions yet.",
    // Its pages count the transactions that need review ("Mark all N as reviewed")
    countsForReview: false,
  },
  "needs-review": {
    label: "Needs review",
    query: needsReviewTransactionsQueryOptions,
    emptyMessage: "All caught up: no transactions need review.",
    countsForReview: true,
  },
} as const

export type TransactionView = keyof typeof TRANSACTION_VIEWS

export const DEFAULT_VIEW: TransactionView = "all"

export function isTransactionView(value: string | null): value is TransactionView {
  return value !== null && Object.hasOwn(TRANSACTION_VIEWS, value)
}
