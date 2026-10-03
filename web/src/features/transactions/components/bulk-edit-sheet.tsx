import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { XIcon } from "lucide-react"

import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Sheet, SheetClose, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { categoriesQueryOptions } from "@/features/categories/api"
import { CategorySelect } from "@/features/categories/components/category-select"
import { ALL_CATEGORY_TYPES, groupAssignableCategories, NO_CATEGORY } from "@/features/categories/grouping"
import { walletsQueryOptions } from "@/features/wallets/api"
import { WalletsSummary } from "@/features/wallets/components/wallets-summary"
import { todayInputValue } from "@/lib/dates"
import { pluralize } from "@/lib/text"
import type { Transaction } from "../api"

const NO_CHANGE = { label: "No change", selectable: true }

/** The fields of a bulk edit. Empty means "leave as it is". Applying them comes with the save step. */
function BulkEditFields({ transactions }: { transactions: Transaction[] }) {
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const [categoryId, setCategoryId] = useState(NO_CATEGORY)
  const [date, setDate] = useState("")
  const [notes, setNotes] = useState("")
  // The bank sets the date of its transactions
  const hasBankTransactions = transactions.some((transaction) => transaction.is_imported)

  return (
    <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
      <FormField id="bulk-category" label="Category">
        <CategorySelect
          id="bulk-category"
          className="h-10"
          emptyOption={NO_CHANGE}
          value={categoryId}
          onChange={(event) => setCategoryId(event.target.value)}
          groups={groupAssignableCategories(categories, ALL_CATEGORY_TYPES)}
        />
      </FormField>

      <FormField id="bulk-date" label="Date">
        <Input
          id="bulk-date"
          type="date"
          className="h-10"
          max={todayInputValue()}
          value={date}
          onChange={(event) => setDate(event.target.value)}
          disabled={hasBankTransactions}
          aria-describedby={hasBankTransactions ? "bulk-date-hint" : undefined}
        />
        {hasBankTransactions && (
          <p id="bulk-date-hint" className="text-sm text-muted-foreground">
            Bank transactions keep the date the bank gave them.
          </p>
        )}
      </FormField>

      <FormField id="bulk-notes" label="Notes">
        <Input
          id="bulk-notes"
          className="h-10"
          placeholder="No change"
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
        />
      </FormField>
    </div>
  )
}

type BulkEditSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  transactions: Transaction[]
}

/** "Edit N transactions": a panel from the right with the fields to change on all of them. */
export function BulkEditSheet({ open, onOpenChange, transactions }: BulkEditSheetProps) {
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
        {open && <BulkEditFields transactions={transactions} />}
      </SheetContent>
    </Sheet>
  )
}
