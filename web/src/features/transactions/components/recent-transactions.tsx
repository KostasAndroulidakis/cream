import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { categoriesQueryOptions } from "@/features/categories/api"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { formatShortDate } from "@/lib/dates"
import { formatMoney } from "@/lib/money"
import { cn } from "@/lib/utils"
import { recentTransactionsQueryOptions, type Transaction } from "../api"

const RECENT_LIMIT = 10
const SKELETON_ROWS = 4

type RowProps = {
  transaction: Transaction
  categoryName: string
  walletName: string
  // Unknown only for the moment before wallets finish loading
  currency?: string
}

function TransactionRow({ transaction, categoryName, walletName, currency }: RowProps) {
  const isIncome = !transaction.amount.startsWith("-")
  // Bank imports carry the merchant; manual entries carry the user's note
  const title = transaction.counterparty || transaction.description || categoryName

  return (
    <li className="flex items-center gap-4 py-3">
      <time
        dateTime={transaction.occurred_at}
        className="w-12 shrink-0 text-sm tabular-nums text-muted-foreground"
      >
        {formatShortDate(transaction.occurred_at)}
      </time>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{title}</p>
        <p className="truncate text-sm text-muted-foreground">
          {title === categoryName ? walletName : `${categoryName}, ${walletName}`}
        </p>
      </div>
      <p className={cn("font-medium tabular-nums", isIncome && "text-primary")}>
        {isIncome && "+"}
        {currency ? formatMoney(transaction.amount, currency) : transaction.amount}
      </p>
    </li>
  )
}

export function RecentTransactions() {
  const transactionsQuery = useQuery(recentTransactionsQueryOptions(RECENT_LIMIT))
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)

  if (transactionsQuery.isPending) {
    return (
      <ul className="divide-y" aria-label="Loading transactions">
        {Array.from({ length: SKELETON_ROWS }, (_, i) => (
          <li key={i} className="h-16 animate-pulse py-3">
            <div className="h-full rounded-lg bg-muted" />
          </li>
        ))}
      </ul>
    )
  }
  if (transactionsQuery.isError) return <FormAlert message={userMessage(transactionsQuery.error)} />

  const transactions = transactionsQuery.data
  if (transactions.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        Nothing recorded yet. Add your first expense or income to see it here.
      </p>
    )
  }

  const categoryNames = new Map(categories.map((category) => [category.id, category.name]))
  const walletsById = new Map(wallets.map((wallet) => [wallet.id, wallet]))

  return (
    <ul className="divide-y">
      {transactions.map((transaction) => {
        const wallet = walletsById.get(transaction.wallet_id)
        return (
          <TransactionRow
            key={transaction.id}
            transaction={transaction}
            categoryName={categoryNames.get(transaction.category_id) ?? ""}
            walletName={wallet?.name ?? ""}
            currency={wallet?.currency}
          />
        )
      })}
    </ul>
  )
}
