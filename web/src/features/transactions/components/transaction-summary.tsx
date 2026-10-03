import type { ReactNode } from "react"

import { Amount } from "@/components/amount"
import { formatShortDate } from "@/lib/dates"
import type { Transaction } from "../api"

type TransactionSummaryProps = {
  transaction: Transaction
  title: string
  subtitle: ReactNode
  // Unknown only for the moment before wallets finish loading
  currency?: string
  // Optional control at the end of the row, e.g. a hide button
  action?: ReactNode
}

/** Date, who and how much: the shared look of a transaction in any list. */
export function TransactionSummary({ transaction, title, subtitle, currency, action }: TransactionSummaryProps) {
  return (
    <div className="flex items-center gap-4">
      <time dateTime={transaction.occurred_at} className="w-12 shrink-0 text-sm tabular-nums text-muted-foreground">
        {formatShortDate(transaction.occurred_at)}
      </time>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{title}</p>
        <div className="truncate text-sm text-muted-foreground">{subtitle}</div>
      </div>
      <Amount value={transaction.amount} currency={currency} className="font-medium" />
      {action}
    </div>
  )
}
