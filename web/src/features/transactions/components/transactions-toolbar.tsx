import { Check } from "lucide-react"

import { SelectionCheckbox } from "@/components/selection-checkbox"
import { Button } from "@/components/ui/button"
import { MOD_KEY_PREFIX } from "@/lib/keyboard"
import { pluralize } from "@/lib/text"
import type { Selection } from "../use-selection"

type TransactionsToolbarProps = {
  selection: Selection
  // Every transaction loaded on the page, for "select all"
  allIds: readonly number[]
  onEdit: () => void
}

/** The bar on top of the transactions card: "Edit multiple", or the selection controls while selecting. */
export function TransactionsToolbar({ selection, allIds, onEdit }: TransactionsToolbarProps) {
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
            {count > 0 ? `${pluralize(count, "transaction")} selected` : "All transactions"}
          </span>
          <span className="text-sm text-muted-foreground">({count > 0 ? "ESC" : `${MOD_KEY_PREFIX}A`})</span>
        </label>
      ) : (
        <h2 className="text-base font-semibold">All transactions</h2>
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
          <Button variant="outline" size="lg" onClick={selection.start}>
            <Check aria-hidden />
            Edit multiple
          </Button>
        )}
      </div>
    </div>
  )
}
