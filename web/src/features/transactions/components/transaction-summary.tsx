import type { ReactNode } from "react"

import { isMoneyIn } from "@/lib/amount"
import { formatShortDate } from "@/lib/dates"
import { formatMoney } from "@/lib/money"
import { cn } from "@/lib/utils"
import type { Transaction } from "../api"

type TransactionSummaryProps = {
  transaction: Transaction
  title: string
  subtitle: ReactNode
  // Unknown only for the moment before wallets finish loading
  currency?: string
}

/** Date, who and how much: the shared look of a transaction in any list. */
export function TransactionSummary({ transaction, title, subtitle, currency }: TransactionSummaryProps) {
  const moneyIn = isMoneyIn(transaction.amount)

  return (
    <div className="flex items-center gap-4">
      <time dateTime={transaction.occurred_at} className="w-12 shrink-0 text-sm tabular-nums text-muted-foreground">
        {formatShortDate(transaction.occurred_at)}
      </time>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{title}</p>
        <div className="truncate text-sm text-muted-foreground">{subtitle}</div>
      </div>
      <p className={cn("font-medium tabular-nums", moneyIn && "text-primary")}>
        {moneyIn && "+"}
        {currency ? formatMoney(transaction.amount, currency) : transaction.amount}
      </p>
    </div>
  )
}
