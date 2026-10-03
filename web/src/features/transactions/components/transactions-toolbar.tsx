import { Check } from "lucide-react"

import { SelectionCheckbox } from "@/components/selection-checkbox"
import { Button } from "@/components/ui/button"
import { MOD_KEY_PREFIX } from "@/lib/keyboard"
import { pluralize } from "@/lib/text"
import type { Selection } from "../use-selection"
import { TRANSACTION_VIEWS, type TransactionView } from "../views"
import { MarkAllReviewedButton } from "./mark-all-reviewed-button"
import { TransactionViewSelect } from "./transaction-view-select"

type TransactionsToolbarProps = {
  selection: Selection
  // Every transaction loaded on the page, for "select all"
  allIds: readonly number[]
  onEdit: () => void
  view: TransactionView
  onViewChange: (view: TransactionView) => void
  // How many need review, when the view counts them; offers "Mark all N as reviewed"
  reviewCount?: number
}

/** The bar on top of the transactions card: the view and its actions, or the selection controls while selecting. */
export function TransactionsToolbar({
  selection,
  allIds,
  onEdit,
  view,
  onViewChange,
  reviewCount,
}: TransactionsToolbarProps) {
  const count = selection.selectedIds.size
  const allSelected = count > 0 && count === allIds.length

  return (
    <div className="flex min-h-16 flex-wrap items-center justify-between gap-3 border-b px-6 py-3">
      {selection.isSelecting ? (
        <label className="flex cursor-pointer items-center gap-3">
          <SelectionCheckbox
            aria-label="Select all transactions"
            checked={allSelected}
            indeterminate={count > 0 && !allSelected}
            onChange={() => (count > 0 ? selection.clear() : selection.selectAll(allIds))}
          />
          <span className="text-base font-semibold">
            {count > 0 ? `${pluralize(count, "transaction")} selected` : TRANSACTION_VIEWS[view].label}
          </span>
          <span className="text-sm text-muted-foreground">({count > 0 ? "ESC" : `${MOD_KEY_PREFIX}A`})</span>
        </label>
      ) : (
        <TransactionViewSelect value={view} onChange={onViewChange} />
      )}

      <div className="flex items-center gap-2">
        {selection.isSelecting ? (
          <>
            <Button variant="outline" size="lg" onClick={selection.cancel}>
              Cancel
            </Button>
            <Button size="lg" disabled={count === 0} onClick={onEdit}>
              Edit {count}
            </Button>
          </>
        ) : (
          <>
            <Button variant="outline" size="lg" onClick={selection.start}>
              <Check aria-hidden />
              Edit multiple
            </Button>
            {reviewCount != null && reviewCount > 0 && <MarkAllReviewedButton count={reviewCount} />}
          </>
        )}
      </div>
    </div>
  )
}
