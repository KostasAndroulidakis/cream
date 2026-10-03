import type { Transaction } from "../api"
import { DeleteTransactionDialog } from "./delete-transaction-dialog"
import { VisibilityButton } from "./visibility-button"

type TransactionActionsProps = {
  transaction: Transaction
  currency?: string
}

/** The buttons at the end of a transaction row. Bank transactions can only be hidden, never deleted. */
export function TransactionActions({ transaction, currency }: TransactionActionsProps) {
  return (
    <div className="flex items-center">
      {!transaction.is_imported && <DeleteTransactionDialog transaction={transaction} currency={currency} />}
      <VisibilityButton transaction={transaction} />
    </div>
  )
}
