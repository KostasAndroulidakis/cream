import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { categoriesQueryOptions } from "@/features/categories/api"
import { categoriesById } from "@/features/categories/grouping"
import { ChangeCategoryDialog } from "@/features/categorization/components/change-category-dialog"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { recentTransactionsQueryOptions } from "../api"
import { transactionLabel } from "../display"
import { TransactionSummary } from "./transaction-summary"

const RECENT_LIMIT = 10
const SKELETON_ROWS = 4

export function RecentTransactions() {
  const transactionsQuery = useQuery(recentTransactionsQueryOptions(RECENT_LIMIT))
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)

  if (transactionsQuery.isPending) {
    return <ListSkeleton rows={SKELETON_ROWS} label="Loading transactions" rowClassName="h-16" />
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

  const categoryById = categoriesById(categories)
  const walletsById = new Map(wallets.map((wallet) => [wallet.id, wallet]))

  return (
    <ul className="divide-y">
      {transactions.map((transaction) => {
        const wallet = walletsById.get(transaction.wallet_id)
        const categoryName = categoryById.get(transaction.category_id)?.name ?? ""
        return (
          <li key={transaction.id} className="py-3">
            <TransactionSummary
              transaction={transaction}
              title={transactionLabel(transaction) ?? categoryName}
              currency={wallet?.currency}
              subtitle={
                <>
                  <ChangeCategoryDialog transaction={transaction} categoryName={categoryName} />
                  {wallet && `, ${wallet.name}`}
                </>
              }
            />
          </li>
        )
      })}
    </ul>
  )
}
