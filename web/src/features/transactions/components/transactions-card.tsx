import { useMemo, useState, type ReactNode } from "react"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"

import { Amount, AmountTotals } from "@/components/amount"
import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { SelectionCheckbox } from "@/components/selection-checkbox"
import { Button } from "@/components/ui/button"
import { AccountLogo } from "@/features/bank/components/account-logo"
import { categoriesQueryOptions, type Category } from "@/features/categories/api"
import { CategoryIcon } from "@/features/categories/components/category-icon"
import { MerchantAvatar } from "@/features/merchants/components/merchant-avatar"
import { categoriesById } from "@/features/categories/grouping"
import { walletsQueryOptions, type Wallet } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { formatLongDate } from "@/lib/dates"
import { cn } from "@/lib/utils"
import type { Transaction } from "../api"
import type { CurrencyTotal } from "@/lib/currency-totals"
import { groupByDay } from "../day-groups"
import { transactionLabel } from "../display"
import { useSelection, useSelectionShortcuts, type Selection } from "../use-selection"
import { useTransactionView } from "../use-transaction-view"
import { TRANSACTION_VIEWS } from "../views"
import { BulkEditSheet } from "./bulk-edit-sheet"
import { MarkReviewedButton } from "./mark-reviewed-button"
import { TransactionsToolbar } from "./transactions-toolbar"

const SKELETON_ROWS = 8
// Merchant, category, account, row actions, amount. The actions and amount columns have fixed widths,
// so every row (each its own grid) gets the same column positions.
const ROW_GRID =
  "grid grid-cols-[minmax(0,1fr)_2rem_auto] items-center gap-x-4 md:grid-cols-[minmax(0,5fr)_minmax(0,4fr)_minmax(0,4fr)_2rem_8rem] md:gap-x-6"

type RowProps = {
  transaction: Transaction
  category?: Category
  wallet?: Wallet
  // Set while selecting: the row becomes a checkbox
  selection?: { selected: boolean; onToggle: () => void }
}

// One column's icon and text, the text cut short when it doesn't fit
function IconCell({ icon, text, className }: { icon: ReactNode; text: string; className?: string }) {
  return (
    <div className={cn("min-w-0 items-center gap-2.5", className)}>
      {icon}
      <span className="truncate">{text}</span>
    </div>
  )
}

function TransactionRow({ transaction, category, wallet, selection }: RowProps) {
  const categoryName = category?.name ?? ""
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
      <IconCell
        icon={<CategoryIcon icon={category?.icon ?? null} />}
        text={categoryName}
        className="hidden md:flex"
      />
      <IconCell
        icon={wallet && <AccountLogo wallet={wallet} className="size-6" />}
        text={wallet?.name ?? ""}
        className="hidden md:flex"
      />
      {/* Not while selecting: a click there toggles the row's checkbox */}
      <div>{!selection && transaction.needs_review && <MarkReviewedButton transaction={transaction} />}</div>
      <p className="text-right">
        <Amount value={transaction.amount} currency={wallet?.currency} />
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
        <div className={cn(rowClass, "group/row")}>{cells}</div>
      )}
    </li>
  )
}

function DayHeader({ day, totals }: { day: string; totals: CurrencyTotal[] }) {
  return (
    <div className="flex items-center justify-between gap-4 bg-sidebar px-6 py-2 text-sm font-medium text-muted-foreground">
      <h3>{formatLongDate(day)}</h3>
      <AmountTotals totals={totals} />
    </div>
  )
}

type DayGroupsProps = {
  transactions: Transaction[]
  selection: Selection
}

/** The transactions under a header per day, each row a checkbox while selecting. */
function DayGroups({ transactions, selection }: DayGroupsProps) {
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)
  const categoryById = categoriesById(categories)
  const walletsById = new Map(wallets.map((wallet) => [wallet.id, wallet]))
  const groups = groupByDay(transactions, (walletId) => walletsById.get(walletId)?.currency)

  return groups.map(({ day, transactions: dayTransactions, totals }) => (
    <section key={day} aria-label={formatLongDate(day)}>
      <DayHeader day={day} totals={totals} />
      <ul className="divide-y">
        {dayTransactions.map((transaction) => {
          const wallet = walletsById.get(transaction.wallet_id)
          return (
            <TransactionRow
              key={transaction.id}
              transaction={transaction}
              category={categoryById.get(transaction.category_id)}
              wallet={wallet}
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
  ))
}

/** The chosen view's transactions, newest first, grouped by day, with the view and its actions on top. */
export function TransactionsCard() {
  const [view, setView] = useTransactionView()
  const { query, emptyMessage, countsForReview } = TRANSACTION_VIEWS[view]
  const transactionsQuery = useInfiniteQuery(query)
  const selection = useSelection()
  const [isEditing, setIsEditing] = useState(false)

  const pages = transactionsQuery.data?.pages
  const transactions = useMemo(() => pages?.flatMap((page) => page.items) ?? [], [pages])
  const allIds = useMemo(() => transactions.map((transaction) => transaction.id), [transactions])
  useSelectionShortcuts(selection, allIds, !isEditing)

  function body() {
    if (transactionsQuery.isPending) {
      return <ListSkeleton rows={SKELETON_ROWS} label="Loading transactions" rowClassName="h-14 px-6" />
    }
    if (transactionsQuery.isError) return <FormAlert message={userMessage(transactionsQuery.error)} />
    if (transactions.length === 0) {
      return <p className="px-6 py-10 text-center text-sm text-muted-foreground">{emptyMessage}</p>
    }
    return <DayGroups transactions={transactions} selection={selection} />
  }

  return (
    <div>
      <TransactionsToolbar
        selection={selection}
        allIds={allIds}
        onEdit={() => setIsEditing(true)}
        view={view}
        onViewChange={setView}
        reviewCount={countsForReview ? pages?.[0]?.total : undefined}
      />
      <BulkEditSheet
        open={isEditing}
        onOpenChange={setIsEditing}
        transactions={transactions.filter((transaction) => selection.selectedIds.has(transaction.id))}
        onDone={() => {
          // Back to the plain list, like after a save in Monarch
          setIsEditing(false)
          selection.cancel()
        }}
      />
      {body()}
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
