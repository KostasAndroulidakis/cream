import { useState, type FormEvent } from "react"

import { FormAlert } from "@/components/form-alert"
import { FormDialog } from "@/components/form-dialog"
import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { notifySuccess } from "@/lib/notify"
import { pluralize } from "@/lib/text"
import { useDeleteMerchant, type MerchantSummary } from "../api"
import { MerchantTargetCombobox } from "./merchant-target-combobox"

const TARGET_ID = "merge-target"

type DeleteMerchantFormProps = {
  merchant: MerchantSummary
  onCancel: () => void
  onDeleted: () => void
}

/** Monarch's Delete merchant: its transactions need a new merchant first, and that is the merge. */
function DeleteMerchantForm({ merchant, onCancel, onDeleted }: DeleteMerchantFormProps) {
  const remove = useDeleteMerchant()
  const [target, setTarget] = useState<MerchantSummary | null>(null)
  const hasTransactions = merchant.transaction_count > 0
  const canDelete = (!hasTransactions || target !== null) && !remove.isPending

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!canDelete) return
    remove.mutate(
      { id: merchant.id, moveTo: target?.id },
      {
        onSuccess: () => {
          notifySuccess({ title: target ? `${merchant.name} merged into ${target.name}` : `${merchant.name} deleted` })
          onDeleted()
        },
      },
    )
  }

  return (
    <FormDialog
      open
      onOpenChange={(open) => !open && !remove.isPending && onCancel()}
      title="Delete merchant"
      description={`Delete ${merchant.name}, moving its transactions to another merchant.`}
      onSubmit={onSubmit}
      footer={
        <>
          <Button type="button" variant="outline" className="ml-auto" onClick={onCancel} disabled={remove.isPending}>
            Cancel
          </Button>
          <Button type="submit" variant="destructive" disabled={!canDelete}>
            {remove.isPending ? "Deleting…" : "Delete merchant"}
          </Button>
        </>
      }
    >
      {remove.isError && <FormAlert message={userMessage(remove.error)} />}
      {hasTransactions ? (
        <>
          <p>
            There {merchant.transaction_count === 1 ? "is" : "are"}{" "}
            {pluralize(merchant.transaction_count, "transaction")} still tied to this merchant, select a new merchant to
            update these relations to before deleting.
          </p>
          <FormField id={TARGET_ID} label="Update relations to merchant">
            <MerchantTargetCombobox id={TARGET_ID} excludeId={merchant.id} value={target} onChange={setTarget} />
          </FormField>
        </>
      ) : (
        <p>{merchant.name} has no transactions, so nothing else changes.</p>
      )}
    </FormDialog>
  )
}

type MergeAndDeleteButtonProps = {
  merchant: MerchantSummary
  // Called once the merchant is gone, e.g. to close Edit merchant too
  onDeleted: () => void
}

/** Edit merchant's "Merge & delete": opens Delete merchant on top of it. */
export function MergeAndDeleteButton({ merchant, onDeleted }: MergeAndDeleteButtonProps) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <Button
        type="button"
        variant="outline"
        className="text-destructive hover:text-destructive"
        onClick={() => setOpen(true)}
      >
        Merge & delete
      </Button>
      {/* Mounted only while open: every opening starts with no merchant chosen */}
      {open && <DeleteMerchantForm merchant={merchant} onCancel={() => setOpen(false)} onDeleted={onDeleted} />}
    </>
  )
}
