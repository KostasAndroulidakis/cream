import type { Transaction } from "./api"

/** Who the money went to or came from: the bank's merchant, else the user's note. */
export function transactionLabel(transaction: Transaction): string | null {
  return transaction.counterparty || transaction.description || null
}
