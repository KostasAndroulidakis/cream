import { useState } from "react"
import { Trash2 } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
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
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={`Delete ${label}`}
            title="Delete"
            className={cn("text-muted-foreground hover:text-destructive", REVEAL_ON_ROW_HOVER)}
          />
        }
      >
        <Trash2 aria-hidden />
      </DialogTrigger>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Delete this transaction?</DialogTitle>
          <DialogDescription>
            {label}, {amount}. The wallet balance changes, and this can't be undone.
          </DialogDescription>
        </DialogHeader>
        {deleteTransaction.isError && <FormAlert message={userMessage(deleteTransaction.error)} />}
        <DialogFooter>
          <DialogClose render={<Button variant="outline" />}>Cancel</DialogClose>
          <Button
            variant="destructive"
            disabled={deleteTransaction.isPending}
            onClick={() => deleteTransaction.mutate(transaction.id, { onSuccess: () => setOpen(false) })}
          >
            {deleteTransaction.isPending ? "Deleting…" : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
