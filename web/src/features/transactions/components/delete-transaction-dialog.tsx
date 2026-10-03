import { useState } from "react"
import { Trash2 } from "lucide-react"

import { ConfirmDialog } from "@/components/confirm-dialog"
import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { formatMoney } from "@/lib/money"
import { cn } from "@/lib/utils"
import { useDeleteTransaction, type Transaction } from "../api"
import { transactionLabel } from "../display"
import { REVEAL_ON_ROW_HOVER } from "../row-actions"

type DeleteTransactionDialogProps = {
  transaction: Transaction
  // Unknown only for the moment before wallets finish loading
  currency?: string
}

/** A delete button that asks for confirmation first: deleting changes the balance and can't be undone. */
export function DeleteTransactionDialog({ transaction, currency }: DeleteTransactionDialogProps) {
  const [open, setOpen] = useState(false)
  const deleteTransaction = useDeleteTransaction()
  const label = transactionLabel(transaction) ?? "This transaction"
  const amount = currency ? formatMoney(transaction.amount, currency) : transaction.amount

  return (
    <>
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={`Delete ${label}`}
        title="Delete"
        className={cn("text-muted-foreground hover:text-destructive", REVEAL_ON_ROW_HOVER)}
        onClick={() => {
          deleteTransaction.reset()
          setOpen(true)
        }}
      >
        <Trash2 aria-hidden />
      </Button>
      <ConfirmDialog
        open={open}
        onOpenChange={setOpen}
        title="Delete this transaction?"
        description={`${label}, ${amount}. The wallet balance changes, and this can't be undone.`}
        confirmLabel="Delete"
        confirmVariant="destructive"
        isPending={deleteTransaction.isPending}
        errorMessage={deleteTransaction.isError ? userMessage(deleteTransaction.error) : undefined}
        onConfirm={() => deleteTransaction.mutate(transaction.id, { onSuccess: () => setOpen(false) })}
      />
    </>
  )
}
