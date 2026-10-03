import { useMemo, useState } from "react"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { SelectionCheckbox } from "@/components/selection-checkbox"
import { Button } from "@/components/ui/button"
import { categoriesQueryOptions } from "@/features/categories/api"
import { categoriesById } from "@/features/categories/grouping"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { isMoneyIn } from "@/lib/amount"
import { formatLongDate } from "@/lib/dates"
import { formatFlow } from "@/lib/money"
import { cn } from "@/lib/utils"
import { allTransactionsQueryOptions, type Transaction } from "../api"
import { groupByDay, type CurrencyTotal } from "../day-groups"
import { transactionLabel } from "../display"
import { useSelection, useSelectionShortcuts } from "../use-selection"
import { BulkEditSheet } from "./bulk-edit-sheet"
import { MerchantAvatar } from "./merchant-avatar"
import { TransactionsToolbar } from "./transactions-toolbar"

const SKELETON_ROWS = 8
// Merchant, category, account, amount. The amount column has a fixed width, so every row
// (each its own grid) gets the same column positions.
const ROW_GRID =
  "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-6 md:grid-cols-[minmax(0,5fr)_minmax(0,4fr)_minmax(0,4fr)_8rem]"

type RowProps = {
  transaction: Transaction
  categoryName: string
  walletName: string
  currency?: string
  // Set while selecting: the row becomes a checkbox
  selection?: { selected: boolean; onToggle: () => void }
}

function TransactionRow({ transaction, categoryName, walletName, currency, selection }: RowProps) {
  const merchant = transactionLabel(transaction) ?? categoryName
  const cells = (
    <>
      <div className="flex min-w-0 items-center gap-3">
        {selection && (
          <SelectionCheckbox
            aria-label={`Select ${merchant}`}
            checked={selection.selected}
            onChange={selection.onToggle}
          />
        )}
        <MerchantAvatar name={merchant} />
        <div className="min-w-0">
          <p className="truncate">{merchant}</p>
          {/* Phones have no room for the category and account columns */}
          <p className="truncate text-sm text-muted-foreground md:hidden">{categoryName}</p>
        </div>
      </div>
      <p className="hidden truncate md:block">{categoryName}</p>
      <p className="hidden truncate md:block">{walletName}</p>
      <p className={cn("text-right tabular-nums", isMoneyIn(transaction.amount) && "text-primary")}>
        {currency ? formatFlow(transaction.amount, currency) : transaction.amount}
      </p>
    </>
  )
  const rowClass = cn(ROW_GRID, "px-6 py-3 text-[0.9375rem]")

  return (
    <li>
      {/* While selecting, a click anywhere on the row toggles its checkbox */}
      {selection ? (
        <label className={cn(rowClass, "cursor-pointer hover:bg-sidebar/60")}>{cells}</label>
      ) : (
        <div className={rowClass}>{cells}</div>
      )}
    </li>
  )
}

function DayHeader({ day, totals }: { day: string; totals: CurrencyTotal[] }) {
  return (
    <div className="flex items-center justify-between gap-4 bg-sidebar px-6 py-2 text-sm font-medium text-muted-foreground">
      <h3>{formatLongDate(day)}</h3>
      <p className="tabular-nums">{totals.map((total) => formatFlow(total.amount, total.currency)).join(" · ")}</p>
    </div>
  )
}

/** Every visible transaction, newest first, grouped by day, with "Edit multiple" selection on top. */
export function TransactionsCard() {
  const transactionsQuery = useInfiniteQuery(allTransactionsQueryOptions)
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)
  const selection = useSelection()
  const [isEditing, setIsEditing] = useState(false)

  const pages = transactionsQuery.data?.pages
  const transactions = useMemo(() => pages?.flat() ?? [], [pages])
  const allIds = useMemo(() => transactions.map((transaction) => transaction.id), [transactions])
  useSelectionShortcuts(selection, allIds, !isEditing)

  if (transactionsQuery.isPending) {
    return <ListSkeleton rows={SKELETON_ROWS} label="Loading transactions" rowClassName="h-14 px-6" />
  }
  if (transactionsQuery.isError) return <FormAlert message={userMessage(transactionsQuery.error)} />
  if (transactions.length === 0) {
    return <p className="px-6 py-10 text-center text-sm text-muted-foreground">No transactions yet.</p>
  }

  const categoryById = categoriesById(categories)
  const walletsById = new Map(wallets.map((wallet) => [wallet.id, wallet]))
  const groups = groupByDay(transactions, (walletId) => walletsById.get(walletId)?.currency)

  return (
    <div>
      <TransactionsToolbar selection={selection} allIds={allIds} onEdit={() => setIsEditing(true)} />
      <BulkEditSheet
        open={isEditing}
        onOpenChange={setIsEditing}
        transactions={transactions.filter((transaction) => selection.selectedIds.has(transaction.id))}
      />
      {groups.map(({ day, transactions: dayTransactions, totals }) => (
        <section key={day} aria-label={formatLongDate(day)}>
          <DayHeader day={day} totals={totals} />
          <ul className="divide-y">
            {dayTransactions.map((transaction) => {
              const wallet = walletsById.get(transaction.wallet_id)
              return (
                <TransactionRow
                  key={transaction.id}
                  transaction={transaction}
                  categoryName={categoryById.get(transaction.category_id)?.name ?? ""}
                  walletName={wallet?.name ?? ""}
                  currency={wallet?.currency}
                  selection={
                    selection.isSelecting
                      ? {
                          selected: selection.selectedIds.has(transaction.id),
                          onToggle: () => selection.toggle(transaction.id),
                        }
                      : undefined
                  }
                />
              )
            })}
          </ul>
        </section>
      ))}
      {transactionsQuery.hasNextPage && (
        <div className="border-t px-6 py-4 text-center">
          <Button
            variant="outline"
            onClick={() => transactionsQuery.fetchNextPage()}
            disabled={transactionsQuery.isFetchingNextPage}
          >
            {transactionsQuery.isFetchingNextPage ? "Loading…" : "Load more"}
          </Button>
        </div>
      )}
    </div>
  )
}
