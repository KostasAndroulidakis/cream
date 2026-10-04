import type { Transaction } from "./api"

/** How buttons and messages refer to a transaction without a label. */
export const UNNAMED_TRANSACTION = "this transaction"

/**
 * Who the money went to or came from: the merchant (the user's name for it), else the bank's text, else the
 * note; a transfer side with none of these is shown by the account on the other side.
 */
export function transactionLabel(transaction: Transaction): string | null {
  return (
    transaction.merchant?.name ||
    transaction.counterparty ||
    transaction.description ||
    transaction.transfer_account_name ||
    null
  )
}
