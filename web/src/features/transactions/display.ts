import type { Transaction } from "./api"

/** How buttons and messages refer to a transaction without a label. */
export const UNNAMED_TRANSACTION = "this transaction"

/** Who the money went to or came from: the merchant (the user's name for it), else the bank's text, else the note. */
export function transactionLabel(transaction: Transaction): string | null {
  return transaction.merchant?.name || transaction.counterparty || transaction.description || null
}
