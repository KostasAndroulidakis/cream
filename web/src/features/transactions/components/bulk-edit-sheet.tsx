import { useState, type FormEvent } from "react"
import { useQuery } from "@tanstack/react-query"
import { Info, XIcon } from "lucide-react"

import { ConfirmChangesDialog } from "@/components/confirm-changes-dialog"
import { FormField } from "@/components/form-field"
import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Sheet, SheetClose, SheetContent, SheetFooter, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { categoriesQueryOptions } from "@/features/categories/api"
import { CategorySelect } from "@/features/categories/components/category-select"
import { ALL_CATEGORY_TYPES, categoriesById, groupAssignableCategories } from "@/features/categories/grouping"
import { walletsQueryOptions } from "@/features/wallets/api"
import { WalletsSummary } from "@/features/wallets/components/wallets-summary"
import { userMessage } from "@/lib/api/errors"
import { notifySuccess } from "@/lib/notify"
import { todayInputValue } from "@/lib/dates"
import { pluralize } from "@/lib/text"
import { useBulkUpdateTransactions, type Transaction } from "../api"
import {
  BULK_FIELD_LABELS,
  bulkUpdateNotice,
  draftToChanges,
  EMPTY_DRAFT,
  hasChanges,
  NO_CHANGE,
  summarizeChanges,
  VISIBILITY_CHOICES,
  type BulkEditDraft,
} from "../bulk-edit"
import { HIDE_EXPLANATION } from "../hiding"

const NO_CHANGE_LABEL = "No change"
const FIELD_HEIGHT = "h-10"

type BulkEditFormProps = {
  transactions: Transaction[]
  onCancel: () => void
  onSaved: () => void
}

/** The fields of a bulk edit and its Cancel / Save. Untouched fields mean "no change". */
function BulkEditForm({ transactions, onCancel, onSaved }: BulkEditFormProps) {
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const bulkUpdate = useBulkUpdateTransactions()
  const [draft, setDraft] = useState<BulkEditDraft>(EMPTY_DRAFT)
  const [isConfirming, setIsConfirming] = useState(false)
  const changes = draftToChanges(draft)
  const count = transactions.length
  // The bank sets the date of its transactions
  const hasBankTransactions = transactions.some((transaction) => transaction.is_imported)

  function setField<K extends keyof BulkEditDraft>(field: K, value: BulkEditDraft[K]) {
    setDraft((current) => ({ ...current, [field]: value }))
  }

  // Save asks first; only "Apply" changes anything
  function onSubmit(event: FormEvent) {
    event.preventDefault()
    bulkUpdate.reset()
    setIsConfirming(true)
  }

  function apply() {
    bulkUpdate.mutate(
      { transactionIds: transactions.map((transaction) => transaction.id), changes },
      {
        onSuccess: ({ affected }) => {
          setIsConfirming(false)
          onSaved()
          const { title, description } = bulkUpdateNotice(affected)
          notifySuccess(title, description)
        },
      },
    )
  }

  return (
    <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
        <FormField id="bulk-category" label={BULK_FIELD_LABELS.category}>
          <CategorySelect
            id="bulk-category"
            className={FIELD_HEIGHT}
            emptyOption={{ label: NO_CHANGE_LABEL, selectable: true }}
            value={draft.categoryId}
            onChange={(event) => setField("categoryId", event.target.value)}
            groups={groupAssignableCategories(categories, ALL_CATEGORY_TYPES)}
          />
        </FormField>

        <FormField id="bulk-date" label={BULK_FIELD_LABELS.date}>
          <Input
            id="bulk-date"
            type="date"
            className={FIELD_HEIGHT}
            max={todayInputValue()}
            value={draft.date}
            onChange={(event) => setField("date", event.target.value)}
            disabled={hasBankTransactions}
            aria-describedby={hasBankTransactions ? "bulk-date-hint" : undefined}
          />
          {hasBankTransactions && (
            <p id="bulk-date-hint" className="text-sm text-muted-foreground">
              Bank transactions keep the date the bank gave them.
            </p>
          )}
        </FormField>

        <FormField id="bulk-notes" label={BULK_FIELD_LABELS.notes}>
          <Input
            id="bulk-notes"
            className={FIELD_HEIGHT}
            placeholder={NO_CHANGE_LABEL}
            value={draft.notes}
            onChange={(event) => setField("notes", event.target.value)}
          />
        </FormField>

        <FormField
          id="bulk-visibility"
          label={
            <span className="inline-flex items-center gap-1.5">
              {BULK_FIELD_LABELS.visibility}
              <Info className="size-3.5 text-muted-foreground" aria-label={HIDE_EXPLANATION}>
                <title>{HIDE_EXPLANATION}</title>
              </Info>
            </span>
          }
        >
          <NativeSelect
            id="bulk-visibility"
            className={FIELD_HEIGHT}
            value={draft.visibility}
            // The options below are exactly the draft's allowed values
            onChange={(event) => setField("visibility", event.target.value as BulkEditDraft["visibility"])}
          >
            <option value={NO_CHANGE}>{NO_CHANGE_LABEL}</option>
            {Object.entries(VISIBILITY_CHOICES).map(([choice, { label }]) => (
              <option key={choice} value={choice}>
                {label}
              </option>
            ))}
          </NativeSelect>
        </FormField>
      </div>

      <SheetFooter className="mt-0 flex-row justify-end gap-2 border-t px-6 py-4">
        <Button type="button" variant="outline" size="lg" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" size="lg" disabled={!hasChanges(changes)}>
          Save
        </Button>
      </SheetFooter>

      <ConfirmChangesDialog
        open={isConfirming}
        onOpenChange={setIsConfirming}
        title="Does this look right?"
        description={
          <>
            Confirm this looks right to you, you will be applying the following changes to{" "}
            <strong>{pluralize(count, "transaction")}</strong>.
          </>
        }
        rows={summarizeChanges(changes, (id) => categoriesById(categories).get(id)?.name ?? "")}
        confirmLabel={count === 1 ? "Apply" : `Apply to all ${count}`}
        isPending={bulkUpdate.isPending}
        errorMessage={bulkUpdate.isError ? userMessage(bulkUpdate.error) : undefined}
        onConfirm={apply}
      />
    </form>
  )
}

type BulkEditSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  transactions: Transaction[]
  onSaved: () => void
}

/** "Edit N transactions": a panel from the right with the fields to change on all of them. */
export function BulkEditSheet({ open, onOpenChange, transactions, onSaved }: BulkEditSheetProps) {
  const { data: wallets = [] } = useQuery(walletsQueryOptions)
  const selectedWallets = wallets.filter((wallet) => transactions.some((t) => t.wallet_id === wallet.id))

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" showCloseButton={false} className="w-full gap-0 sm:max-w-md">
        <SheetHeader className="flex-row items-center justify-between gap-4 px-6 py-5">
          <SheetTitle className="text-2xl font-semibold tracking-tight">
            Edit {pluralize(transactions.length, "transaction")}
          </SheetTitle>
          <SheetClose render={<Button variant="ghost" size="icon" aria-label="Close" />}>
            <XIcon className="size-5" aria-hidden />
          </SheetClose>
        </SheetHeader>
        <WalletsSummary wallets={selectedWallets} />
        {/* Mounted only while open, so every edit starts from "No change" */}
        {open && <BulkEditForm transactions={transactions} onCancel={() => onOpenChange(false)} onSaved={onSaved} />}
      </SheetContent>
    </Sheet>
  )
}
