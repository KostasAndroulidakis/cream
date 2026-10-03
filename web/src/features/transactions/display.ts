import type { Transaction } from "./api"

/** Who the money went to or came from: the merchant (the user's name for it), else the bank's text, else the note. */
export function transactionLabel(transaction: Transaction): string | null {
  return transaction.merchant?.name || transaction.counterparty || transaction.description || null
}
