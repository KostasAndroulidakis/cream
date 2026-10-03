import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { CheckCircle2 } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { TransactionSummary } from "@/features/transactions/components/transaction-summary"
import { TransactionActions } from "@/features/transactions/components/transaction-actions"
import { transactionLabel } from "@/features/transactions/display"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { inboxQueryOptions } from "../api"
import { CategorizeForm } from "./categorize-form"

const SKELETON_ROWS = 4
const UNKNOWN_MERCHANT = "Unknown merchant"

/** Imported transactions CREAM couldn't place on its own, each with a quick category picker. */
export function ReviewInbox() {
  const inbox = useQuery(inboxQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)
  const [lastResult, setLastResult] = useState<string | null>(null)

  const status = (
    // Always mounted so screen readers announce changes; takes no space while empty
    <p role="status" className={cn("text-sm text-primary", !lastResult && "sr-only")}>
      {lastResult}
    </p>
  )

  if (inbox.isPending) return <ListSkeleton rows={SKELETON_ROWS} label="Loading transactions to review" rowClassName="h-28" />
  if (inbox.isError) return <FormAlert message={userMessage(inbox.error)} />

  const { total, items } = inbox.data
  if (total === 0) {
    return (
      <div className="space-y-2">
        {status}
        <div className="rounded-xl border border-dashed px-6 py-10 text-center">
          <CheckCircle2 className="mx-auto size-8 text-primary" aria-hidden />
          <p className="mt-3 font-medium">All caught up</p>
          <p className="mx-auto mt-1 max-w-xs text-sm text-muted-foreground">
            Imports that CREAM can't categorize on its own will wait for you here.
          </p>
        </div>
      </div>
    )
  }

  const walletsById = new Map(wallets.map((wallet) => [wallet.id, wallet]))

  return (
    <div className="space-y-2">
      {status}
      <ul className="divide-y">
        {items.map((transaction) => {
          const wallet = walletsById.get(transaction.wallet_id)
          return (
            <li key={transaction.id} className="group/row space-y-3 py-4">
              <TransactionSummary
                transaction={transaction}
                title={transactionLabel(transaction) ?? UNKNOWN_MERCHANT}
                subtitle={wallet?.name}
                currency={wallet?.currency}
                action={<TransactionActions transaction={transaction} currency={wallet?.currency} />}
              />
              <CategorizeForm transaction={transaction} layout="inline" onCategorized={setLastResult} />
            </li>
          )
        })}
      </ul>
      {total > items.length && (
        <p className="pt-2 text-sm text-muted-foreground">
          Showing the newest {items.length} of {total}. The rest appear as you go.
        </p>
      )}
    </div>
  )
}
