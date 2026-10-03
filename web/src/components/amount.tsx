import { Fragment } from "react"

import type { CurrencyTotal } from "@/lib/currency-totals"
import { amountTone, formatSigned } from "@/lib/money"
import { cn } from "@/lib/utils"

type AmountProps = {
  // Exact decimal string from the API, e.g. "-46.3000"
  value: string
  // Unknown only for the moment before accounts finish loading: the raw value shows meanwhile
  currency?: string
  className?: string
}

/** An amount as CREAM shows every amount: signed, green when positive, red when negative. */
export function Amount({ value, currency, className }: AmountProps) {
  return (
    <span className={cn("tabular-nums", amountTone(value), className)}>
      {currency ? formatSigned(value, currency) : value}
    </span>
  )
}

/** Totals side by side, one per currency (never added together): "+€1,200.00 · -$35.00". */
export function AmountTotals({ totals, className }: { totals: readonly CurrencyTotal[]; className?: string }) {
  return (
    <span className={className}>
      {totals.map((total, index) => (
        <Fragment key={total.currency}>
          {index > 0 && " · "}
          <Amount value={total.amount} currency={total.currency} />
        </Fragment>
      ))}
    </span>
  )
}
